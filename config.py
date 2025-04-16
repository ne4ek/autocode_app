from consts import *
from services.taiga_service import TaigaService
from services.db_service import DBService
from db.db_config import qdrant_database
from services.embedding_service import EmbeddingService
from sentence_transformers import SentenceTransformer
from services.llm_service import LLMService
from services.llm.wizardcoder_provider import WizardCoderProvider
from services.llm.open_ai_provider import OpenAIProvider

taiga_service = TaigaService(TAIGA_API_URL, TAIGA_AUTH_TOKEN, TAIGA_WEBHOOK_SECRET, PROJECT_ID, US_ID, HEADERS)

embedding_service = EmbeddingService(SentenceTransformer(EMBEDDING_MODEL))
db_service = DBService(qdrant_database, embedding_service)


__providers = {
    "wizardcoder": WizardCoderProvider(WIZARDCODER_MODEL, WIZARDCODER_HOST),
    "openai": OpenAIProvider(OPENAI_MODEL, OPENAI_API_KEY, PROXY)
}

llm_service = LLMService(__providers, db_service, taiga_service)