from pathlib import Path
import pickle
import platformdirs

from typing import TypeAlias


type T = TypeAlias


class SaveFile[T]:
    _file: Path

    def save(self, ctx: T) -> None:
        with open(self._file, "wb+") as fp:
            fp.write(pickle.dumps(ctx))

    def load(self) -> T:
        with open(self._file, "rb") as fp:
            ctx = pickle.loads(fp.read())
            return ctx


class MorseToneSaveFile(SaveFile):
    def __init__(self):
        config_path = platformdirs.user_config_path() / "morsetrainer"
        config_path.mkdir(exist_ok=True, parents=True)
        self._file = config_path / "config.dat"


class HistoricalSaveFile(SaveFile):
    def __init__(self):
        config_path = platformdirs.user_state_path() / "morsetrainer"
        config_path.mkdir(exist_ok=True, parents=True)
        self._file = config_path / "history.dat"
