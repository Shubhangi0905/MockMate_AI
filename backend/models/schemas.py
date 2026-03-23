from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.models.domain import AnalysisResult, Difficulty, Mode


class UploadRequest(BaseModel):
    resume_text: str = Field(min_length=20)
    jd_text: str | None = None


class UploadResponse(BaseModel):
    session_id: str


class AnalyzeRequest(BaseModel):
    session_id: str | None = None
    resume_text: str | None = None
    jd_text: str | None = None


class AnalyzeResponse(BaseModel):
    session_id: str
    analysis: AnalysisResult


class StartInterviewRequest(BaseModel):
    session_id: str
    mode: Mode = "quick"
    difficulty: Difficulty = "easy"
    max_questions: int = Field(default=5, ge=1, le=50)


class NextQuestionRequest(BaseModel):
    session_id: str


class QuestionResponse(BaseModel):
    session_id: str
    question: str
    difficulty: Difficulty
    question_index: int
    max_questions: int

    @classmethod
    def from_state(cls, session_id: str, state: dict) -> "QuestionResponse":
        return cls(
            session_id=session_id,
            question=str(state.get("current_question") or ""),
            difficulty=state.get("difficulty", "easy"),
            question_index=int(state.get("question_index", 0)),
            max_questions=int(state.get("max_questions", 0)),
        )


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(min_length=1)


class SubmitAnswerResponse(BaseModel):
    session_id: str
    evaluation: dict[str, Any] | None
    next_question: str | None
    done: bool
    report_ready: bool
    difficulty: Difficulty
    question_index: int
    max_questions: int


class ReportResponse(BaseModel):
    session_id: str
    report: dict[str, Any]

