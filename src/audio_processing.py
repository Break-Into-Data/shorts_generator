import os
from dataclasses import dataclass
import subprocess
import tempfile
import uuid

import dotenv
import mutagen.mp3

from elevenlabs import save
from elevenlabs.client import ElevenLabs, DEFAULT_VOICE


dotenv.load_dotenv()


@dataclass
class VoiceClip:
    text: str
    file_path: str
    duration: int


def combine_audio_clips(voice_clips: list[VoiceClip]):
    combined_path = f"./assets/audio/combined.mp3"
    concat_file = "./assets/audio/concat.txt"
    
    # Write the list of audio files to a text file
    with open(concat_file, "w+") as f:
        for voice_clip in voice_clips:
            # extract file name
            file_name = os.path.basename(voice_clip.file_path)
            f.write(f"file '{file_name}'\n")
    
    command = f"ffmpeg -f concat -safe 0 -i {concat_file} -c copy -y {combined_path}  -hide_banner -loglevel error"
    subprocess.run(command, shell=True, check=True, capture_output=False)
    
    return combined_path


def get_audio_length(file_path: str) -> int:
    audio = mutagen.mp3.MP3(file_path)
    return int(audio.info.length) + 1


def pad_audio_file(file_path: str, duration: int):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = os.path.join(tmpdir, "tmp.mp3")
        command = f"ffmpeg -y -i {file_path} -af apad=whole_dur={duration} {tmp_file}  -hide_banner -loglevel error"
        subprocess.run(command, shell=True, check=True)
        # move the padded file to the original file path
        os.rename(tmp_file, file_path)


def generate_audio(text: str, save_as: str) -> VoiceClip:
    # if not os.path.exists(save_as):
    client = ElevenLabs(
        api_key=os.getenv("ELEVEN_API_KEY"),
    )
    voice = os.getenv("ELEVEN_VOICE", DEFAULT_VOICE)
    output = client.generate(text=text, voice=voice)
    save(output, save_as)
    
    dur = get_audio_length(save_as)
    pad_audio_file(save_as, dur)
    
    return VoiceClip(
        text=text,
        file_path=save_as,
        duration=dur,
    )
