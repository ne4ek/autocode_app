from flask import Flask, request, jsonify
from config import taiga_service, llm_service, db_service
from consts import FLASK_HOST, FLASK_PORT
from promts import *
from icecream import ic

app = Flask(__name__)


@app.route("/taiga-webhook", methods=["POST"])
def handle_webhook():
    return taiga_service.handle_taiga_webhook(request)


@app.route("/generate-code-task-create", methods=["GET"])
def generate_code_task_create():
    text = request.args.get("text")
    task_id = request.args.get("task_id")
    prompt = llm_service.generate_prompt_for_task_create(text, limit=5)
    response = llm_service.ask_openai(prompt)
    taiga_service.add_comment(task_id, response)
    return jsonify({"status": "ok"}), 200


@app.route("/generate-code-task-change", methods=["POST"])
def generate_code_task_change():
    data = request.json
    subject = data.get("subject")
    comments = data.get("comments")
    last_comment = data.get("last_comment")
    task_id = data.get("task_id")
    prompt = llm_service.generate_prompt_for_task_change(subject, comments, last_comment, limit=5)
    response = llm_service.ask_openai(prompt)
    # ic(response)
    taiga_service.add_comment(task_id, response)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)