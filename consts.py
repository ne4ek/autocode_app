
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_auth_token(taiga_user_name: str, taiga_user_password: str) -> str:
    url = f"{TAIGA_API_URL}/auth"
    data = {
        "type": "normal",
        "username": taiga_user_name,
        "password": taiga_user_password
    }
    response = requests.post(url, json=data)
    return response.json().get("auth_token")


FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_PORT = os.getenv("FLASK_PORT")
LOCAL_FLASK_HOST = os.getenv("LOCAL_FLASK_HOST")

TAIGA_USER_NAME = os.getenv("TAIGA_USER_NAME")
TAIGA_USER_PASSWORD = os.getenv("TAIGA_USER_PASSWORD")

TAIGA_API_URL = os.getenv("TAIGA_API_URL")
TAIGA_AUTH_TOKEN = get_auth_token(TAIGA_USER_NAME, TAIGA_USER_PASSWORD)
TAIGA_WEBHOOK_SECRET = os.getenv("TAIGA_WEBHOOK_SECRET") 
PROJECT_SLUG = os.getenv("PROJECT_SLUG")
US_ID = int(os.getenv("US_ID"))
PROJECT_ID = int(os.getenv("PROJECT_ID"))
HEADERS = {
    "Authorization": f"Bearer {TAIGA_AUTH_TOKEN.strip()}",
    "Content-Type": "application/json"
}


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)
COLLECTION_NAME = "wiki_jarvel_embeddings"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


WIZARDCODER_MODEL = os.getenv("WIZARDCODER_MODEL")
WIZARDCODER_HOST = os.getenv("WIZARDCODER_HOST")

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY = os.getenv("PROXY")
MEDIA_WIKI_API_URL = os.getenv("MEDIA_WIKI_API_URL")
PROJECT_NAME = os.getenv("PROJECT_NAME")