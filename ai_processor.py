import json
import logging
import re
import httpx
import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — AI-эксперт, который оценивает посты из Telegram-каналов про AI/ML/Data Science.

Для каждого поста ты должен:
1. Оценить релевантность по шкале от 1 до 10 (10 = очень релевантный и полезный контент про AI/ML/DS)
2. Написать краткое саммари на русском языке (2-4 предложения), сохраняя ключевые факты и выводы

Ответь строго в формате JSON без markdown-обёртки:
{
  \"score\": <число от 1 до 10>,
  \"summary\": \"<краткое саммари на русском>\"
}

Критерии оценки:
- 9-10: Важные новости, прорывы, детальный технический контент
- 7-8: Полезный контент, обзоры, туториалы
- 5-6: Общая информация, косвенно связанная с AI/ML
- 1-4: Нерелевантный контент, реклама, спам"""


async def evaluate_and_summarize(text: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{config.OMNI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.OMNI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config.LLM_MODEL_SUMMARY,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text},
                    ],
                    "max_tokens": 512,
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()

        response_text = response.json()["choices"][0]["message"]["content"].strip()
        response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()

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
    except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse model response: {e}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"OmniRoute HTTP error: {e}")
        return None
