import requests
from icecream import ic
class WizardCoderProvider:
    def __init__(self, model_name: str, host: str):
        self.model_name = model_name
        self.host = host.rstrip('/')
        self.max_context_length = 1500


    def generate_text(self, prompt: str) -> str:
        url = f"{self.host}/v1/completions"
        headers={"Content-Type": "application/json"}
        json_data = {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.3,
            "model": self.model_name
        }
        response = requests.post(url, headers=headers, json=json_data)
        ic(response.json())
        if response.status_code == 200:
            return response.json()['choices'][0]['text']
        else:
            return ""
