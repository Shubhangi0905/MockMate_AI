from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.services.analyzer import analyze_resume
from backend.services.evaluator import evaluate_answer
from backend.services.question_generator import generate_question
from backend.services.report_generator import generate_report


def _adjust_difficulty(current: str, score: int) -> str:
    order = ["easy", "medium", "hard"]
    idx = order.index(current) if current in order else 0
    if score >= 8 and idx < 2:
        return order[idx + 1]
    if score < 5 and idx > 0:
        return order[idx - 1]
    return order[idx]


def analyze_node(state: dict) -> dict:
    if not state.get("analysis"):
        analysis = analyze_resume(resume_text=state.get("resume_text", ""), jd_text=state.get("jd_text"))
        state["analysis"] = analysis.model_dump()
    return state


def question_node(state: dict) -> dict:
    q = generate_question(state)
    state.setdefault("questions", []).append(q.question)
    state["question_index"] = len(state.get("questions") or [])
    state["current_question"] = q.question
    state["difficulty"] = q.difficulty
    state["pending_answer"] = None
    state["next_action"] = "await_answer"
    return state


def answer_node(state: dict) -> dict:
    answer = state.get("pending_answer")
    if not answer:
        state["next_action"] = "await_answer"
        return state
    state.setdefault("answers", []).append(answer)
    return state


def evaluate_node(state: dict) -> dict:
    questions = state.get("questions") or []
    answers = state.get("answers") or []
    if not questions or not answers:
        return state
    result = evaluate_answer(
        question=questions[-1],
        answer=answers[-1],
        difficulty=state.get("difficulty", "easy"),
    )
    state.setdefault("evaluations", []).append(result.model_dump())
    return state


def decision_node(state: dict) -> dict:
    evals = state.get("evaluations") or []
    last_score = int(evals[-1]["score"]) if evals else 0

    state["difficulty"] = _adjust_difficulty(state.get("difficulty", "easy"), last_score)

    if int(state.get("question_index", 0)) >= int(state.get("max_questions", 0)):
        state["done"] = True
        state["next_action"] = "report"
    else:
        state["done"] = False
        state["next_action"] = "ask"
    return state


def report_node(state: dict) -> dict:
    report = generate_report(state)
    state["report"] = report.model_dump()
    state["done"] = True
    state["next_action"] = "report_ready"
    return state


def _route_after_analyze(state: dict) -> str:
    action = state.get("next_action") or "ask"
    if action in {"ask", "start"}:
        return "question_node"
    if action == "answer":
        return "answer_node"
    if action in {"report", "report_ready"}:
        return "report_node"
    return END


def _route_after_decision(state: dict) -> str:
    if state.get("done") or state.get("next_action") in {"report", "report_ready"}:
        return "report_node"
    return "question_node"


def build_graph():
    g = StateGraph(dict)
    g.add_node("analyze_node", analyze_node)
    g.add_node("question_node", question_node)
    g.add_node("answer_node", answer_node)
    g.add_node("evaluate_node", evaluate_node)
    g.add_node("decision_node", decision_node)
    g.add_node("report_node", report_node)

    g.add_edge(START, "analyze_node")
    g.add_conditional_edges("analyze_node", _route_after_analyze)

    g.add_edge("question_node", END)

    g.add_edge("answer_node", "evaluate_node")
    g.add_edge("evaluate_node", "decision_node")
    g.add_conditional_edges("decision_node", _route_after_decision)

    g.add_edge("report_node", END)
    return g.compile()
