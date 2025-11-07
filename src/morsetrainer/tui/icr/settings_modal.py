import pyaudio

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.validation import Integer
from textual.widgets import Label, Input, Button
from textual.events import Key
from typing import override

from morsetrainer.core import MorseTones, MorseToneContext

type key_value = dict[str, str | int | bool]


class SettingsModal(ModalScreen[MorseToneContext]):
    TITLE = "Settings"
    SUB_TITLE = "User Settings"

    def __init__(self, ctx: MorseToneContext):
        super().__init__()
        self.ctx = ctx

    @override
    def compose(self) -> ComposeResult:
        with Vertical(id="settings-container"):
            with Horizontal(classes="setting-row"):
                yield Label("Words per minute", classes="setting-label")
                yield Input(
                    value=str(self.ctx.wpm),
                    placeholder="20",
                    id="wpm-input",
                    type="integer",
                    validators=[
                        Integer(
                            minimum=20,
                            maximum=99,
                            failure_description="WPM must be between 20 and 99",
                        )
                    ],
                )

            with Horizontal(classes="setting-row"):
                yield Label("Frequency (Hz)", classes="setting-label")
                yield Input(
                    value=str(self.ctx.frequency),
                    placeholder="440",
                    id="freq-input",
                    type="integer",
                    validators=[
                        Integer(
                            minimum=20,
                            maximum=1600,
                            failure_description="Frequency must be between 20 and 1600",
                        )
                    ],
                )

            with Horizontal(classes="setting-row"):
                yield Label("Tone fade (1–10)", classes="setting-label")
                yield Input(
                    value=str(self.ctx.tone_fade),
                    placeholder="2",
                    id="tone-fade-input",
                    type="integer",
                    validators=[
                        Integer(
                            minimum=1,
                            maximum=10,
                            failure_description="Tone Fade must be between 1 and 10",
                        )
                    ],
                )

            with Horizontal(classes="button-container"):
                yield Button(
                    "Test Tone",
                    variant="success",
                    id="test-tone",
                    classes="settings-button",
                )
                yield Button(
                    "Save", variant="primary", id="save", classes="settings-button"
                )
                yield Button(
                    "Cancel", variant="error", id="cancel", classes="settings-button"
                )

    @work(thread=True)
    async def _play_test_tone(self) -> None:
        tone = MorseTones(self._context_from_settings(), self._stream)
        tone.play_letter("C")

    def on_mount(self) -> None:
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=48000,
            output=True,
        )

    def on_unmount(self) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._pyaudio.terminate()

    def on_key(self, key: Key) -> None:
        if key.key == "escape":
            self.dismiss()

    def _context_from_settings(self) -> MorseToneContext:
        return MorseToneContext(
            int(self.query_one("#wpm-input", Input).value or 20),
            int(self.query_one("#freq-input", Input).value or 450),
            int(self.query_one("#tone-fade-input", Input).value or 2),
        )

    def _all_inputs_valid(self) -> bool:
        for input_node in self.query(Input).results():
            self.app.log(f"{input_node.value=}")
            if "-invalid" in input_node.classes:
                return False
        return True

    @on(Input.Blurred)
    def _input_blurred(self, event: Input.Blurred) -> None:
        if event.validation_result:
            if not event.validation_result.is_valid:
                self.app.notify(
                    "\n".join(event.validation_result.failure_descriptions),
                )

    @on(Input.Changed)
    def _input_changed(self, _: Input.Changed) -> None:
        """Enable Save only when *all* validators are happy."""
        if self._all_inputs_valid():
            self.query_one("#save", Button).disabled = False
        else:
            self.query_one("#save", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.dismiss(self._context_from_settings())

        elif event.button.id == "cancel":
            self.dismiss(None)

        elif event.button.id == "test-tone":
            self._play_test_tone()
