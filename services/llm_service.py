from services.db_service import DBService
from services.taiga_service import TaigaService
from promts import base_promt, task_promt, project_structure_promt, classes_description_promt, methods_description_promt
from flask import jsonify
from consts import TAIGA_USER_NAME
from icecream import ic

class LLMService:
    def __init__(self, providers: dict, db_service: DBService, taiga_service: TaigaService):
        self.providers = providers
        self.db_service = db_service
        self.taiga_service = taiga_service

    def ask_openai(self, messages: list[dict]) -> str:
        # return "gpt is offline"
        return self.providers["openai"].generate_text(messages)
    
    def ask_wizardcoder(self, prompt: str) -> str:
        return self.providers["wizardcoder"].generate_text(str(prompt))
    
    
    def generate_prompt_for_task_create(self, text: str, limit: int) -> list[dict]:
        messages = [
            {"role": "system", "content": base_promt.format(programming_language="python")},
            {"role": "system", "content": "Я тебе предоставляю структуру проекта\n" + project_structure_promt},
            {"role": "user", "content": "Описание нескольких классов из существующего кода: \n" + self.__get_classes_description(text, limit)},
            {"role": "user", "content": "Описание нескольких методов из существующего кода: \n" + self.__get_methods_description(text, limit)},
            {"role": "user", "content": task_promt.format(task=text)}
        ]
        with open("messages.txt", "w", encoding="utf-8") as f:
            f.write(str(messages))
        # ic(messages)
        return messages

    def __get_classes_description(self, text: str, limit: int) -> str:
        classes_payload = self.db_service.get_class_payload_from_text(text, limit)
        classes_description = ""
        if classes_payload:
            for payload in classes_payload:
                classes_description += classes_description_promt.format(class_name=payload.payload["name"], file_path=payload.payload["file_path"], class_description=payload.payload["text"])
        return classes_description

    def __get_methods_description(self, text: str, limit: int) -> str:
        methods_payload = self.db_service.get_method_payload_from_text(text, limit)
        methods_description = ""
        if methods_payload:
            for payload in methods_payload:
                methods_description += methods_description_promt.format(method_name=payload.payload["name"], file_path=payload.payload["file_path"], method_description=payload.payload["text"])
        return methods_description
    

    def generate_prompt_for_task_change(self, subject: str, comments: list[dict], last_comment: dict, limit: int=4) -> list[dict]: 
        messages = [
            {"role": "system", "content": base_promt.format(programming_language="python")},
            {"role": "system", "content": "Я тебе предоставляю структуру проекта\n" + project_structure_promt},
            {"role": "user", "content": "Описание нескольких классов из существующего кода: \n" + self.__get_classes_description(subject, limit)},
            {"role": "user", "content": "Описание нескольких методов из существующего кода: \n" + self.__get_methods_description(subject, limit)},
            {"role": "user", "content": task_promt.format(task=subject)},
        ]


        for comment in comments:
            # ic(comment)
            if comment['user']['username'] == TAIGA_USER_NAME:
                messages.append({"role": "assistant", "content": comment['comment']})
            else:
                messages.append({"role": "user", "content":comment['comment']})
        messages.append({"role": "user", "content": last_comment['comment']})
        # ic(messages)
        return messages