import os, json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("LLM_MODEL", "gpt-4o")

def review_connector(api_docs: str, code: str) -> dict:
    with open("prompts/reviewer.txt", encoding="utf-8") as f:
        system = f.read()
    resp = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"Review this Calendly connector code:\n\n{code}"}],
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"verdict": "FAIL", "reasons": ["Reviewer returned invalid JSON"]}