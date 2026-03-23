from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["easy", "medium", "hard"]
Mode = Literal["quick", "full", "weak"]


class AnalysisResult(BaseModel):
    inferred_role: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_summary: list[str] = Field(default_factory=list)

    match_score: int | None = Field(default=None, ge=0, le=100)
    missing_skills: list[str] | None = None

    strong_skills: list[str] | None = None
    weak_skills: list[str] | None = None


class GeneratedQuestion(BaseModel):
    question: str
    skill_focus: str | None = None
    difficulty: Difficulty = "easy"


class EvaluationResult(BaseModel):
    score: int = Field(ge=0, le=10)
    feedback: str
    improvement_tip: str


class FinalReport(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    verdict: str

