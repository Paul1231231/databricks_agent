from typing import Any, Literal, TypedDict


Intent = Literal[
    "bom_children",
    "where_used",
    "component_details",
    "unsupported",
]


class AgentState(TypedDict, total=False):
    question: str

    intent: Intent
    item_id: str | None

    sql_query: str | None
    sql_parameters: list[Any]

    query_results: list[dict[str, Any]]

    answer: str
    error: str | None