from textual.containers import Container


class GamePanel(Container):
    def start(self) -> None:
        self.app.notify("MORE THING")
