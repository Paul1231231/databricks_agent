import json

from agent.graph.state import AgentState
from integrations.databricks.llm import create_chat_model


ANSWER_PROMPT = """
You are a Bill of Material database assistant.

Answer only from the provided Databricks query results.

Rules:
- Never invent a part, assembly, quantity, unit, date, or relationship.
- Preserve identifiers exactly.
- If the query returns no rows, say that no matching record was found.
- If an error is provided, explain it briefly.
- For BOM children, list component ID, description, quantity, and unit.
- For where-used questions, list the parent assemblies.
- Mention if the result may have been truncated by a query limit.
- Keep the response concise and factual.
"""


def response_generation(state: AgentState) -> dict:
    if state.get("error"):
        return {
            "answer": state["error"],
        }

    results = state.get("query_results", [])

    if not results:
        return {
            "answer": (
                f"No matching record was found for "
                f"{state.get('item_id', 'the requested item')}."
            )
        }

    evidence = {
        "intent": state.get("intent"),
        "item_id": state.get("item_id"),
        "row_count": len(results),
        "rows": results,
    }

    model = create_chat_model()

    response = model.invoke(
        [
            {
                "role": "system",
                "content": ANSWER_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{state['question']}\n\n"
                    f"Databricks evidence:\n"
                    f"{json.dumps(evidence, indent=2, default=str)}"
                ),
            },
        ]
    )

    return {
        "answer": response.content,
    }