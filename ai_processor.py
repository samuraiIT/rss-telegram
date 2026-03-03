import json
import logging
from openai import OpenAI, APIError
import config

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.OPENROUTER_API_KEY,
)

MODEL = "qwen/qwen3-32b:free"

SYSTEM_PROMPT = """Ты — AI-эксперт, который оценивает посты из Telegram-каналов про AI/ML/Data Science.

Для каждого поста ты должен:
1. Оценить релевантность по шкале от 1 до 10 (10 = очень релевантный и полезный контент про AI/ML/DS)
2. Написать краткое саммари на русском языке (2-4 предложения), сохраняя ключевые факты и выводы

Ответь строго в формате JSON без markdown-обёртки:
{
  "score": <число от 1 до 10>,
  "summary": "<краткое саммари на русском>"
}

Критерии оценки:
- 9-10: Важные новости, прорывы, детальный технический контент
- 7-8: Полезный контент, обзоры, туториалы
- 5-6: Общая информация, косвенно связанная с AI/ML
- 1-4: Нерелевантный контент, реклама, спам"""


async def evaluate_and_summarize(text: str) -> dict | None:
    """Send text to OpenRouter (Qwen) for relevance evaluation and summarization.

    Returns dict with keys: relevant (bool), score (int), summary (str)
    or None on error.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        response_text = response.choices[0].message.content.strip()

        # Strip <think>...</think> blocks (Qwen reasoning)
        import re
        response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            response_text = "\n".join(lines).strip()

        data = json.loads(response_text)
        score = int(data["score"])
        summary = data["summary"]

        return {
            "relevant": score >= config.RELEVANCE_THRESHOLD,
            "score": score,
            "summary": summary,
        }
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Failed to parse model response: {e}")
        return None
    except APIError as e:
        logger.error(f"OpenRouter API error: {e}")
        return None
