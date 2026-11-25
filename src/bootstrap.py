from pathlib import Path

PROJECT_NAME = "databricks_agent"

folders = [
    "agent/graph",
    "agent/nodes",
    "agent/prompts",
    "integrations/databricks",
    "integrations/neo4j",
    "config",
    "tests",
]

files = [
    # Agent graph
    "agent/graph/__init__.py",
    "agent/graph/state.py",
    "agent/graph/workflow.py",

    # Agent nodes
    "agent/nodes/__init__.py",
    "agent/nodes/intent_router.py",
    "agent/nodes/databricks_query.py",
    "agent/nodes/response_generation.py",

    # Prompts
    "agent/prompts/router.txt",
    "agent/prompts/answer.txt",

    # Databricks integration
    "integrations/__init__.py",
    "integrations/databricks/__init__.py",
    "integrations/databricks/llm.py",
    "integrations/databricks/sql_client.py",

    # Future Neo4j integration
    "integrations/neo4j/__init__.py",
    "integrations/neo4j/connector.py",

    # Configuration
    "config/__init__.py",
    "config/settings.py",
    "config/logging.py",

    # Tests
    "tests/__init__.py",
    "tests/test_routing.py",
    "tests/test_sql_safety.py",

    # Root files
    "main.py",
    ".env.example",
    ".gitignore",
    "README.md",
]

root = Path(PROJECT_NAME)
root.mkdir(exist_ok=True)

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

for file_name in files:
    path = root / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print(f"Created project: {root.resolve()}")