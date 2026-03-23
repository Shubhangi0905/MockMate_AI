from __future__ import annotations

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.models.domain import EvaluationResult
from backend.services.llm import get_llm
from backend.services.prompt_loader import load_prompt


def evaluate_answer(*, question: str, answer: str, difficulty: str) -> EvaluationResult:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    template = load_prompt("evaluate.txt")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | parser
    return chain.invoke(
        {
            "question": question,
            "answer": answer,
            "difficulty": difficulty,
            "format_instructions": parser.get_format_instructions(),
        }
    )

