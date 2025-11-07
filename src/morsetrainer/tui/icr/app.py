from textual.app import App, ComposeResult
from textual.widgets import Header

from typing import override, final, Any

from morsetrainer.core import MorseToneContext
from morsetrainer.storage import MorseToneSaveFile

from .status_bar import MyFooter
from .game_panel import GamePanel
from .history_panel import HistoryPanel
from .settings_modal import SettingsModal

type key_value = dict[str, Any]


@final
class IcrTuiApp(App[int]):
    CSS_PATH = "../app.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("ctrl+s", "sound_settings", "Sound"),
        ("ctrl+t", "choose_theme", "Theme"),
        ("ctrl+p", "start_stop", "Start/Stop"),
    ]
    TITLE = "ICR Trainer"
    SUB_TITLE = "Just morsin' around"
    MCT_TONE_CONTROL: MorseToneContext

    @override
    def compose(self) -> ComposeResult:
        f = MorseToneSaveFile()
        self.MCT_TONE_CONTROL: MorseToneContext = f.load()

        yield Header(icon="💫")
        yield GamePanel()
        yield HistoryPanel()
        yield MyFooter()

    def _update_status_bar(self, ctx: MorseToneContext) -> None:
        from .status_bar import (
            StatusFrequency,
            StatusWPM,
        )

        self.query_one(StatusWPM).wpm = ctx.wpm
        self.query_one(StatusFrequency).frequency = ctx.frequency

    def action_sound_settings(self) -> None:
        def save_settings(new_ctx: MorseToneContext | None) -> None:
            if new_ctx:
                self._update_status_bar(new_ctx)
                self.MCT_TONE_CONTROL = new_ctx
                f = MorseToneSaveFile()
                f.save(new_ctx)
                self.app.notify("Updated Settings!", timeout=1)

        modal = SettingsModal(self.MCT_TONE_CONTROL)
        self.push_screen(modal, save_settings)

    def action_choose_theme(self) -> None:
        self.search_themes()

    def action_start_stop(self) -> None:
        self.query_one(GamePanel).start()
