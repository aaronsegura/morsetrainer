from textual.app import ComposeResult
from textual.widgets import TextArea
from textual.containers import Container, Horizontal


class HelpScreen(Container):
    def compose(self) -> ComposeResult:
        yield TextArea("THIS IS A THING", id="help-text")
