import requests
from icecream import ic
class OpenAIProvider:
    def __init__(self, model_name: str, api_key: str, proxy: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.proxy = proxy

    def generate_text(self, messages: list[dict]) -> str:
        try:
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            } if self.proxy else None

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1000,
                },
                proxies=proxies,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            ic(f"Ошибка вызова OpenAI API: {e}")
            return ""


