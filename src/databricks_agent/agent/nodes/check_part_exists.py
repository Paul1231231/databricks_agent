import re

from databricks_agent.agent.graph.state import AgentState, PartType
from databricks_agent.config.settings import get_settings
from databricks_agent.integrations.databricks.sql_client import DatabricksSQLClient

# Change these three names to the item master in the warehouse.
ITEM_TABLE = "item_master"
ITEM_ID_COLUMN = "item_id"
ITEM_TYPE_COLUMN = "item_type"

_TYPE_BY_VALUE = {
    "assembly": "assembly",
    "component": "component",
    "model": "model",
}

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def check_part_exists(state: AgentState) -> dict:
    part_number = state.get("part_number")
    if not part_number:
        return {
            "part_exists": False,
            "error": "No part number to look up.",
        }

    try:
        found = lookup_part(part_number)
    except Exception as exc:  # noqa: BLE001 — lookup failures become an answer
        return {
            "part_exists": False,
            "error": f"Part lookup failed: {exc}",
        }

    if found is None:
        return {
            "part_exists": False,
            "error": None,
        }

    if len(found) > 1:
        listed = ", ".join(found)
        return {
            "part_exists": False,
            "error": (
                f"{part_number} matches more than one part type: {listed}."
            ),
        }

    return {
        "part_exists": True,
        "part_type": found[0],
        "error": None,
    }


def lookup_part(part_number: str) -> list[PartType] | None:
    """Return the distinct types for an exact part number, or None when it is absent.

    One item master is assumed: an id column and a type column. If assemblies,
    components, and models live in separate tables, this is the function to change.
    The guessed type from the model is not used here; the row decides.
    """
    query = f"""
        SELECT DISTINCT {_column(ITEM_TYPE_COLUMN)} AS item_type
        FROM {_qualified(ITEM_TABLE)}
        WHERE {_column(ITEM_ID_COLUMN)} = ?
        LIMIT 5
    """
    rows = DatabricksSQLClient().execute_read(
        query=query,
        parameters=[part_number],
    )
    if not rows:
        return None

    found: list[PartType] = []
    for row in rows:
        raw = _cell(row, "item_type")
        if raw is None or str(raw).strip() == "":
            raise ValueError(
                f"{part_number} exists but {ITEM_TYPE_COLUMN} is empty."
            )
        part_type = _TYPE_BY_VALUE.get(str(raw).strip().casefold())
        if part_type is None:
            raise ValueError(
                f"{part_number} exists but {ITEM_TYPE_COLUMN} "
                f"{raw!r} is not assembly, component, or model."
            )
        if part_type not in found:
            found.append(part_type)
    return found


def _qualified(table: str) -> str:
    settings = get_settings()
    parts = (
        _column(settings.databricks_catalog),
        _column(settings.databricks_schema),
        _column(table),
    )
    return ".".join(f"`{part}`" for part in parts)


def _column(name: str) -> str:
    if not _IDENT.fullmatch(name):
        raise ValueError(f"Unsafe SQL identifier: {name}")
    return name


def _cell(row: dict, column: str):
    for key, value in row.items():
        if str(key).casefold() == column.casefold():
            return value
    raise KeyError(column)
