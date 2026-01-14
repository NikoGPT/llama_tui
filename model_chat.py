import requests, subprocess, time, threading, os, json

class LlamaChat:
    def __init__(self, exe_path, model_data):
        self.url = "http://127.0.0.1:8080/v1/chat/completions" # Перешли на OpenAI-совместимый эндпоинт
        self.exe = os.path.join(os.path.dirname(exe_path), "llama-server.exe")
        self.model_path = model_data["path"]
        self.history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        self._ensure_server_running()

    def _ensure_server_running(self):
        try:
            requests.get("http://127.0.0.1:8080/health", timeout=1)
        except:
            subprocess.Popen([self.exe, "-m", self.model_path, "--port", "8080", 
                            "-ngl", "999", "--log-disable", "--chat-template", "chatml"], 
                            creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(5)

    def start(self, user_input, out_q, err_q):
        self.history.append({"role": "user", "content": user_input})
        
        def run():
            try:
                full_response = ""
                payload = {
                    "messages": self.history,
                    "stream": True,
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                
                with requests.post(self.url, json=payload, stream=True) as r:
                    for line in r.iter_lines():
                        if not line: continue
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data: "):
                            if "[DONE]" in line_str: break
                            data = json.loads(line_str[6:])
                            delta = data['choices'][0]['delta'].get('content', '')
                            if delta:
                                full_response += delta
                                out_q.put(delta)
                
                
                self.history.append({"role": "assistant", "content": full_response})
                
                
                if len(self.history) > 11:
                    self.history = [self.history[0]] + self.history[-10:]
                    
            except Exception as e:
                err_q.put(f"[ERR] {e}")

        threading.Thread(target=run, daemon=True).start()
