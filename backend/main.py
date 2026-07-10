from fastapi import FastAPI
from pydantic import BaseModel

from github_service import analyze_repository

app = FastAPI()


class AnalyzeRequest(BaseModel):
    github_url: str
    mission: str


@app.get("/")
def root():
    return {"status": "RampUp backend is running"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    repository = analyze_repository(request.github_url)
    return {
        "github_url": request.github_url,
        "mission": request.mission,
        "repository": repository,
    }
