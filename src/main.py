
import logging
from src.audio_processing import generate_audio
from src.video_processing import generate_video
from src.script_processing import generate_script


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
root_logger.addHandler(ch)

logger = logging.getLogger(__name__)


def main():
    topic = "Using elevenlabs to generate audio from text"
    script = generate_script(topic)

    voice_clip = generate_audio(script.intro_text, "./assets/audio/intro.mp3")
    script.intro_text_voide_clip = voice_clip
    
    for idx, code_block in enumerate(script.highlights):
        voice_file = f"./assets/audio/voice_{idx}.mp3"
        voice_clip = generate_audio(code_block.text, voice_file)
        code_block.voice_clip = voice_clip


    video_path = generate_video(script)


if __name__ == "__main__":
    main()
