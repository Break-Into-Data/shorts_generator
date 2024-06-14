from dataclasses import dataclass
import io
import subprocess

import pixie
import black
import PIL.Image
from pygments import highlight
from pygments.style import Style
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pygments.token import (
    Keyword,
    Name,
    Comment,
    String,
    Error,
    Number,
    Operator,
    Generic,
    Punctuation,
)

from src.script_processing import Script
from src.audio_processing import combine_audio_clips


class SimpleStyle(Style):
    default_style = ""
    background_color = "#212121"
    styles = {
        Comment: "italic #888",
        Keyword: "#2e95d3",
        Name: "#fff",
        Name.Function: "#e9950c",
        Name.Class: "bold #0f0",
        String: "#ba2121",
        Error: "bg:#F00 #FFF",
        Number: "#df3079",
        Operator: "#fff",
        Punctuation: "#fff",
        Generic.Output: "#888",
    }


def generate_code_image(code: str):
    # Highlight the code
    highlighted_code = highlight(
        code,
        PythonLexer(),
        ImageFormatter(
            style=SimpleStyle,
            font_name="Courier",
            line_numbers=False,
            dpi=400,
            font_size=40,
        ),
    )

    image = PIL.Image.open(io.BytesIO(highlighted_code))
    path = "./assets/images/code_image.png"
    image.save(path)

    return path


def generate_frame(
    code_image,
    highlighted_code_block,
    frame_w=1080,
    frame_h=1920,
):
    image = pixie.Image(frame_w, frame_h)
    image.fill(pixie.Color(0.12, 0.12, 0.12, 1))

    code_image_x = (frame_w - code_image.width) // 2
    code_image_y = (frame_h - code_image.height) // 2

    image.draw(
        code_image,
        pixie.translate(
            code_image_x,
            code_image_y,
        ),
    )

    paint = pixie.Paint(pixie.SOLID_PAINT)
    paint.color = pixie.Color(1, 0, 0, 0.1)

    line_height = 371 / 11

    if highlighted_code_block.line_count > 0:
        ctx = image.new_context()
        ctx.fill_style = paint
        ctx.rounded_rect(
            code_image_x + 0,
            code_image_y + line_height * highlighted_code_block.line_number,
            code_image.width,
            line_height * highlighted_code_block.line_count + 14,
            25,
            25,
            25,
            25,
        )
        ctx.fill()

    return image


@dataclass
class HighlightedCodeBlock:
    line_number: int
    line_count: int


def add_audio_to_video(video_path: str, voice_path: str, start_offset: int):
    new_path = f"./assets/clips/final.mp4"
    command = f"ffmpeg -i {video_path} -itsoffset {start_offset} -i {voice_path} -map 0:v -map 1:a -c:v copy -c:a aac -y {new_path}"
    subprocess.run(command, shell=True, check=True)
    
    return new_path


def generate_video(script: Script):
    code_image_path = generate_code_image(script.code)
    code_image = pixie.read_image(code_image_path)

    frame = generate_frame(
        code_image=code_image,
        highlighted_code_block=HighlightedCodeBlock(
            line_number=-1,
            line_count=0,
        ),
    )
    frame.write_file("./assets/images/frame_intro.png")
    dur = script.intro_text_voide_clip.duration
    command = f"ffmpeg -y -loop 1 -i ./assets/images/frame_intro.png -c:v libx264 -t {dur} -pix_fmt yuv420p ./assets/clips/clip_intro.mp4"
    subprocess.run(command, shell=True, check=True)

    for idx, code_block in enumerate(script.highlights):
        frame = generate_frame(
            code_image=code_image,
            highlighted_code_block=HighlightedCodeBlock(
                line_number=code_block.line_number,
                line_count=code_block.line_count,
            ),
        )
        frame.write_file(f"./assets/images/frame_{idx}.png")

        dur = code_block.voice_clip.duration
        command = f"ffmpeg -y -loop 1 -i ./assets/images/frame_{idx}.png -c:v libx264 -t {dur} -pix_fmt yuv420p ./assets/clips/clip_{idx}.mp4"
        subprocess.run(command, shell=True, check=True)

    # create a text file with the list of videos to concatenate
    concat_file = "./assets/clips/concat.txt"
    with open(concat_file, "w") as f:
        f.write("file 'clip_intro.mp4'\n")
        for idx, code_block in enumerate(script.highlights):
            f.write(f"file 'clip_{idx}.mp4'\n")

    # combine all the clips into one video
    video_path = "./assets/clips/combined.mp4"
    
    command = (
        f"ffmpeg -y -f concat -safe 0 -i {concat_file} -c copy {video_path}"
    )
    subprocess.run(command, shell=True, check=True)
    
    # combine all the audio files into one
    final_audio_filepath = combine_audio_clips([
        script.intro_text_voide_clip, 
    ] + [
        code_block.voice_clip
        for code_block in script.highlights
    ])
    
    video_path = add_audio_to_video(
        video_path=video_path,
        voice_path=final_audio_filepath,
        start_offset=0,
    )
    print(video_path)
    return video_path
