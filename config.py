import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "")

OMNI_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNI_API_KEY = os.getenv("OMNIROUTE_API_KEY", "any-string")

LLM_MODEL_SUMMARY = os.getenv("LLM_MODEL_SUMMARY", "ws/claude-sonnet-4-6")
LLM_MODEL_PROFILE = os.getenv("LLM_MODEL_PROFILE", "gc/gemini-3-flash")
LLM_MODEL_HUMANIZE = os.getenv("LLM_MODEL_HUMANIZE", "ws/claude-haiku-4-5")

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
RELEVANCE_THRESHOLD = int(os.getenv("RELEVANCE_THRESHOLD", "7"))

SOURCE_CHANNELS = [
    "ai_newz",
    "gonzo_ML",
    "data_secrets",
    "machinelearning_ru",
    "dlinnlp",
    "neuralmind",
    "aiexplained_official",
    "datascienceandai",
]

KEYWORDS = [
    "ai", "ml", "artificial intelligence", "machine learning",
    "deep learning", "llm", "gpt", "claude", "gemini",
    "neural network", "нейросет", "data science",
    "nlp", "computer vision", "transformer",
    "fine-tuning", "fine tuning", "rag",
    "retrieval augmented", "langchain", "llama",
    "mistral", "openai", "anthropic", "hugging face",
    "stable diffusion", "midjourney", "генеративный",
    "prompt engineering", "embeddings", "vector database",
    "rlhf", "lora", "qlora", "agents", "multimodal",
]
