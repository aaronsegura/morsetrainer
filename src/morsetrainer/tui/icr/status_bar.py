from textual.app import ComposeResult
from textual.widgets import Label, Footer
from textual.reactive import reactive
from textual.containers import Horizontal, Container


class StatusWPM(Label):
    wpm = reactive(default=20)

    def render(self) -> str:
        return f"[b]{self.wpm}[/]wpm"


class StatusFrequency(Label):
    frequency = reactive(default=450)

    def render(self) -> str:
        return f"[b]{self.frequency}[/]Hz"


class MyFooter(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(id="footer-outer"):
            with Horizontal(id="footer-inner"):
                yield Footer()
            yield StatusBar()


class StatusBar(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(id="status_bar"):
            yield Label("|", classes="label-separator")
            yield StatusWPM(classes="label")
            yield Label("@", classes="label")
            yield StatusFrequency(classes="label")
