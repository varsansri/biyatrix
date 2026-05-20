import pickle
import json
from groq import Groq
from embeddings import embed, cosine_similarity
from database import get_all_entries
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

RELEVANCE_THRESHOLD = 0.25


def find_matches(query: str, top_k: int = 5) -> list:
    entries = get_all_entries()
    if not entries:
        return []

    query_vec = embed(query)

    scored = []
    for entry in entries:
        if not entry.get("embedding"):
            continue
        vec = pickle.loads(entry["embedding"])
        score = cosine_similarity(query_vec, vec)
        if score >= RELEVANCE_THRESHOLD:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    if not top:
        return []

    summaries = "\n".join(
        f"{i+1}. [{e.get('domain','?')} | {e.get('emotion','?')}] {e.get('summary','')}"
        for i, (_, e) in enumerate(top)
    )
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "For each matched entry, write ONE short sentence (max 20 words) explaining why it's relevant to the query. Reference a specific shared constraint or struggle. Return as JSON array of strings.",
            },
            {"role": "user", "content": f"Query: {query}\n\nMatches:\n{summaries}"},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    try:
        raw = json.loads(resp.choices[0].message.content)
        explanations = raw if isinstance(raw, list) else next(iter(raw.values()), [])
    except Exception:
        explanations = []

    results = []
    for i, (score, entry) in enumerate(top):
        results.append({
            "id": entry["id"],
            "summary": entry.get("summary"),
            "problem": entry.get("problem"),
            "solution": entry.get("solution"),
            "domain": entry.get("domain"),
            "emotion": entry.get("emotion"),
            "stage": entry.get("stage"),
            "tools": json.loads(entry.get("tools") or "[]"),
            "constraints": json.loads(entry.get("constraints") or "[]"),
            "created_at": entry.get("created_at"),
            "relevance_score": round(score * 100),
            "why_relevant": explanations[i] if i < len(explanations) else "",
        })

    return results
