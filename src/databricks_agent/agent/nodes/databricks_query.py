from agent.graph.state import AgentState
from config.settings import get_settings
from integrations.databricks.sql_client import DatabricksSQLClient


def build_table_name() -> str:
    settings = get_settings()

    return (
        f"`{settings.databricks_catalog}`."
        f"`{settings.databricks_schema}`."
        "`bom_relationships`"
    )


def build_query(intent: str) -> str:
    table = build_table_name()

    queries = {
        "bom_children": f"""
            SELECT
                parent_item_id,
                component_item_id,
                component_description,
                quantity,
                unit_of_measure,
                bom_level
            FROM {table}
            WHERE parent_item_id = ?
            ORDER BY bom_level, component_item_id
            LIMIT 200
        """,
        "where_used": f"""
            SELECT DISTINCT
                component_item_id,
                parent_item_id,
                bom_level
            FROM {table}
            WHERE component_item_id = ?
            ORDER BY bom_level, parent_item_id
            LIMIT 200
        """,
        "component_details": f"""
            SELECT DISTINCT
                component_item_id,
                component_description,
                unit_of_measure,
                effective_from,
                effective_to
            FROM {table}
            WHERE component_item_id = ?
            LIMIT 50
        """,
    }

    if intent not in queries:
        raise ValueError(f"No query exists for intent: {intent}")

    return queries[intent]


def databricks_query(state: AgentState) -> dict:
    item_id = state.get("item_id")
    intent = state.get("intent")

    if not item_id:
        return {
            "query_results": [],
            "error": (
                "No assembly, BOM, part, or component identifier "
                "was found in the question."
            ),
        }

    try:
        query = build_query(intent)
        client = DatabricksSQLClient()

        results = client.execute_read(
            query=query,
            parameters=[item_id],
        )

        return {
            "sql_query": query,
            "sql_parameters": [item_id],
            "query_results": results,
            "error": None,
        }

    except Exception as exc:
        return {
            "query_results": [],
            "error": f"Databricks query failed: {exc}",
        }