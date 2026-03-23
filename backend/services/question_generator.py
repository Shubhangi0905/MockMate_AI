from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.models.domain import GeneratedQuestion
from backend.services.llm import get_llm
from backend.services.prompt_loader import load_prompt


def generate_question(state: dict) -> GeneratedQuestion:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=GeneratedQuestion)
    template = load_prompt("question.txt")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | parser
    return chain.invoke(
        {
            "analysis": state.get("analysis", {}),
            "mode": state.get("mode", "quick"),
            "difficulty": state.get("difficulty", "easy"),
            "questions": state.get("questions", []),
            "answers": state.get("answers", []),
            "evaluations": state.get("evaluations", []),
            "question_index": state.get("question_index", 0),
            "max_questions": state.get("max_questions", 5),
            "format_instructions": parser.get_format_instructions(),
        }
    )

