# Databricks BOM Agent

A work-in-progress Python agent for answering Bill of Materials (BOM) questions using data stored in Databricks.

## Current status

The project has an initial LangGraph workflow, intent routing, and fixed SQL templates for three BOM query types. The application is still under development and is not yet runnable end to end.

## Supported question types

The router is designed to handle:

- **BOM components** — What components belong to an assembly?
- **Where used** — Which assemblies use a component?
- **Component details** — What descriptive information is available for a component?

The SQL queries read from:

```text
<catalog>.<schema>.bom_relationships
Expected columns include parent_item_id, component_item_id, component_description, quantity, unit_of_measure, bom_level, effective_from, and effective_to.
```
Project structure
Text
src/databricks_agent/
├── agent/
│   ├── graph/          # LangGraph state and workflow
│   ├── nodes/          # Intent routing, Databricks query, response generation
│   └── prompts/        # Prompt files
├── config/             # Application settings and logging
├── integrations/
│   ├── databricks/     # Databricks LLM and SQL integrations
│   └── neo4j/          # Reserved for a future integration
└── tests/              # Test package
Requirements
Python 3.14 or newer
uv
A Databricks workspace and SQL warehouse
Databricks credentials with read access to the configured catalog and schema
Setup
Install the project dependencies:

bash
uv sync
Copy the example environment file and fill in the values for your workspace:

bash
cp .env.example .env
The project settings currently define these variables:

Variable	Purpose
DATABRICKS_HOST	Databricks workspace URL
DATABRICKS_TOKEN	Databricks access token
DATABRICKS_HTTP_PATH	SQL warehouse HTTP path
DATABRICKS_CATALOG	Catalog containing the BOM table
DATABRICKS_SCHEMA	Schema containing the BOM table
DATABRICKS_LLM_ENDPOINT	Intended model-serving endpoint setting
Do not commit .env or put credentials in source code.

Running
The CLI and LLM integration are not wired up yet. The configured databricks-agent command currently points to a placeholder, and the workflow expects a create_chat_model() function that is not yet implemented.

SQL behavior
The query node uses predefined SELECT templates and binds the item identifier as a query parameter. Queries have result limits of 50 or 200 rows, depending on the intent. The SQL client also checks for read-only query prefixes and blocks common write-operation keywords.

Use a Databricks identity with read-only permissions restricted to the data this agent needs.

Development
Run the test suite with:

bash
uv run pytest
Run Ruff checks with:

bash
uv run ruff check .
Tests and application wiring are still being built out.

Roadmap
Implement and configure the Databricks chat model integration.
Wire the package entry point to the actual CLI.
Add tests for routing, SQL parameter binding, and query behavior.
Document and validate the BOM table schema and effective-date behavior.
Add evaluation examples for representative questions and answers.
Code


One detail to revisit as you implement: `DATABRICKS_LLM_ENDPOINT` is in the settings, but the current `llm.py` uses a hard-coded endpoint/model instead.
