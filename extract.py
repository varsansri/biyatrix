import json
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You extract structured insight from raw human brain dumps.
Input may be messy, emotional, incomplete, multilingual, or conversational. Extract what you can, never invent.

Return ONLY valid JSON:
{
  "problem": "the core problem, struggle, or thought (string or null)",
  "constraints": ["list of constraints: time, money, tools, location, skill, resources"],
  "solution": "any solution or partial solution mentioned (string or null)",
  "domain": "one word: tech/business/personal/craft/health/finance/creative/other",
  "tools": ["tools, platforms, apps, methods mentioned"],
  "stage": "one of: exploring/building/stuck/solved/venting/celebrating",
  "emotion": "one of: frustrated/excited/confused/hopeful/exhausted/proud/anxious/relieved",
  "summary": "1 sentence human summary — what is this person going through?"
}"""


def extract(text: str) -> dict:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {"summary": text[:100], "domain": "other", "emotion": "neutral", "stage": "exploring"}
