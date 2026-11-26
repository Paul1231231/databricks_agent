from typing import Literal

from pydantic import BaseModel, Field

from databricks_agent.agent.graph.state import (
    USECASES_BY_PART_TYPE,
    AgentState,
    Usecase,
)


class UsecaseDecision(BaseModel):
    usecase: Literal[
        "bom_explosion",
        "customer_impact",
        "model_impact",
        "component_impact",
        "supplier_impact",
        "unsupported",
    ] = Field(
        description="The single fixed analysis that answers the question, or unsupported."
    )


USECASE_DESCRIPTIONS: dict[Usecase, str] = {
    "bom_explosion": "Explode the BOM for this model.",
    "customer_impact": "Report the customer impact of this model.",
    "model_impact": "Report the model impact of this model.",
    "component_impact": "Report the impact of this purchased component.",
    "supplier_impact": "Report the supplier impact of this purchased component.",
}


def match_usecase(state: AgentState) -> dict:
    part_type = state.get("part_type")
    part_number = state.get("part_number") or "this part"
    allowed = USECASES_BY_PART_TYPE.get(part_type, ())

    if not allowed:
        kind = part_type or "unknown part"
        return {
            "usecase": None,
            "error": (
                f"{part_number} is a {kind}. "
                "No fixed query is registered for that part type."
            ),
        }

    try:
        decision = _choose(state["question"], part_number, part_type, allowed)
    except Exception as exc:  # noqa: BLE001 — model failures become an answer
        return {
            "usecase": None,
            "error": f"Could not match the question to a query: {exc}",
        }

    if decision.usecase not in allowed:
        return {
            "usecase": None,
            "error": _unsupported_message(part_type, part_number, allowed),
        }

    return {
        "usecase": decision.usecase,
        "error": None,
    }


def _choose(question: str, part_number: str, part_type: str, allowed: tuple[Usecase, ...]):
    from databricks_agent.integrations.databricks.llm import create_chat_model

    listed = "\n".join(
        f"- {name}: {USECASE_DESCRIPTIONS[name]}" for name in allowed
    )
    prompt = f"""
You match one Bill of Materials question to exactly one fixed query.

The part {part_number} is a {part_type}.
The only allowed queries are:
{listed}

Choose unsupported when none of them answer the question.
Do not invent a query outside that list.
"""
    model = create_chat_model().with_structured_output(UsecaseDecision)
    decision = model.invoke(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ]
    )
    if not isinstance(decision, UsecaseDecision):
        raise TypeError("Use-case matching did not return the expected schema.")
    return decision


def _unsupported_message(
    part_type: str,
    part_number: str,
    allowed: tuple[Usecase, ...],
) -> str:
    names = ", ".join(name.replace("_", " ") for name in allowed)
    return f"{part_number} is a {part_type}. Ask about: {names}."
