from typing import Any, Literal, TypedDict

Intent = Literal[
    "bom_children",
    "where_used",
    "component_details",
    "unsupported",
]

PartType = Literal["assembly", "component", "model"]

Usecase = Literal[
    "bom_explosion",
    "customer_impact",
    "model_impact",
    "component_impact",
    "supplier_impact",
]

# The database confirms part_type. These are the only queries that may run.
USECASES_BY_PART_TYPE: dict[PartType, tuple[Usecase, ...]] = {
    "model": ("bom_explosion", "customer_impact", "model_impact"),
    "component": ("component_impact", "supplier_impact"),
    "assembly": (),
}


class AgentState(TypedDict, total=False):
    question: str

    part_number: str | None
    part_type: PartType | None
    part_exists: bool
    retyped_part_number: str | None
    part_attempts: int
    suggested_parts: list[dict[str, Any]]

    usecase: Usecase | None

    # Kept for the earlier routing nodes.
    intent: Intent
    item_id: str | None

    sql_query: str | None
    sql_parameters: list[Any]
    query_results: list[dict[str, Any]]

    answer: str
    error: str | None
