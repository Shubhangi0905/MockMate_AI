from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from backend.models.domain import AnalysisResult


@dataclass
class Session:
    session_id: str
    resume_text: str
    jd_text: str | None
    analysis: AnalysisResult | None = None
    state: dict | None = None
    report: dict | None = None


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self._sessions: dict[str, Session] = {}

    def create_session(self, *, resume_text: str, jd_text: str | None) -> str:
        with self._lock:
            session_id = str(uuid4())
            self._sessions[session_id] = Session(
                session_id=session_id, resume_text=resume_text, jd_text=jd_text
            )
            return session_id

    def get_session(self, session_id: str) -> Session:
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError("Unknown session_id")
            return self._sessions[session_id]

    def save_session(self, session: Session) -> None:
        with self._lock:
            self._sessions[session.session_id] = session

    def get_or_create_session(
        self,
        *,
        session_id: str | None,
        resume_text: str | None,
        jd_text: str | None,
    ) -> Session:
        if session_id:
            try:
                return self.get_session(session_id)
            except KeyError:
                raise KeyError("Unknown session_id") from None

        if not resume_text:
            raise ValueError("resume_text is required when session_id is not provided")

        new_id = self.create_session(resume_text=resume_text, jd_text=jd_text)
        return self.get_session(new_id)

    def new_interview_state(
        self,
        *,
        resume_text: str,
        jd_text: str | None,
        analysis: dict,
        mode: str,
        difficulty: str,
        max_questions: int,
    ) -> dict:
        return {
            "resume_text": resume_text,
            "jd_text": jd_text,
            "analysis": analysis,
            "mode": mode,
            "difficulty": difficulty,
            "max_questions": max_questions,
            "question_index": 0,
            "questions": [],
            "answers": [],
            "evaluations": [],
            "current_question": None,
            "pending_answer": None,
            "next_action": "ask",
            "done": False,
            "report": None,
        }


store = InMemoryStore()

