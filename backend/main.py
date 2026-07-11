import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_service import generate_ai_brief
from github_service import analyze_repository_complete

GITHUB_URL_PATTERN = re.compile(
    r"^https?://(www\.)?github\.com/[\w.-]+/[\w.-]+/?(\?.*)?$",
    re.IGNORECASE,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    github_url: str
    role: str
    mission: str


@app.get("/")
def root():
    return {"status": "RampUp backend is running"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    github_url = request.github_url.strip()
    role = request.role.strip()
    mission = request.mission.strip()

    if not github_url or not role or not mission:
        raise HTTPException(
            status_code=400,
            detail="GitHub URL, role, and mission are all required.",
        )

    if not GITHUB_URL_PATTERN.match(github_url):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid GitHub repository URL. "
                "Use the format: https://github.com/owner/repository"
            ),
        )

    try:
        repository, repository_summary = analyze_repository_complete(github_url)
    except Exception as exc:
        message = str(exc).strip() or "Unknown error"
        lowered = message.lower()
        if "not found" in lowered or "404" in lowered:
            detail = (
                "Repository not found. Check that the URL is correct and the repo is public."
            )
        elif "authentication" in lowered or "permission" in lowered:
            detail = (
                "Unable to access this repository. It may be private or require authentication."
            )
        elif "timed out" in lowered or "timeout" in lowered:
            detail = "Cloning the repository timed out. Try again or use a smaller repository."
        else:
            detail = f"Failed to analyze repository: {message}"
        raise HTTPException(status_code=422, detail=detail) from exc

    rampup_brief = generate_ai_brief(repository_summary, role, mission)

    return {
        "github_url": github_url,
        "role": role,
        "mission": mission,
        "repository": repository,
        "rampup_brief": rampup_brief,
    }
