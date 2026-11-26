from typing import Literal

from pydantic import BaseModel, Field

from databricks_agent.agent.graph.state import AgentState, PartType


class PartIdentification(BaseModel):
    part_number: str | None = Field(
        default=None,
        description=(
            "The part number copied exactly from the question. "
            "Null when the question has no identifier."
        ),
    )
    part_type: Literal["assembly", "component", "model", "unknown"] = Field(
        description=(
            "A hint only. model is a product, component is a purchased "
            "part, assembly is a built assembly, unknown when unstated."
        ),
    )


class PartTypeGuess(BaseModel):
    part_type: Literal["assembly", "component", "model", "unknown"]


EXTRACT_PROMPT = """
You extract a part number from a Bill of Materials question.

Rules:
- Copy part_number exactly as written in the question.
- Do not correct spelling, insert hyphens, expand abbreviations, or invent an identifier.
- Use null for part_number when the question has no identifier.
- part_type is a hint: model (product), component (purchased part), assembly (built assembly), or unknown.
- The database decides the real type after an exact lookup.
"""

CLASSIFY_PROMPT = """
Classify this exact part number as model (product), component (purchased part),
assembly (built assembly), or unknown.

Use the question only as context. Do not change the part number.
"""


def identify_part(state: AgentState) -> dict:
    question = state["question"]
    retyped = (state.get("retyped_part_number") or "").strip()

    if retyped:
        return {
            "part_number": retyped,
            "part_type": _guess_type(question, retyped),
            "retyped_part_number": None,
            "part_exists": False,
            "usecase": None,
            "sql_query": None,
            "sql_parameters": [],
            "query_results": [],
            "answer": "",
            "error": None,
        }

    try:
        decision = _extract(question)
    except Exception as exc:  # noqa: BLE001 — model failures become an answer
        return {
            "part_number": None,
            "part_exists": False,
            "error": f"Could not identify the part number: {exc}",
        }

    part_number = _span_in_question(question, decision.part_number)
    if part_number is None:
        return {
            "part_number": None,
            "part_exists": False,
            "error": (
                "Type the part number as it appears on the part. "
                "I only look up an identifier that is written in the question."
            ),
        }

    return {
        "part_number": part_number,
        "part_type": _known_type(decision.part_type),
        "part_exists": False,
        "usecase": None,
        "sql_query": None,
        "sql_parameters": [],
        "query_results": [],
        "answer": "",
        "error": None,
    }


def _extract(question: str) -> PartIdentification:
    model = _structured_model(PartIdentification)
    decision = model.invoke(
        [
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": question},
        ]
    )
    if not isinstance(decision, PartIdentification):
        raise TypeError("Part identification did not return the expected schema.")
    return decision


def _guess_type(question: str, part_number: str) -> PartType | None:
    """Classify a number the user just typed. A model failure leaves the type to the database."""
    try:
        model = _structured_model(PartTypeGuess)
        decision = model.invoke(
            [
                {"role": "system", "content": CLASSIFY_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Part number: {part_number}\n\nQuestion:\n{question}"
                    ),
                },
            ]
        )
    except Exception:  # noqa: BLE001 — type guess is optional on a retyped number
        return None

    if not isinstance(decision, PartTypeGuess):
        return None
    return _known_type(decision.part_type)


def _structured_model(schema: type[BaseModel]):
    from databricks_agent.integrations.databricks.llm import create_chat_model

    return create_chat_model().with_structured_output(schema)


def _known_type(value: str) -> PartType | None:
    if value in {"assembly", "component", "model"}:
        return value
    return None


def _span_in_question(question: str, part_number: str | None) -> str | None:
    """Return the identifier using the exact characters from the question."""
    if not part_number or not part_number.strip():
        return None

    token = part_number.strip()
    folded_question = question.casefold()
    folded_token = token.casefold()
    if len(folded_question) != len(question) or len(folded_token) != len(token):
        return None

    start = 0
    while True:
        index = folded_question.find(folded_token, start)
        if index < 0:
            return None
        end = index + len(folded_token)
        before = index == 0 or not _in_part_number(question[index - 1])
        after = end == len(question) or not _in_part_number(question[end])
        if before and after:
            return question[index:end]
        start = index + 1


def _in_part_number(character: str) -> bool:
    return character.isalnum() or character in "-_./"
