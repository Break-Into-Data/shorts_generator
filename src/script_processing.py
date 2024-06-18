import os
import logging
from dataclasses import dataclass
from pprint import pprint
from typing import Optional

import black
from dotenv import load_dotenv
import requests

from src.audio_processing import VoiceClip
from src.llms import openai_gpt4 as gpt4
from src.llms import grok_llama3 as llama3


load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ScriptCodeHighlight:
    text: str
    line_number: int
    line_count: int
    voice_clip: Optional[VoiceClip] = None


@dataclass
class Script:
    code: str
    intro_text: str
    highlights: list[ScriptCodeHighlight]
    cta_text: str
    intro_text_voide_clip: Optional[VoiceClip] = None


PROMPT_DESCRIPTION_GENERATION = """I'm creating a youtube video about this topic:
--- Topic:
{}
--- Rules:
Please output the introduction text for this topic.
Assume average or below average knowledge of the topic.
Description should be short - 1 sentence (up to 20 words).
It should be engaging and attention-grabbing.
--- Format examples:
"How to achieve [dream outcome] without [massive obstacle]"
"60 second [topic] masterclass"
"Here's how to [get desired outcome] in [timeframe]"
---
Only output the description, no other text or comments.
"""

PROMPT_CODE_GENERATION = """I'm creating a presentation about this topic:
--- Topic:
{topic}
--- Documentation:
{documentation}
--- 
Please write a code snippet that demonstrates the main concept of this topic.
Code must be short - up to 25 lines.
Don't output anything else, start printing the code immediately.
Make the code as simple as possible, while maintaining the clarity of the point we want to make. 
Don't comment the code in any way. 
Very important: Any line of the code must not exceed 42 characters.
"""

PROMPT_HIGHLIGHTS_GENERATION = """I'm creating a presentation about this topic:
---
{}
---
Description of the topic:
---
{}
---
Code for the slide:
---
{}
---
Please find important code blocks inside this code. 
Describe code blocks that are important for the audience to understand the topic.
Descriptions should be short and relative to the topic.
Don't be very repetitive and don't start all desceriptions in the same way, the text must be interesting and relevant to the topic.

Good examples of description:
"Here we do X, Y, and Z"
"This code block is used to do X"
"This is a code block that is used to do Y"
"In this line we do Z"
"Execution of this line will do X"

Don't do this (bad examples):
"Importing the necessary libraries"
"Calling the function"
"Defines the constants used in the code"
You are talking to the audience.

Format of output:
```csv
start_line_number|end_line_number|description_of_the_block
1|5|"Description of block 1"
23|23|"Description of block 2"
```
"""

def _annote_line_numbers(code: str) -> str:
    lines = code.split("\n")
    annotated_lines = [f"{idx + 1}: {line}" for idx, line in enumerate(lines)]
    return "\n".join(annotated_lines)


def _generate_topic_description(topic: str) -> str:
    logger.info("Generating description for topic: %s", topic)
    prompt = PROMPT_DESCRIPTION_GENERATION.format(topic)

    description = gpt4.invoke(prompt, temperature=1.0)
    print(description)

    return description


def _fetch_documentation(library: str) -> str:
    logger.info("Fetching documentation for library: %s", library)
    url = f"https://pypi.org/pypi/{library}/json"

    response = requests.get(url)
    data = response.json()

    return data["info"]["description"]


def _generate_code(topic: str, description: str, library: str) -> str:
    logger.info(f"Generating code for topic: {topic}")
    documentation = _fetch_documentation(library)
    prompt = PROMPT_CODE_GENERATION.format(topic=topic, documentation=documentation)
    code = llama3.invoke(prompt, temperature=0.3)

    code = code[code.index("```"):]

    code = code.strip().strip("`")
    if code.startswith("python\n"):
        code = code[7:]

    # remove all comments
    code = "\n".join([line for line in code.split("\n") if not line.strip().startswith("#")])

    code = code.strip().strip("`")

    print(code)

    # Format the code
    black_mode = black.Mode(line_length=42)
    try:
        code = black.format_str(code, mode=black_mode)
    except black.NothingChanged:
        pass

    print("Formatted code:")
    print(code)

    return code


def _generate_highlights(topic: str, description: str, code: str) -> list[ScriptCodeHighlight]:
    logger.info("Generating highlights for topic: %s", topic)
    annotated_code = _annote_line_numbers(code)
    prompt = PROMPT_HIGHLIGHTS_GENERATION.format(topic, description, annotated_code)
    output = gpt4.invoke(prompt)

    output = output.strip().strip("`")
    if output.startswith("csv\n"):
        output = output[4:]

    if output.startswith("start_line_number"):
        output = '\n'.join(output.split("\n")[1:])

    csv_lines = output.split("\n")
    data = [line.strip().split("|") for line in csv_lines]

    result = []

    for row in data:
        try:
            start, end, description = row
        except ValueError:
            logger.warning(f"Skipping row: {row}")
            continue
        try:
            result.append(
                ScriptCodeHighlight(
                    text=description.strip('"').strip("'"),
                    line_number=int(start) - 1,
                    line_count=int(end) - int(start) + 1,
                )
            )
        except ValueError:
            logger.warning(f"Can't parse row: {row}")
            continue

    pprint(result)

    return result


def generate_script(topic: str, library: str) -> Script:
    logger.info(f"Generating script for topic: {topic}")
    description = _generate_topic_description(topic)
    code = _generate_code(topic, description, library)

    highlights = _generate_highlights(topic, description, code)

    script = Script(
        code=code,
        intro_text=description,
        intro_text_voide_clip=None,
        highlights=highlights,
        cta_text="",
    )

    return script
