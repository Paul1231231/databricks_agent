from databricks_agent.agent.graph.state import USECASES_BY_PART_TYPE, AgentState
from databricks_agent.integrations.databricks.sql_client import DatabricksSQLClient

# Pre-written SELECT text for each use case. None until the warehouse query is pasted in.
# Every query must be read-only and bind the confirmed part number as the only ? parameter.
FIXED_QUERIES: dict[str, str | None] = {
    "bom_explosion": None,
    "customer_impact": None,
    "model_impact": None,
    "component_impact": None,
    "supplier_impact": None,
}


def run_fixed_query(state: AgentState) -> dict:
    usecase = state.get("usecase")
    part_number = state.get("part_number")
    part_type = state.get("part_type")
    allowed = USECASES_BY_PART_TYPE.get(part_type, ())

    if usecase is None or usecase not in allowed:
        return {
            "query_results": [],
            "error": "No allowed fixed query for this part.",
        }

    if not part_number:
        return {
            "query_results": [],
            "error": "No part number to query.",
        }

    query = FIXED_QUERIES.get(usecase)
    if not query or not query.strip():
        label = usecase.replace("_", " ")
        return {
            "query_results": [],
            "sql_query": None,
            "sql_parameters": [part_number],
            "error": f"The {label} query is not registered yet.",
        }

    try:
        results = DatabricksSQLClient().execute_read(
            query=query,
            parameters=[part_number],
        )
    except Exception as exc:  # noqa: BLE001 — query failures become an answer
        return {
            "query_results": [],
            "sql_query": query,
            "sql_parameters": [part_number],
            "error": f"Databricks query failed: {exc}",
        }

    return {
        "sql_query": query,
        "sql_parameters": [part_number],
        "query_results": results,
        "error": None,
    }
