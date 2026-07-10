from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_service import generate_ai_brief
from github_service import analyze_repository_complete

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
    repository, repository_summary = analyze_repository_complete(request.github_url)
    rampup_brief = generate_ai_brief(
        repository_summary,
        request.role,
        request.mission,
    )
    return {
        "github_url": request.github_url,
        "role": request.role,
        "mission": request.mission,
        "repository": repository,
        "rampup_brief": rampup_brief,
    }
