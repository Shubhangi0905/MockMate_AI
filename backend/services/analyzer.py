from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.models.domain import AnalysisResult
from backend.services.llm import get_llm
from backend.services.prompt_loader import load_prompt


def analyze_resume(*, resume_text: str, jd_text: str | None) -> AnalysisResult:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=AnalysisResult)

    template = load_prompt("analyze.txt")
    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm | parser
    return chain.invoke(
        {
            "resume_text": resume_text,
            "jd_text": jd_text or "",
            "has_jd": bool(jd_text),
            "format_instructions": parser.get_format_instructions(),
        }
    )

