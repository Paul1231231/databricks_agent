from databricks_agent.agent.graph.workflow import (
    route_after_exists,
    route_after_identify,
    route_after_suggest,
    route_after_usecase,
)
from databricks_agent.agent.nodes.identify_part import _span_in_question
from databricks_agent.agent.nodes.match_usecase import match_usecase
from databricks_agent.agent.nodes.run_fixed_query import run_fixed_query


def test_part_number_must_appear_in_the_question():
    assert _span_in_question("explode BOM for AB-100", "AB-100") == "AB-100"
    assert _span_in_question("explode BOM for AB-100", "ab-100") == "AB-100"
    assert _span_in_question("explode BOM for AB-100", "AB") is None


def test_missing_part_skips_the_lookup():
    assert route_after_identify({"part_number": "A"}) == "check_part_exists"
    assert route_after_identify({"error": "x", "part_number": "A"}) == "compose_answer"


def test_unknown_part_asks_for_a_retype():
    assert route_after_exists({"part_exists": True}) == "match_usecase"
    assert route_after_exists({"part_exists": False}) == "suggest_part"
    assert route_after_exists({"error": "lookup failed"}) == "compose_answer"


def test_retyped_part_returns_to_identify():
    assert route_after_suggest({"retyped_part_number": "B"}) == "identify_part"
    assert route_after_suggest({}) == "compose_answer"


def test_only_an_allowed_usecase_runs_sql():
    assert route_after_usecase({"usecase": "bom_explosion"}) == "run_fixed_query"
    assert (
        route_after_usecase({"usecase": "bom_explosion", "error": "x"})
        == "compose_answer"
    )

    blocked = run_fixed_query(
        {
            "usecase": "supplier_impact",
            "part_number": "A1",
            "part_type": "model",
        }
    )
    assert blocked["error"] == "No allowed fixed query for this part."


def test_assembly_has_no_fixed_query():
    result = match_usecase(
        {
            "question": "explode it",
            "part_number": "A1",
            "part_type": "assembly",
        }
    )
    assert result["usecase"] is None
    assert "assembly" in result["error"]
