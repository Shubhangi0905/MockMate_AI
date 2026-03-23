from fastapi import APIRouter, HTTPException

from backend.graph.runner import run_graph_step
from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    NextQuestionRequest,
    QuestionResponse,
    ReportResponse,
    StartInterviewRequest,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    UploadRequest,
    UploadResponse,
)
from backend.services.analyzer import analyze_resume
from backend.services.llm_errors import map_llm_exception
from backend.services.store import store

router = APIRouter()


def _get_session(session_id: str):
    try:
        return store.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown session_id") from None


@router.post("/upload", response_model=UploadResponse)
def upload(payload: UploadRequest) -> UploadResponse:
    session_id = store.create_session(resume_text=payload.resume_text, jd_text=payload.jd_text)
    return UploadResponse(session_id=session_id)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        session = store.get_or_create_session(
            session_id=payload.session_id,
            resume_text=payload.resume_text,
            jd_text=payload.jd_text,
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    try:
        analysis = analyze_resume(resume_text=session.resume_text, jd_text=session.jd_text)
    except Exception as e:
        mapped = map_llm_exception(e)
        if mapped:
            raise HTTPException(
                status_code=mapped.status_code,
                detail=mapped.detail,
                headers=mapped.headers or {},
            ) from None
        raise
    session.analysis = analysis
    store.save_session(session)
    return AnalyzeResponse(session_id=session.session_id, analysis=analysis)


@router.post("/start-interview", response_model=QuestionResponse)
def start_interview(payload: StartInterviewRequest) -> QuestionResponse:
    session = _get_session(payload.session_id)

    session.state = store.new_interview_state(
        resume_text=session.resume_text,
        jd_text=session.jd_text,
        analysis=session.analysis.model_dump() if session.analysis else None,
        mode=payload.mode,
        difficulty=payload.difficulty,
        max_questions=payload.max_questions,
    )
    session.report = None

    session.state["next_action"] = "ask"
    try:
        session.state = run_graph_step(session.state)
    except Exception as e:
        mapped = map_llm_exception(e)
        if mapped:
            raise HTTPException(
                status_code=mapped.status_code,
                detail=mapped.detail,
                headers=mapped.headers or {},
            ) from None
        raise
    store.save_session(session)

    if not session.state.get("current_question"):
        raise HTTPException(status_code=500, detail="Failed to generate the first question.")

    return QuestionResponse.from_state(session.session_id, session.state)


@router.post("/next-question", response_model=QuestionResponse)
def next_question(payload: NextQuestionRequest) -> QuestionResponse:
    session = _get_session(payload.session_id)
    if session.state is None:
        raise HTTPException(status_code=400, detail="Start an interview first via /start-interview.")

    if session.state.get("next_action") == "await_answer" and session.state.get("current_question"):
        return QuestionResponse.from_state(session.session_id, session.state)

    session.state["next_action"] = "ask"
    try:
        session.state = run_graph_step(session.state)
    except Exception as e:
        mapped = map_llm_exception(e)
        if mapped:
            raise HTTPException(
                status_code=mapped.status_code,
                detail=mapped.detail,
                headers=mapped.headers or {},
            ) from None
        raise
    store.save_session(session)

    if not session.state.get("current_question"):
        raise HTTPException(status_code=500, detail="Failed to generate the next question.")

    return QuestionResponse.from_state(session.session_id, session.state)


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest) -> SubmitAnswerResponse:
    session = _get_session(payload.session_id)
    if session.state is None:
        raise HTTPException(status_code=400, detail="Start an interview first via /start-interview.")

    if session.state.get("next_action") != "await_answer":
        raise HTTPException(status_code=400, detail="No question is awaiting an answer right now.")

    session.state["pending_answer"] = payload.answer
    session.state["next_action"] = "answer"
    try:
        session.state = run_graph_step(session.state)
    except Exception as e:
        mapped = map_llm_exception(e)
        if mapped:
            raise HTTPException(
                status_code=mapped.status_code,
                detail=mapped.detail,
                headers=mapped.headers or {},
            ) from None
        raise
    store.save_session(session)

    last_eval = None
    if session.state.get("evaluations"):
        last_eval = session.state["evaluations"][-1]

    next_q = None
    if session.state.get("next_action") == "await_answer":
        next_q = session.state.get("current_question")

    report_ready = bool(session.state.get("report"))
    if report_ready:
        session.report = session.state["report"]
        store.save_session(session)

    return SubmitAnswerResponse(
        session_id=session.session_id,
        evaluation=last_eval,
        next_question=next_q,
        done=bool(session.state.get("done")),
        report_ready=report_ready,
        difficulty=session.state.get("difficulty", "easy"),
        question_index=int(session.state.get("question_index", 0)),
        max_questions=int(session.state.get("max_questions", 0)),
    )


@router.get("/report", response_model=ReportResponse)
def report(session_id: str) -> ReportResponse:
    session = _get_session(session_id)
    if session.report is None:
        raise HTTPException(status_code=404, detail="Report not ready. Finish the interview first.")
    return ReportResponse(session_id=session.session_id, report=session.report)
