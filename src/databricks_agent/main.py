from agent.graph.workflow import workflow


def main() -> None:
    print("Databricks BOM Agent")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        result = workflow.invoke(
            {
                "question": question,
                "query_results": [],
                "sql_parameters": [],
                "error": None,
            }
        )

        print(f"\n{result['answer']}")


if __name__ == "__main__":
    main()