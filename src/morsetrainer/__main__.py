import argparse
import pyaudio

from morsetrainer.core import MorseToneContext, Phrase

_FS = 48000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ICR Trainer")

    parser.add_argument(
        "--phrase",
        "-p",
        help="Phrase to be translated.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--wpm",
        "-w",
        help="Words per minute",
        type=int,
        default=20,
    )
    parser.add_argument(
        "--freq",
        "-f",
        help="Tone frequency in Hz",
        type=int,
        default=450,
    )
    parser.add_argument(
        "--fade",
        "-F",
        help="Soften the edges on the tones.",
        type=int,
        default=2,
    )

    return parser.parse_args()


def main():
    try:
        morse()
    except RuntimeError as e:
        print(e)
        exit(1)


def morse():
    args = parse_args()

    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=_FS,
        output=True,
    )
    phrase = Phrase(args.phrase)
    context = MorseToneContext(args.wpm, args.freq, args.fade)
    stream.write(phrase.stream(context))
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    main()
