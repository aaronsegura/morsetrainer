from pathlib import Path
import pickle
import platformdirs

from typing import TypeVar


T = TypeVar("T")


class SaveFile[T]:
    _file: Path
    _path: Path

    def save(self, thing: T) -> None:
        self._path.mkdir(exist_ok=True, parents=True)
        with open(self._file, "wb+") as fp:
            fp.write(pickle.dumps(thing))

    def load(self) -> T:
        with open(self._file, "rb") as fp:
            ctx = pickle.loads(fp.read())
            return ctx


class MorseToneSaveFile(SaveFile):
    _path = platformdirs.user_config_path() / "morsetrainer"
    _file = _path / "config.dat"


class IcrStateSaveFile(SaveFile):
    _path = platformdirs.user_state_path() / "morsetrainer"
    _file = _path / "icr_history.dat"
