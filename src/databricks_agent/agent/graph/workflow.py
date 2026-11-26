from langgraph.graph import END, START, StateGraph

from databricks_agent.agent.graph.state import AgentState
from databricks_agent.agent.nodes.check_part_exists import check_part_exists
from databricks_agent.agent.nodes.compose_answer import compose_answer
from databricks_agent.agent.nodes.identify_part import identify_part
from databricks_agent.agent.nodes.match_usecase import match_usecase
from databricks_agent.agent.nodes.run_fixed_query import run_fixed_query
from databricks_agent.agent.nodes.suggest_part import suggest_part


def route_after_identify(state: AgentState) -> str:
    if state.get("error") or not state.get("part_number"):
        return "compose_answer"
    return "check_part_exists"


def route_after_exists(state: AgentState) -> str:
    if state.get("error"):
        return "compose_answer"
    if state.get("part_exists"):
        return "match_usecase"
    return "suggest_part"


def route_after_suggest(state: AgentState) -> str:
    if state.get("retyped_part_number"):
        return "identify_part"
    return "compose_answer"


def route_after_usecase(state: AgentState) -> str:
    if state.get("usecase") and not state.get("error"):
        return "run_fixed_query"
    return "compose_answer"


def build_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("identify_part", identify_part)
    builder.add_node("check_part_exists", check_part_exists)
    builder.add_node("suggest_part", suggest_part)
    builder.add_node("match_usecase", match_usecase)
    builder.add_node("run_fixed_query", run_fixed_query)
    builder.add_node("compose_answer", compose_answer)

    builder.add_edge(START, "identify_part")

    builder.add_conditional_edges(
        "identify_part",
        route_after_identify,
        {
            "check_part_exists": "check_part_exists",
            "compose_answer": "compose_answer",
        },
    )
    builder.add_conditional_edges(
        "check_part_exists",
        route_after_exists,
        {
            "match_usecase": "match_usecase",
            "suggest_part": "suggest_part",
            "compose_answer": "compose_answer",
        },
    )
    builder.add_conditional_edges(
        "suggest_part",
        route_after_suggest,
        {
            "identify_part": "identify_part",
            "compose_answer": "compose_answer",
        },
    )
    builder.add_conditional_edges(
        "match_usecase",
        route_after_usecase,
        {
            "run_fixed_query": "run_fixed_query",
            "compose_answer": "compose_answer",
        },
    )

    builder.add_edge("run_fixed_query", "compose_answer")
    builder.add_edge("compose_answer", END)

    return builder.compile()


workflow = build_workflow()
