from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, RichLog, Static
from textual.containers import ScrollableContainer
from textual.binding import Binding

class LlamaUI(App):
    CSS = """
    #chat_container { height: 1fr; background: #0b0e14; border: solid #333; overflow-y: scroll; }
    #chat_log { width: 100%; height: auto; padding: 1; }
    #system_log { height: 6; background: #000; color: #00ff00; border: tall #222; }
    TextArea { height: 6; dock: bottom; border: double #00ffff; }
    """
    BINDINGS = [
        Binding("ctrl+q", "quit", "Выход"),
        Binding("ctrl+l", "clear_chat", "Очистить"),
        Binding("ctrl+j", "submit", "Отправить"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="chat_container"):
            yield Static(id="chat_log", markup=True)
        yield RichLog(id="system_log", markup=True)
        yield TextArea(id="user_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#user_input").focus()
