from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class PdfDoc:
    filename: str
    title: str
    body: str


def _pdf_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_lines(text: str, width: int) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        if not raw.strip():
            out.append("")
            continue
        # Preserve bullet indentation reasonably
        indent = ""
        stripped = raw.lstrip()
        if raw.startswith("  "):
            indent = "  "
        if stripped.startswith(("-", "*")):
            indent = raw[: len(raw) - len(stripped)] + "  "
            raw = stripped[0] + " " + stripped[1:].lstrip()
        wrapped = textwrap.wrap(raw, width=width, subsequent_indent=indent, break_long_words=False)
        out.extend(wrapped if wrapped else [""])
    return out


def write_text_pdf(
    path: Path,
    *,
    title: str,
    body: str,
    page_size: tuple[int, int] = (595, 842),  # A4 in points
    margin: int = 48,
    font_size: int = 11,
    leading: int = 14,
    wrap_width_chars: int = 92,
) -> None:
    """
    Minimal PDF writer (no external deps). Supports multi-page, monospaced-ish layout.
    """
    width_pt, height_pt = page_size
    x = margin
    y_start = height_pt - margin
    max_lines = max(1, int((height_pt - margin * 2) / leading) - 2)  # reserve for title spacing

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"{title}\nGenerated: {now}\n\n"
    lines = _wrap_lines(header + body.strip() + "\n", width=wrap_width_chars)

    pages: list[list[str]] = []
    buf: list[str] = []
    for ln in lines:
        buf.append(ln)
        if len(buf) >= max_lines:
            pages.append(buf)
            buf = []
    if buf:
        pages.append(buf)

    def content_stream(page_lines: list[str]) -> bytes:
        # Use Helvetica. Draw text line-by-line using T* (next line).
        parts: list[str] = []
        parts.append("BT")
        parts.append(f"/F1 {font_size} Tf")
        parts.append(f"{leading} TL")
        parts.append(f"{x} {y_start} Td")
        for ln in page_lines:
            safe = _pdf_escape(ln)
            parts.append(f"({safe}) Tj")
            parts.append("T*")
        parts.append("ET")
        data = "\n".join(parts).encode("utf-8")
        return data

    objects: list[bytes] = []

    def add_obj(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    # 1) Catalog
    # 2) Pages
    # 3) Font
    # 4.. Page + content pairs
    font_obj = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_kids: list[int] = []
    content_objs: list[int] = []
    for page_lines in pages:
        stream = content_stream(page_lines)
        content = (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        content_id = add_obj(content)
        content_objs.append(content_id)

        page_dict = (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
            + str(width_pt).encode("ascii")
            + b" "
            + str(height_pt).encode("ascii")
            + b"] "
            + b"/Resources << /Font << /F1 "
            + str(font_obj).encode("ascii")
            + b" 0 R >> >> "
            + b"/Contents "
            + str(content_id).encode("ascii")
            + b" 0 R >>"
        )
        page_id = add_obj(page_dict)
        page_kids.append(page_id)

    kids_str = b" ".join([str(pid).encode("ascii") + b" 0 R" for pid in page_kids])
    pages_obj = b"<< /Type /Pages /Kids [" + kids_str + b"] /Count " + str(len(page_kids)).encode("ascii") + b" >>"
    # Insert Pages as object 2: if not at index 1, we need to place it. We'll build with placeholders.
    # We'll rebuild objects with fixed numbering for catalog/pages/font and appended rest.
    # Layout:
    # 1 catalog
    # 2 pages
    # 3 font
    # 4.. content/page...
    rest = objects[1:]  # everything after font_obj currently at index 0
    objects = []
    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")  # 1
    add_obj(pages_obj)  # 2
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")  # 3
    # Re-add rest with corrected references:
    # content streams are fine, pages refer to parent 2, font ref should be 3.
    # We need to regenerate page dicts with correct content ids after renumber.
    objects = objects[:3]

    # Map old content objs/pages to new ids by regenerating in order
    new_page_ids: list[int] = []
    new_content_ids: list[int] = []
    for page_lines in pages:
        stream = content_stream(page_lines)
        content = (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        content_id = add_obj(content)
        new_content_ids.append(content_id)

        page_dict = (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
            + str(width_pt).encode("ascii")
            + b" "
            + str(height_pt).encode("ascii")
            + b"] "
            + b"/Resources << /Font << /F1 3 0 R >> >> "
            + b"/Contents "
            + str(content_id).encode("ascii")
            + b" 0 R >>"
        )
        page_id = add_obj(page_dict)
        new_page_ids.append(page_id)

    # Update Pages object (2) with correct kids list
    kids_str = b" ".join([str(pid).encode("ascii") + b" 0 R" for pid in new_page_ids])
    objects[1] = (
        b"<< /Type /Pages /Kids [" + kids_str + b"] /Count " + str(len(new_page_ids)).encode("ascii") + b" >>"
    )

    # Write file with xref
    out = bytearray()
    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = [0]

    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_offset = len(out)
    out.extend(b"xref\n")
    out.extend(f"0 {len(objects)+1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    out.extend(b"trailer\n")
    out.extend(f"<< /Size {len(objects)+1} /Root 1 0 R >>\n".encode("ascii"))
    out.extend(b"startxref\n")
    out.extend(f"{xref_offset}\n".encode("ascii"))
    out.extend(b"%%EOF\n")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def build_docs() -> list[PdfDoc]:
    body_common = """
This documentation is generated for the MockMate AI project (FastAPI + LangGraph + LangChain + LLM).
It explains the workflow, components, and how the agentic loop is implemented.
"""

    workflow = f"""
{body_common}

1) High-level workflow

  START
    |
    v
  Upload Resume (+ optional JD)
    |
    v
  Analyze (LLM):
    - Extract skills + experience summary
    - If JD exists: match score + missing skills
    - Else: infer role + strong/weak skills
    |
    v
  Interview Loop (LangGraph):
    - Generate ONE question (LLM)
    - User answers
    - Evaluate answer (LLM): score 0–10 + feedback + improvement tip
    - Adaptive decision:
        * score >= 8  -> increase difficulty
        * score 5–7   -> keep difficulty
        * score < 5   -> decrease difficulty
    - Repeat until N questions done
    |
    v
  Final Report (LLM):
    - overall_score 0–100
    - strengths / weaknesses / suggestions / verdict
    |
    v
  END

2) Why LangGraph
LangGraph provides a state machine / graph execution model so the interview can:
- keep structured state across steps
- loop deterministically
- separate responsibilities into nodes (question/evaluate/decision/report)
"""

    tech = f"""
{body_common}

Tech stack

Backend
- Python 3.10+
- FastAPI: HTTP API endpoints and request/response validation
- Pydantic: domain schemas for analysis/question/evaluation/report outputs
- LangChain: LLM wrapper + prompt templates + structured output parsing
- LangGraph: stateful orchestration of the interview loop
- Provider adapters:
    * OpenAI via langchain-openai
    * Gemini via langchain-google-genai

Frontend
- Vue 3 + Vite
- Vue Router: multi-page dashboard
- pdfjs-dist: extract text from uploaded PDF resume/JD (client-side)
- jsPDF: generate a downloadable PDF report (client-side)

Runtime configuration
- .env files control provider selection and model names
  - LLM_PROVIDER=openai|gemini
  - OPENAI_API_KEY / GOOGLE_API_KEY
"""

    llm = f"""
{body_common}

How the LLM is used

There are four core LLM tasks, each with its own prompt template and strict JSON schema:

1) Analyzer (resume + optional JD)
- Prompt: backend/prompts/analyze.txt
- Output schema: AnalysisResult

2) Question Generator (one at a time)
- Prompt: backend/prompts/question.txt
- Output schema: GeneratedQuestion
- Inputs include:
    - analysis (skills/gaps)
    - current difficulty + mode
    - previous questions/answers/evaluations (to avoid repeats)

3) Evaluation Engine
- Prompt: backend/prompts/evaluate.txt
- Output schema: EvaluationResult (score 0–10, feedback, improvement_tip)

4) Report Generator
- Prompt: backend/prompts/report.txt
- Output schema: FinalReport (overall_score, strengths, weaknesses, suggestions, verdict)

Structured outputs
All LLM calls use a Pydantic parser to enforce JSON shape. This reduces UI breakage and makes state updates predictable.

Rate limiting / quota
Provider 429 errors are mapped to HTTP 429 so the frontend can show a user-friendly message with a retry delay when available.
"""

    agentic = f"""
{body_common}

How the agentic interview works

Agentic behavior in this MVP comes from:
1) Stateful memory:
   - questions asked
   - answers given
   - evaluation scores + feedback
   - current difficulty, interview mode, question index

2) Tool-like steps (nodes):
   - analyze_node: ensure analysis exists
   - question_node: produce next tailored question
   - answer_node: append user answer into memory
   - evaluate_node: score the answer + coaching feedback
   - decision_node: change difficulty and decide loop/end
   - report_node: create final report

3) Deterministic control logic:
   - difficulty changes follow a fixed rule based on score
   - loop continues until max_questions is reached

What this project is NOT (yet)
- Classic RAG (Retrieval Augmented Generation):
  There is no vector database, embeddings, or retrieval step in this MVP.
  The model uses the resume/JD text + accumulated interview history as context.

How to add real RAG (next step)
- Chunk resume/JD into passages
- Create embeddings and store in a vector index (FAISS/Chroma/etc.)
- Retrieve relevant chunks per node (question/evaluate/report) and inject them into prompts
"""

    api = f"""
{body_common}

API overview (MVP)

POST /upload
- Input: resume_text, jd_text (optional)
- Output: session_id

POST /analyze
- Input: session_id (or resume_text)
- Output: analysis JSON

POST /start-interview
- Input: session_id, mode, difficulty, max_questions
- Output: first question

POST /submit-answer
- Input: session_id, answer
- Output:
    - evaluation (internal)
    - next_question (if interview continues)
    - done/report_ready flags

GET /report?session_id=...
- Output: final report JSON

State and persistence
- Sessions are stored in memory on the backend. If the backend restarts, session_ids become invalid.
"""

    return [
        PdfDoc("01_workflow.pdf", "MockMate AI — Workflow", workflow),
        PdfDoc("02_tech_stack.pdf", "MockMate AI — Tech Stack", tech),
        PdfDoc("03_llm_usage.pdf", "MockMate AI — LLM Usage", llm),
        PdfDoc("04_agentic_ai.pdf", "MockMate AI — Agentic AI", agentic),
        PdfDoc("05_api_and_state.pdf", "MockMate AI — API & State", api),
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "docs" / "pdfs"
    docs = build_docs()
    for d in docs:
        write_text_pdf(out_dir / d.filename, title=d.title, body=d.body)
    print(f"Generated {len(docs)} PDFs into: {out_dir}")


if __name__ == "__main__":
    main()

