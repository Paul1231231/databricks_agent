from openai import OpenAI
import os

client = OpenAI(
  api_key=os.environ.get("DATABRICKS_TOKEN"),
  base_url="https://adb-4227358389530592.12.azuredatabricks.net/ai-gateway/mlflow/v1",
)

response = client.responses.create(
  model="system.ai.claude-haiku-5-5",
  max_output_tokens=256,
  input=[
    {"role": "user", "content": [{"type": "input_text", "text": "Hello!"}]},
    {"role": "assistant", "content": [{"type": "output_text", "text": "Hello! How can I assist you today?"}]},
    {"role": "user", "content": [{"type": "input_text", "text": "What is Databricks?"}]},
  ],
)

print(response.output[0].content[0].text)