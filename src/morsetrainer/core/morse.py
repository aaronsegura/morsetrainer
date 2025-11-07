"""Morse Code encodier.

With thanks to:
    https://www.exchangetuts.com/removecontrol-clicking-sound-using-pyaudio-as-an-oscillator-1641675424622548
"""

import numpy
import pyaudio
from dataclasses import dataclass, field
import morsedecode


_TONE_FADE_BASE = 0.001
_SAMPLING_RATE = 48000


@dataclass
class MorseToneContext:
    wpm: int
    frequency: int
    tone_fade: int


@dataclass
class Tone:
    frequency: int
    duration: float
    tone_fade: int
    sampling_frequency: int = field(default=_SAMPLING_RATE)

    @property
    def stream(self) -> bytes:
        return self.faded_tone(
            self.frequency, self.duration, self.tone_fade, self.sampling_frequency
        )

    @classmethod
    def faded_tone(
        cls, frequency: int, length: float, tone_fade: int, rate: int = _SAMPLING_RATE
    ) -> bytes:
        def _sine(frequency: int, length: float, rate: int):
            import math

            samples = int(length * rate)
            factor = float(frequency) * (math.pi * 2) / rate
            return numpy.sin(numpy.arange(samples) * factor)

        chunks = [_sine(frequency, length, rate)]
        chunk = numpy.concatenate(chunks) * 0.25

        fade = int(_TONE_FADE_BASE * tone_fade * rate)

        fade_in = numpy.arange(0.0, 1.0, 1 / fade)
        fade_out = numpy.arange(1.0, 0.0, -1 / fade)

        chunk[:fade] = numpy.multiply(chunk[:fade], fade_in)
        chunk[-fade:] = numpy.multiply(chunk[-fade:], fade_out)

        return chunk.astype(numpy.float32).tobytes()


@dataclass
class MorseTones:
    ctx: MorseToneContext
    stream: pyaudio.Stream

    def play_letter(self, letter: str) -> None:
        _letter = Letter(letter)
        self.stream.write(_letter.stream(self.ctx))

    def play_word(self, word: str) -> None:
        _word = Word(word)
        self.stream.write(_word.stream(self.ctx))

    def play_phrase(self, phrase: str) -> None:
        _phrase = Phrase(phrase)
        self.stream.write(_phrase.stream(self.ctx))

    def play_tone(self, duration: float, frequency: int, tone_fade: int = 2) -> None:
        self.stream.write(Tone.faded_tone(frequency, duration, tone_fade))


class Phrase:
    def __init__(self, phrase: str) -> None:
        self._phrase: str = phrase

    def stream(self, ctx: MorseToneContext) -> bytes:
        phrase_stream: list[bytes] = []
        for word in self._phrase.split(" "):
            _word = Word(word)
            phrase_stream.append(_word.stream(ctx))
            phrase_stream.append(_silence(_dit_length(ctx.wpm) * 5))
        return b"".join(phrase_stream)


class Word:
    def __init__(self, word: str) -> None:
        self._word: str = word

    def stream(self, ctx: MorseToneContext) -> bytes:
        word_stream: list[bytes] = []
        for letter in self._word:
            _letter = Letter(letter)
            word_stream.append(_letter.stream(ctx))
            word_stream.append(_silence(_dit_length(ctx.wpm) * 3))
        return b"".join(word_stream)


class Letter:
    def __init__(self, letter: str) -> None:
        if len(letter) != 1:
            raise RuntimeError("Letter must be one letter.")

        self._letter: str = letter
        self._morse: str = morsedecode.encode(self._letter)

    def stream(self, ctx: MorseToneContext) -> bytes:
        letter_stream: list[bytes] = []
        for particle in self._morse:
            match particle:
                case "-":
                    letter_stream.append(_dah(ctx))
                case ".":
                    letter_stream.append(_dit(ctx))

            letter_stream.append(_silence(_dit_length(ctx.wpm)))

        return b"".join(letter_stream)


def _dit_length(wpm: int) -> float:
    return 60 / (50 * wpm)


def _dit(
    ctx: MorseToneContext,
) -> bytes:
    return Tone.faded_tone(ctx.frequency, _dit_length(ctx.wpm), ctx.tone_fade)


def _dah(
    ctx: MorseToneContext,
) -> bytes:
    return Tone.faded_tone(ctx.frequency, _dit_length(ctx.wpm) * 3, ctx.tone_fade)


def _silence(length: float, rate: int = _SAMPLING_RATE) -> bytes:
    return Tone.faded_tone(0, length, 1, rate)
