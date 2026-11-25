from databricks_agent.config.settings import get_settings


class Neo4jConnector:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.neo4j_enabled:
            raise RuntimeError(
                "Neo4j integration is currently disabled."
            )

        raise NotImplementedError(
            "Neo4j will be implemented in a future release."
        )