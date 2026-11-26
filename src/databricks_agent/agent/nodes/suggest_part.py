from typing import Any

from databricks_agent.agent.graph.state import AgentState, PartType

# Fully qualified Databricks Vector Search index. Empty skips suggestions.
VECTOR_INDEX = ""

MAX_PART_ATTEMPTS = 3


def suggest_part(state: AgentState) -> dict:
    attempts = state.get("part_attempts", 0) + 1
    part_number = state.get("part_number") or ""
    try:
        matches = search_similar_parts(part_number, state.get("part_type"))
    except NotImplementedError as exc:
        matches = []
        message = f"{_message(part_number, matches)}\n{exc}"
    else:
        message = _message(part_number, matches)

    if attempts >= MAX_PART_ATTEMPTS:
        return {
            "part_attempts": attempts,
            "suggested_parts": matches,
            "retyped_part_number": None,
            "answer": (
                f"{message}\n"
                "The part number is still unknown. Start again with the exact number."
            ),
        }

    try:
        typed = read_reply(message)
    except EOFError:
        typed = ""

    if not typed:
        return {
            "part_attempts": attempts,
            "suggested_parts": matches,
            "retyped_part_number": None,
            "answer": f"{message}\nNo part number was entered.",
        }

    return {
        "part_attempts": attempts,
        "suggested_parts": matches,
        "retyped_part_number": typed,
        "part_exists": False,
        "usecase": None,
        "sql_query": None,
        "sql_parameters": [],
        "query_results": [],
        "answer": "",
        "error": None,
    }


def search_similar_parts(
    part_number: str,
    part_type: PartType | None,
) -> list[dict[str, Any]]:
    """Closest part numbers for a value that missed the exact lookup.

    Each hit should include part_number, part_type, and score.
    Wire this to the vector index named by VECTOR_INDEX. Until that index
    is set, the node still asks the user to type the number again.
    """
    if not part_number or not VECTOR_INDEX:
        return []
    raise NotImplementedError(
        f"Vector index {VECTOR_INDEX} is named but search_similar_parts "
        f"is not connected yet for {part_number} ({part_type})."
    )


def read_reply(message: str) -> str:
    print(message)
    return input("Part number: ").strip()


def _message(part_number: str, matches: list[dict[str, Any]]) -> str:
    if not matches:
        return (
            f"{part_number} was not found, and there is no close match to suggest.\n"
            "Type the part number again."
        )

    lines = [f"{part_number} was not found. Closest part numbers:"]
    for match in matches:
        number = match.get("part_number", "")
        kind = match.get("part_type", "")
        score = match.get("score")
        if score is None:
            lines.append(f"- {number} ({kind})")
        else:
            lines.append(f"- {number} ({kind}, score {score})")
    lines.append("Type the part number again.")
    return "\n".join(lines)
