import hmac
import hashlib
import requests
from flask import jsonify
from consts import LOCAL_FLASK_HOST, FLASK_PORT, TAIGA_USER_NAME
from icecream import ic

class TaigaService:
    def __init__(self, api_url: str, auth_token: str, webhook_secret: str, project_id: int, us_id: int, headers: dict):
        self.api_url = api_url
        self.auth_token = auth_token
        self.webhook_secret = webhook_secret
        self.project_id = project_id
        self.us_id = us_id
        self.headers = headers
        
    def __str__(self):
        return f"TaigaService(api_url={self.api_url}, auth_token={self.auth_token}, webhook_secret={self.webhook_secret}, project_id={self.project_id}, us_id={self.us_id})"

    def handle_taiga_webhook(self, request):
        if not self.verify_signature(request):
            return jsonify({"error": "Invalid signature"}), 403
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        json_data = request.get_json()
        username = json_data.get("data").get("assigned_to").get("username")
        if username == TAIGA_USER_NAME:
            if json_data.get("type") == "task" and json_data.get("action") == "create":
                return self.handle_taiga_webhook_task_create(json_data.get("data"))
            elif json_data.get("type") == "task" and json_data.get("action") == "change" and json_data.get("by").get("username") != TAIGA_USER_NAME:
                ic("task change")
                return self.handle_taiga_webhook_task_change(json_data.get("data"))
        return jsonify({"status": "ok"}), 200

    def handle_taiga_webhook_task_create(self, data):
        project_id = data.get("project").get("id")
        us_id = data.get("user_story").get("id")
        if project_id == self.project_id and us_id == self.us_id:
            subject = data.get("subject")
            task_id = data.get("id")
            self.add_comment(task_id, "🤖 Принято в работу!")
            self.change_status(task_id, 2)
            ic(f"Обработана задача #{task_id}")
            requests.get(f"http://{LOCAL_FLASK_HOST}:{FLASK_PORT}/generate-code-task-create?text={subject}&task_id={task_id}")
            return jsonify({"status": "ok"}), 200

    def handle_taiga_webhook_task_change(self, data):
        project_id = data.get("project").get("id")
        us_id = data.get("user_story").get("id")
        if project_id == self.project_id and us_id == self.us_id:
            subject = data.get("subject")
            task_id = data.get("id")
            comments = self.get_task_comments(task_id)
            sorted_comments = sorted(comments, key=lambda x: x['created_at'], reverse=False)

            last_comment = sorted_comments[-1]
            filtered_comments = sorted_comments[2:-1]  
            json_data = {
                "subject": subject,
                "comments": filtered_comments[:6],
                "last_comment": last_comment,
                "task_id": task_id
            }
            requests.post(f"http://{LOCAL_FLASK_HOST}:{FLASK_PORT}/generate-code-task-change", json=json_data)
            return jsonify({"status": "ok"}), 200


    def verify_signature(self, request):
        signature = request.headers.get("X-TAIGA-WEBHOOK-SIGNATURE")
        if not signature:
            return False
        
        body = request.get_data()
        expected_signature = hmac.new(
            key=self.webhook_secret.encode(),
            msg=body,
            digestmod=hashlib.sha1
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def get_task(self, task_id: int):
        try:
            response = requests.get(
                f"{self.api_url}/tasks/{task_id}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            ic(f"Ошибка соединения: {type(e).__name__}: {str(e)}")
            return False


    def get_task_comments(self, task_id: int):
        try:
            response = requests.get(
                f"{self.api_url}/history/task/{task_id}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            ic(f"Ошибка соединения: {type(e).__name__}: {str(e)}")
            return False

    def add_comment(self, task_id: int, comment: str):
        task = self.get_task(task_id)
        version = task.get("version")
        data = {
            "comment": comment,
            "version": version
        }
        url = f"{self.api_url}/tasks/{task_id}"
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            return response.status_code == 201
        except Exception as e:
            ic(f"Ошибка соединения: {type(e).__name__}: {str(e)}")
            return False


    def change_status(self, task_id: int, status_id: int):
        task = self.get_task(task_id)
        version = task.get("version")
        data = {
            "status": status_id,
            "version": version,
            "id": task_id
        }
        url = f"{self.api_url}/tasks/{task_id}"
        ic(f"Отправка статуса {status_id} к задаче {task_id}")
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            return response.status_code == 201
        except Exception as e:
            ic(f"Ошибка соединения: {type(e).__name__}: {str(e)}")
            return False