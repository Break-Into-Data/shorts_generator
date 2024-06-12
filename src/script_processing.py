import os
import logging
from dataclasses import dataclass
from pprint import pprint
from typing import Optional

import black
from openai import OpenAI
from dotenv import load_dotenv

from src.audio_processing import VoiceClip


load_dotenv()

logger = logging.getLogger(__name__)


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

"""
import tensorflow as tf

# Simulated data: features and labels
features = tf.random.normal([100, 10])
labels = tf.concat([tf.zeros(80, dtype=tf.int32), tf.ones(20, dtype=tf.int32)], axis=0)

# Model setup
model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, activation='relu', input_shape=(10,)),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Class weights to handle imbalance
class_weights = {0: 1, 1: 4}

# Compile the model
model.compile(optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy'])

# Fit the model
model.fit(features, labels, epochs=10, class_weight=class_weights)
"""


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


PROMPT_DESCRIPTION_GENERATION = """I'm creating a presentation about this topic:
---
{}
---
Please describe what this topic is about (only the most important points).
Description should be short - 2-5 sentences.
"""

PROMPT_CODE_GENERATION = """I'm creating a presentation about this topic:
---
{}
---
Please write a code snippet that demonstrates the main concept of this topic.
Code must be short - up to 25 lines.
Don't output anything else, start printing the code immediately. 
Make the code as simple as possible, while maintaining the clarity of the point we want to make. 
Don't comment the code at all. 
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
Please find important code blocks inside this code. Example output:
```csv
start_line_number|end_line_number|description_of_the_block
1|5|"These lines import all the necessary libraries"
23|23|"This line trains the model"
```
"""

def _annote_line_numbers(code: str) -> str:
    lines = code.split("\n")
    annotated_lines = [f"{idx + 1}: {line}" for idx, line in enumerate(lines)]
    return "\n".join(annotated_lines)


def invoke_llm(prompt: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4-turbo",
    )

    return chat_completion.choices[0].message.content


def _generate_topic_description(topic: str) -> str:
    logger.info(f"Generating description for topic: {topic}")
    prompt = PROMPT_DESCRIPTION_GENERATION.format(topic)

    description = invoke_llm(prompt)
    print(description)

    return description


def _generate_code(topic: str, description: str) -> str:
    logger.info(f"Generating code for topic: {topic}")
    prompt = PROMPT_CODE_GENERATION.format(topic)
    code = invoke_llm(prompt)

    code = code.strip().strip("`")
    if code.startswith("python\n"):
        code = code[7:]

    # remove all comments
    code = "\n".join([line for line in code.split("\n") if not line.strip().startswith("#")])

    # Format the code
    black_mode = black.Mode(line_length=42)
    try:
        code = black.format_str(code, mode=black_mode)
    except black.NothingChanged:
        pass

    print(code)

    return code


def _generate_highlights(topic: str, description: str, code: str) -> list[ScriptCodeHighlight]:
    logger.info(f"Generating highlights for topic: {topic}")
    annotated_code = _annote_line_numbers(code)
    prompt = PROMPT_HIGHLIGHTS_GENERATION.format(topic, description, annotated_code)
    output = invoke_llm(prompt)

    output = output.strip().strip("`")
    if output.startswith("csv\n"):
        output = output[4:]

    if output.startswith("start_line_number"):
        output = '\n'.join(output.split("\n")[1:])

    csv_lines = output.split("\n")
    data = [line.split("|").strip() for line in csv_lines]

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


def generate_script(topic: str) -> Script:
    logger.info(f"Generating script for topic: {topic}")
    description = _generate_topic_description(topic)
    code = _generate_code(topic, description)
    highlights = _generate_highlights(topic, description, code)

    script = Script(
        code=code,
        intro_text="Hello",
        highlights=highlights,
        cta_text="",
    )

    return script
