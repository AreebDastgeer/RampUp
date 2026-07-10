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
FIREWORKS_MAX_TOKENS = int(os.getenv("FIREWORKS_MAX_TOKENS", "800"))


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

def build_user_prompt(repository_summary, role, mission):
    return f"""
You are preparing an onboarding brief for a developer.

===== REPOSITORY SUMMARY =====

{repository_summary}

===== END REPOSITORY SUMMARY =====

===== DEVELOPER ROLE =====

--------------
{role}

===== MISSION =====

-------
{mission}

Generate the onboarding brief using only the repository information provided.
"""

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
            {"role": "user", "content": build_user_prompt(repository_summary, role, mission)},
        ],
        "reasoning_effort": "none",
        "max_tokens": FIREWORKS_MAX_TOKENS,
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
        print("\n========== FIREWORKS FINISH REASON ==========")
        print(body["choices"][0]["finish_reason"])
        print("===========================================\n")
        return _parse_json_response(content)
    except Exception as e:
        print("\n========== FIREWORKS ERROR ==========")
        print(type(e).__name__)
        print(e)

        if isinstance(e, urllib.error.HTTPError):
            print(e.read().decode())

        print("=====================================\n")

        return None
    # except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError, TypeError):
    #     return None
