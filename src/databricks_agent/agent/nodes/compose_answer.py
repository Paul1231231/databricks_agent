import json

from databricks_agent.agent.graph.state import AgentState

ANSWER_PROMPT = """
You are a Bill of Materials assistant.

Answer only from the Databricks rows in the evidence.

Rules:
- Never invent a part, customer, supplier, quantity, date, or relationship.
- Preserve part numbers exactly.
- If the rows are empty, say that no matching record was found.
- Keep the response concise and factual.
"""

MAX_ROWS_IN_PROMPT = 50


def compose_answer(state: AgentState) -> dict:
    if state.get("answer"):
        return {"answer": state["answer"]}

    if state.get("error"):
        return {"answer": state["error"]}

    results = state.get("query_results") or []
    part_number = state.get("part_number") or "the requested part"
    usecase = (state.get("usecase") or "query").replace("_", " ")

    if not results:
        return {
            "answer": f"No matching record was found for {part_number} ({usecase})."
        }

    shown = results[:MAX_ROWS_IN_PROMPT]
    omitted = len(results) - len(shown)
    try:
        prose = _from_model(state, shown, omitted)
    except Exception:  # noqa: BLE001 — a model failure falls back to the rows
        prose = _plain(part_number, usecase, shown, omitted)

    return {"answer": prose}


def _from_model(state: AgentState, rows: list, omitted: int) -> str:
    from databricks_agent.integrations.databricks.llm import create_chat_model

    evidence = {
        "usecase": state.get("usecase"),
        "part_number": state.get("part_number"),
        "part_type": state.get("part_type"),
        "row_count": len(state.get("query_results") or []),
        "rows_omitted_from_prompt": omitted,
        "rows": rows,
    }
    response = create_chat_model().invoke(
        [
            {"role": "system", "content": ANSWER_PROMPT},
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
    content = response.content
    if isinstance(content, str):
        return content
    return json.dumps(content, default=str)


def _plain(part_number: str, usecase: str, rows: list, omitted: int) -> str:
    lines = [
        f"{usecase} for {part_number}: {len(rows) + omitted} row(s).",
    ]
    for row in rows:
        lines.append(json.dumps(row, default=str))
    if omitted:
        lines.append(f"{omitted} further row(s) omitted.")
    return "\n".join(lines)
