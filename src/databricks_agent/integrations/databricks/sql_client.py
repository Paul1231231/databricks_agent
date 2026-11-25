from typing import Any

from databricks import sql

from databricks_agent.config.settings import get_settings


class DatabricksSQLClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def execute_read(
        self,
        query: str,
        parameters: list[Any] | None = None,
    ) -> list[dict[str, Any]]:
        self._validate_read_only_query(query)

        with sql.connect(
            server_hostname=self._server_hostname(),
            http_path=self.settings.databricks_http_path,
            access_token=self.settings.databricks_token,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    parameters=parameters or [],
                )

                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()

                return [
                    dict(zip(columns, row, strict=True))
                    for row in rows
                ]

    def _server_hostname(self) -> str:
        return (
            self.settings.databricks_host
            .removeprefix("https://")
            .removeprefix("http://")
            .rstrip("/")
        )

    @staticmethod
    def _validate_read_only_query(query: str) -> None:
        normalized = " ".join(query.upper().split())

        allowed_starts = ("SELECT ", "WITH ", "SHOW ", "DESCRIBE ")

        forbidden_terms = (
            "INSERT ",
            "UPDATE ",
            "DELETE ",
            "MERGE ",
            "DROP ",
            "ALTER ",
            "CREATE ",
            "TRUNCATE ",
            "GRANT ",
            "REVOKE ",
            "OPTIMIZE ",
            "VACUUM ",
            "COPY INTO ",
        )

        if not normalized.startswith(allowed_starts):
            raise ValueError("Only read-only SQL queries are permitted.")

        if any(term in normalized for term in forbidden_terms):
            raise ValueError(
                "A prohibited SQL operation was detected."
            )