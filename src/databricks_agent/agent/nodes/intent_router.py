from typing import Literal

from pydantic import BaseModel, Field

from agent.graph.state import AgentState
from integrations.databricks.llm import create_chat_model


class RouteDecision(BaseModel):
    intent: Literal[
        "bom_children",
        "where_used",
        "component_details",
        "unsupported",
    ]

    item_id: str | None = Field(
        default=None,
        description=(
            "The exact assembly, BOM, part, or component identifier "
            "from the user question."
        ),
    )


ROUTER_PROMPT = """
You route questions for a Bill of Material assistant.

Available intents:

bom_children:
The user asks which components belong to an assembly or BOM.

where_used:
The user asks which assemblies, products, or BOMs use a component.

component_details:
The user asks for descriptive information about one component or item.

unsupported:
The question cannot be answered through the available BOM database queries.

Extract the exact item identifier when it is present.
Do not rewrite, correct, guess, or invent an identifier.
"""


def intent_router(state: AgentState) -> dict:
    model = create_chat_model()
    structured_model = model.with_structured_output(RouteDecision)

    decision = structured_model.invoke(
        [
            {
                "role": "system",
                "content": ROUTER_PROMPT,
            },
            {
                "role": "user",
                "content": state["question"],
            },
        ]
    )

    return {
        "intent": decision.intent,
        "item_id": decision.item_id,
        "error": None,
    }