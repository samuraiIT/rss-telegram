import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Client API (Telethon)
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

# Telegram Bot API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Target channel for publishing
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "")

# OpenRouter API (free Qwen model)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Check interval
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))

# Relevance threshold
RELEVANCE_THRESHOLD = int(os.getenv("RELEVANCE_THRESHOLD", "7"))

# Source channels to monitor
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

# Keywords for filtering
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
