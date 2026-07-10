import json
import os
import re
import urllib.error
import urllib.request

from dotenv import load_dotenv

from prompts import RAMPUP_SYSTEM_PROMPT

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL")
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"


def _parse_json_response(content: str) -> dict | None:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def generate_ai_brief(
    repository_summary: str,
    role: str,
    mission: str,
) -> dict | None:
    if not FIREWORKS_API_KEY or not FIREWORKS_MODEL:
        return None

    payload = {
        "model": FIREWORKS_MODEL,
        "messages": [
            {"role": "system", "content": RAMPUP_SYSTEM_PROMPT},
            {"role": "user", "content": f"Repository Summary:\n{repository_summary}"},
            {"role": "user", "content": f"Developer Role:\n{role}"},
            {"role": "user", "content": f"Mission:\n{mission}"},
        ],
        "temperature": 0.2,
    }

    try:
        request = urllib.request.Request(
            FIREWORKS_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {FIREWORKS_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))

        content = body["choices"][0]["message"]["content"]
        return _parse_json_response(content)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError, TypeError):
        return None
