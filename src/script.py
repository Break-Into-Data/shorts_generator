from dataclasses import dataclass
from typing import Optional

from src.audio_processing import VoiceClip


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
