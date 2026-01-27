# ui.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Static, RichLog, Button, Label, OptionList
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.binding import Binding

class ModelListScreen(ModalScreen[str]):
    """Окно выбора модели"""
    def __init__(self, models: list):
        super().__init__()
        self.models = models

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Выберите модель из списка:", id="dialog_header")
            option_list = OptionList(id="model_options")
            for model in self.models:
                option_list.add_option(model["name"])
            yield option_list
            yield Button("Отмена", id="cancel_dialog", variant="error")

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option.prompt))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_dialog":
            self.dismiss(None)

class LlamaUI(App):
    CSS = """
    ModelListScreen { align: center middle; background: rgba(0,0,0,0.7); }
    #dialog { width: 60; height: auto; border: thick $accent; background: $surface; padding: 1 2; }
    #model_options { height: auto; max-height: 15; border: solid #444; margin-bottom: 1; }
    
    #top_bar { 
        height: auto; min-height: 3; background: #1a1d22; 
        border-bottom: solid #333; padding: 1 1; align-vertical: middle; 
    }
    #model_label { width: auto; min-width: 25; color: #00ffff; padding: 0 1; text-style: bold; }
    
    #chat_container { height: 1fr; background: #0b0e14; border: solid #333; }
    #chat_log { width: 100%; height: auto; padding: 1; }
    
    #logs_container { width: 35; background: #0a0d12; border-right: solid #222; }
    #system_log { height: 1fr; }
    
    #input_area { height: 8; dock: bottom; border-top: solid #333; padding: 1; background: #1a1d22; }
    #user_input { width: 1fr; height: 100%; border: solid #444; }
    
    #send_button { width: 16; height: 100%; margin-left: 1; }
    /* Стиль для кнопки СТОП */
    .stop-style { background: #aa0000; color: white; border: none; text-style: bold; }
    .stop-style:hover { background: #ff0000; }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Выход"),
        Binding("ctrl+l", "clear_chat", "Очистить"),
        Binding("ctrl+j", "submit", "Отправить/Стоп"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="top_bar"):
            yield Button("Модели", id="model_btn")
            yield Static("Не выбрана", id="model_label")
            yield Button("Загрузить", id="load_button", variant="success", disabled=True)
            yield Button("Сброс", id="unload_button", variant="error", disabled=True)
        
        with Horizontal():
            with Vertical(id="logs_container"):
                yield Static("Системные Логи", id="log_header", classes="log-header")
                yield RichLog(id="system_log", markup=True, wrap=True)
                yield Button("Копировать логи", id="copy_logs")
            
            with ScrollableContainer(id="chat_container"):
                yield Static(id="chat_log", markup=True)
        
        with Horizontal(id="input_area"):
            yield TextArea(id="user_input")
            yield Button("Отправить", id="send_button", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#user_input").focus()
        self.query_one(Footer).visible = False
