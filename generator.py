import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("LLM_MODEL", "gpt-4o")

def generate_connector(api_docs: str) -> str:
    with open("prompts/generator_system.txt", encoding="utf-8") as f:
        system = f.read()
    user = f"""App: Calendly
API docs: {api_docs}
Auth available to the customer: Personal Access Token, read from the env var CALENDLY_TOKEN
Data needed: users in the organization; usage data (scheduled events per user)
Customer constraints: read-only, sandbox first, org-level data only

Generate the connector following your instructions."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content