from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryInput(BaseModel):
    question: str

# ---------- Load Schema ----------
def load_schema():
    with open("schema.txt", "r") as f:
        return f.read()

# ---------- Load Domain Knowledge ----------
def load_domain_knowledge():
    try:
        with open("domain_knowledge.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# ---------- Load Good Examples ----------
def load_good_examples():
    examples = []
    try:
        with open("feedback.json", "r") as f:
            for line in f:
                data = json.loads(line)
                if data.get("feedback") == "good":
                    examples.append(data)
    except FileNotFoundError:
        pass

    return examples[-10:]  # keep it smaller for better performance

# ---------- API ----------
@app.post("/generate-sql", response_class=PlainTextResponse)
def generate_sql(input: QueryInput):
    schema = load_schema()
    domain_knowledge = load_domain_knowledge()
    examples = load_good_examples()

    # ---------- Build example text ----------
    example_text = ""
    for ex in examples:
        example_text += f"""
User: {ex['question']}
SQL:
{ex['sql']}
"""

    prompt = f"""
You are an expert SQL developer for Apriso MES.

DOMAIN KNOWLEDGE (VERY IMPORTANT):
{domain_knowledge}

LEARN FROM THESE EXAMPLES:
{example_text}

RULES:
- Only SELECT queries
- No DELETE, UPDATE, INSERT
- Use SQL Server syntax
- Limit results to TOP 100
- Use proper date filters (GETDATE())
- Always follow domain knowledge for joins and filters
- Do NOT guess joins — use defined relationships

SCHEMA:
{schema}

USER QUESTION:
{input.question}

Return output EXACTLY in this format:

SQL:
<your SQL>

Explanation:
<simple explanation>
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output = response.choices[0].message.content

    # ---------- Clean formatting ----------
    output = output.replace("```sql", "").replace("```", "")
    output = output.replace("\\n", "\n").strip()

    return output