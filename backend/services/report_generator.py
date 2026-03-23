from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.models.domain import FinalReport
from backend.services.llm import get_llm
from backend.services.prompt_loader import load_prompt


def generate_report(state: dict) -> FinalReport:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=FinalReport)
    template = load_prompt("report.txt")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | parser
    return chain.invoke(
        {
            "analysis": state.get("analysis", {}),
            "questions": state.get("questions", []),
            "answers": state.get("answers", []),
            "evaluations": state.get("evaluations", []),
            "format_instructions": parser.get_format_instructions(),
        }
    )

