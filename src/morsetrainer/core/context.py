from dataclasses import dataclass


@dataclass
class MorseTrainerContext:
    wpm: int
    frequency: int
    tone_fade: int
