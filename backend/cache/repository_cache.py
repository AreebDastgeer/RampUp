import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent / "data"
TTL = timedelta(hours=1)


def _cache_key(github_url: str) -> str:
    return hashlib.sha256(github_url.encode("utf-8")).hexdigest()


def _cache_path(github_url: str) -> Path:
    return CACHE_DIR / f"{_cache_key(github_url)}.json"


def get_cached_analysis(github_url: str) -> tuple[dict, str] | None:
    print("Checking cache...")
    path = _cache_path(github_url)
    print(path)
    
    if not path.exists():
        logger.info("Cache miss")
        print("CACHE MISS")
        return None
    print("CACHE FILE FOUND")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        expires_at = datetime.fromisoformat(data["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) >= expires_at:
            logger.info("Cache miss")
            print("CACHE MISS")
            path.unlink(missing_ok=True)
            return None

        logger.info("Cache hit")
        print("CACHE HIT")
        return data["repository"], data["repository_summary"]
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        logger.info("Cache miss")
        print("CACHE MISS")
        path.unlink(missing_ok=True)
        return None


def set_cached_analysis(
    github_url: str,
    repository: dict,
    repository_summary: str,
) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    payload = {
        "github_url": github_url,
        "created_at": now.isoformat(),
        "expires_at": (now + TTL).isoformat(),
        "repository": repository,
        "repository_summary": repository_summary,
    }

    path = _cache_path(github_url)
    temp_path = path.with_suffix(".tmp")
    try:
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        temp_path.replace(path)
    except OSError as exc:
        logger.warning("Failed to write cache: %s", exc)
        temp_path.unlink(missing_ok=True)
