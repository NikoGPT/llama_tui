import os, asyncio, queue, subprocess
from textual.app import App
from ui import LlamaUI
from model_chat import LlamaChat
from search import find_models_smart

class LlamaApp(LlamaUI):
    def __init__(self, chat, model_info):
        super().__init__()
        self.chat = chat
        self.model_info = model_info
        self.out_q = queue.Queue()
        self.err_q = queue.Queue()
        self.full_chat_text = ""
    def on_mount(self) -> None:
        super().on_mount()
        sys_log = self.query_one("#system_log")
        sys_log.write(f"[*] Модель: [bold]{self.model_info['name']}[/bold]")
        self.set_interval(0.1, self.update_logs)

    def action_submit(self) -> None:
        input_widget = self.query_one("#user_input")
        text = input_widget.text.strip()
        if text:
            chat_log = self.query_one("#chat_log")
            self.full_chat_text += f"\n[bold cyan]Вы:[/bold cyan]\n{text}\n\n[bold yellow]ИИ:[/bold yellow] "
            chat_log.update(self.full_chat_text)
            input_widget.load_text("") 
            self.query_one("#chat_container").scroll_end(animate=False)
            self.chat.start(text, self.out_q, self.err_q)

    def action_quit(self) -> None:
        subprocess.run(["taskkill", "/F", "/IM", "llama-server.exe"], 
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.exit()

    async def on_key(self, event):
        if event.key in ("ctrl+j", "ctrl+enter"):
            event.stop()
            event.prevent_default()
            self.action_submit()

    def update_logs(self) -> None:
        chat_log = self.query_one("#chat_log")
        new_text = ""
        while not self.out_q.empty():
            new_text += self.out_q.get_nowait()
        
        if new_text:
            self.full_chat_text += new_text
            chat_log.update(self.full_chat_text)
            self.query_one("#chat_container").scroll_end(animate=False)
            
        sys_log = self.query_one("#system_log")
        while not self.err_q.empty():
            line = self.err_q.get_nowait()
            sys_log.write(line)
    def action_clear_chat(self) -> None:
        self.full_chat_text = ""
        self.query_one("#chat_log").update("")
        self.chat.history = [self.chat.history[0]] # Сброс истории к системному промпту
        sys_log = self.query_one("#system_log")
        sys_log.write("[*] Контекст очищен")

async def main():
    exe_path = os.path.abspath("bin/llama-cli.exe")
    models = find_models_smart("models")
    if not models or not os.path.exists(exe_path):
        print("Ошибка: Проверь bin/llama-cli.exe и models/")
        return
    chat = LlamaChat(exe_path, models[0])
    app = LlamaApp(chat, models[0])
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(main())
