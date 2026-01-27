# _main_.py
import os, asyncio, queue, subprocess
from textual.app import App
from ui import LlamaUI, ModelListScreen
from model_chat import LlamaChat
from search import find_models_smart

class LlamaApp(LlamaUI): # ИСПРАВЛЕНО: наследуем от LlamaUI
    def __init__(self):
        super().__init__()
        self.out_q = queue.Queue()
        self.err_q = queue.Queue()
        self.full_chat_text = ""
        self.log_messages = []
        self.current_chat = None
        self.is_generating = False
        self.models = find_models_smart("models")
        self.selected_model_data = None

    def on_mount(self) -> None:
        super().on_mount()
        if self.models:
            self.write_log(f"[✓] Найдено {len(self.models)} моделей. Выберите в меню.")
        else:
            self.write_log("[!] Модели не найдены в папке 'models'.")
        self.set_interval(0.1, self.update_logs)

    def toggle_generating_ui(self, generating: bool):
        """Меняет кнопку Отправить на Стоп и наоборот"""
        self.is_generating = generating
        btn = self.query_one("#send_button")
        if generating:
            btn.label = "Остановить"
            btn.add_class("stop-style")
            btn.variant = "default"
        else:
            btn.label = "Отправить"
            btn.remove_class("stop-style")
            btn.variant = "primary"

    def action_submit(self) -> None:
        if self.is_generating:
            if self.current_chat:
                self.current_chat.stop_generation()
            return

        if not self.current_chat:
            self.write_log("[!] Сначала загрузите модель!")
            return

        input_widget = self.query_one("#user_input")
        text = input_widget.text.strip()
        if not text: return

        self.full_chat_text += f"\n[bold green]Вы:[/bold green] {text}\n[bold yellow]ИИ:[/bold yellow] "
        self.query_one("#chat_log").update(self.full_chat_text)
        input_widget.load_text("")
        self.query_one("#chat_container").scroll_end(animate=False)

        self.toggle_generating_ui(True)
        # Передаем callback, который вернет кнопку в норму
        self.current_chat.start(
            text, self.out_q, self.err_q, 
            lambda: self.app.call_from_thread(self.toggle_generating_ui, False)
        )

    def on_button_pressed(self, event) -> None:
        bid = event.button.id
        if bid == "send_button":
            self.action_submit()
        elif bid == "model_btn":
            self.push_screen(ModelListScreen(self.models), self.select_model_callback)
        elif bid == "load_button":
            self.action_load_model()
        elif bid == "unload_button":
            self.action_unload_model()
        elif bid == "copy_logs":
            self.app.copy_to_clipboard("\n".join(self.log_messages))
            self.write_log("[i] Логи скопированы")

    def select_model_callback(self, name):
        if name:
            self.selected_model_data = next(m for m in self.models if m["name"] == name)
            self.query_one("#model_label").update(f"Выбрано: {name}")
            self.query_one("#load_button").disabled = False
            self.write_log(f"[*] Выбрана модель: {name}")

    def action_load_model(self):
        if self.selected_model_data:
            exe_path = os.path.abspath("bin/llama-cli.exe")
            self.current_chat = LlamaChat(exe_path, self.selected_model_data, self.write_log)
            self.query_one("#load_button").disabled = True
            self.query_one("#unload_button").disabled = False
            self.query_one("#model_btn").disabled = True

    def action_unload_model(self):
        if self.current_chat:
            self.current_chat.unload()
            self.current_chat = None
            self.write_log("[✓] Модель выгружена")
        self.query_one("#load_button").disabled = False
        self.query_one("#unload_button").disabled = True
        self.query_one("#model_btn").disabled = False

    def write_log(self, msg):
        self.query_one("#system_log").write(msg)
        self.log_messages.append(msg)

    def update_logs(self):
        updated = False
        while not self.out_q.empty():
            self.full_chat_text += self.out_q.get_nowait()
            updated = True
        if updated:
            self.query_one("#chat_log").update(self.full_chat_text)
            self.query_one("#chat_container").scroll_end(animate=False)
        while not self.err_q.empty():
            self.write_log(self.err_q.get_nowait())

    def action_quit(self):
        if self.current_chat: self.current_chat.unload()
        subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"], capture_output=True)
        self.exit()

if __name__ == "__main__":
    LlamaApp().run()
