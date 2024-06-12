import os
from dataclasses import dataclass
import subprocess
import tempfile

import dotenv
import mutagen.mp3

from elevenlabs import save
from elevenlabs.client import ElevenLabs


dotenv.load_dotenv()


@dataclass
class VoiceClip:
    text: str
    file_path: str
    duration: int


def get_audio_length(file_path: str) -> int:
    audio = mutagen.mp3.MP3(file_path)
    return int(audio.info.length) + 1


def pad_audio_file(file_path: str, duration: int):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = os.path.join(tmpdir, "tmp.mp3")
        command = f"ffmpeg -y -i {file_path} -af apad=whole_dur={duration} {tmp_file}"
        subprocess.run(command, shell=True, check=True)
        # move the padded file to the original file path
        os.rename(tmp_file, file_path)


def generate_audio(text: str, save_as: str) -> VoiceClip:
    client = ElevenLabs(
        api_key=os.getenv("ELEVEN_API_KEY"),
    )
    output = client.generate(text=text)
    save(output, save_as)
    
    dur = get_audio_length(save_as)
    pad_audio_file(save_as, dur)
    
    return VoiceClip(
        text=text,
        file_path=save_as,
        duration=dur,
    )
    
    
