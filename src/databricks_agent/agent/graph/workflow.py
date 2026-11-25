from langgraph.graph import END, START, StateGraph

from databricks_agent.agent.graph.state import AgentState
from databricks_agent.agent.nodes.databricks_query import databricks_query
from databricks_agent.agent.nodes.intent_router import intent_router
from databricks_agent.agent.nodes.response_generation import response_generation


def route_intent(state: AgentState) -> str:
    if state.get("intent") in {
        "bom_children",
        "where_used",
        "component_details",
    }:
        return "databricks_query"

    return "response_generation"


def build_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("intent_router", intent_router)
    builder.add_node("databricks_query", databricks_query)
    builder.add_node("response_generation", response_generation)

    builder.add_edge(START, "intent_router")

    builder.add_conditional_edges(
        "intent_router",
        route_intent,
        {
            "databricks_query": "databricks_query",
            "response_generation": "response_generation",
        },
    )

    builder.add_edge(
        "databricks_query",
        "response_generation",
    )

    builder.add_edge(
        "response_generation",
        END,
    )

    return builder.compile()


workflow = build_workflow()