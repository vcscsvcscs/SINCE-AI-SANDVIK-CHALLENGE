from os import environ
import json
import requests

# Featherless LLM config
FEATHERLESS_API_KEY = environ.get("FEATHERLESS_API_KEY")
FEATHERLESS_MODEL = environ.get(
    "FEATHERLESS_MODEL",
    "Qwen/Qwen2.5-7B-Instruct",  # разумный дефолт
)
FEATHERLESS_API_URL = "https://api.featherless.ai/v1/chat/completions"

def call_featherless_llm(user_prompt: str) -> str:
    """
    Low-level helper: call Featherless chat completions API and
    return raw assistant message content as string.
    """

    system_prompt = (
        "You are a classifier for a mining equipment spare parts support chat.\n"
        "Your job:\n"
        "1) Decide if the customer message is about a SPARE PART (part, tire, hose, mirror, transmission, etc.).\n"
        "2) If yes, extract the ONE most important term or phrase that names the part.\n\n"
        "Respond ONLY in JSON with the following keys:\n"
        "{\n"
        '  \"is_spare_part_related\": true/false,\n'
        '  \"spare_part_term\": string or null,\n'
        '  \"reason\": string (very short explanation)\n'
        "}\n"
        "Do not add any extra text, only JSON."
    )

    if not FEATHERLESS_API_KEY:
        # Without the key, there's no point in trying
        raise RuntimeError("FEATHERLESS_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": FEATHERLESS_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(
        FEATHERLESS_API_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    # Take the text of the first response
    return data["choices"][0]["message"]["content"]