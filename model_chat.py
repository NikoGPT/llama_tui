# model_chat.py
import requests, subprocess, time, threading, os, json, re

class LlamaChat:
    def __init__(self, exe_path, model_data, log_callback=None):
        self.base_url = "http://127.0.0.1:8080"
        self.url = f"{self.base_url}/v1/chat/completions"
        self.exe = os.path.join(os.path.dirname(exe_path), "llama-server.exe")
        self.model_path = model_data["path"]
        self.model_name = model_data.get("name", "")
        self.log_callback = log_callback or print
        self.process = None
        self.stop_event = threading.Event() # Событие для остановки
        self.history = [{"role": "system", "content": "You are a helpful assistant."}]
        self.load_model()

    def load_model(self):
        self.log(f"[*] Запуск сервера для: {self.model_name}")
        self.process = subprocess.Popen([
            self.exe, "-m", self.model_path, "--port", "8080",
            "-ngl", "999", "--chat-template", "chatml"
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        for _ in range(20):
            try:
                requests.get(f"{self.base_url}/health", timeout=1)
                self.log("[✓] Сервер готов")
                return
            except:
                time.sleep(0.5)
        raise Exception("Сервер не отвечает")

    def unload(self):
        if self.process:
            self.process.terminate()
            self.process = None

    def clean_text(self, text):
        """Удаляет технические токены (Llama, Qwen, DeepSeek, ChatML)"""
        tokens = [
            r"<\|im_start\|>", r"<\|im_end\|>", r"<\|endoftext\|>",
            r"<\|file_separator\|>", r"\[INST\]", r"\[/INST\]",
            r"<\|end_of_turn\|>", r"assistant\n", r"user\n"
        ]
        for t in tokens:
            text = re.sub(t, "", text, flags=re.IGNORECASE)
        return text

    def start(self, user_input, out_q, err_q, on_finished_callback):
        self.stop_event.clear()
        self.history.append({"role": "user", "content": user_input})

        def run():
            full_response = ""
            try:
                payload = {"messages": self.history, "stream": True, "temperature": 0.7}
                with requests.post(self.url, json=payload, stream=True, timeout=5) as r:
                    for line in r.iter_lines():
                        if self.stop_event.is_set():
                            err_q.put("[!] Генерация прервана")
                            break
                        
                        if not line: continue
                        line_str = line.decode('utf-8').replace("data: ", "")
                        if line_str.strip() == "[DONE]": break
                        
                        try:
                            data = json.loads(line_str)
                            delta = data['choices'][0]['delta'].get('content', '')
                            if delta:
                                clean_delta = self.clean_text(delta)
                                full_response += clean_delta
                                out_q.put(clean_delta)
                        except: continue

                self.history.append({"role": "assistant", "content": full_response})
                if len(self.history) > 11:
                    self.history = [self.history[0]] + self.history[-10:]
            except Exception as e:
                err_q.put(f"[ERR] {e}")
            finally:
                on_finished_callback()

        threading.Thread(target=run, daemon=True).start()

    def stop_generation(self):
        self.stop_event.set()

    def log(self, msg):
        if self.log_callback: self.log_callback(msg)
