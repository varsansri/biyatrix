import json
from groq import Groq
from database import get_all_entries
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def find_matches(query: str, top_k: int = 5) -> list:
    entries = get_all_entries()
    if not entries:
        return []

    candidates = [
        {"id": e["id"], "summary": e.get("summary") or "", "problem": e.get("problem") or "",
         "solution": e.get("solution"), "domain": e.get("domain"), "emotion": e.get("emotion"),
         "stage": e.get("stage"), "constraints": e.get("constraints"), "tools": e.get("tools")}
        for e in entries
    ]

    catalog = "\n".join(
        f"{c['id']}. [{c['domain']}|{c['emotion']}] {c['summary']}"
        for c in candidates
    )

    rank_resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You rank entries by relevance to a query. "
                    "Return JSON: {\"matches\": [{\"id\": <int>, \"score\": <0-100>, \"why\": \"<20 words max>\"}]} "
                    "Top 5 most relevant only. Score 0 if not relevant."
                ),
            },
            {"role": "user", "content": f"Query: {query}\n\nEntries:\n{catalog}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    try:
        ranked = json.loads(rank_resp.choices[0].message.content).get("matches", [])
    except Exception:
        return []

    ranked = [r for r in ranked if r.get("score", 0) >= 25]
    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
    ranked = ranked[:top_k]

    entry_map = {e["id"]: e for e in entries}
    results = []
    for r in ranked:
        e = entry_map.get(r["id"])
        if not e:
            continue
        results.append({
            "id": e["id"],
            "summary": e.get("summary"),
            "problem": e.get("problem"),
            "solution": e.get("solution"),
            "domain": e.get("domain"),
            "emotion": e.get("emotion"),
            "stage": e.get("stage"),
            "tools": json.loads(e.get("tools") or "[]"),
            "constraints": json.loads(e.get("constraints") or "[]"),
            "created_at": e.get("created_at"),
            "relevance_score": r.get("score", 0),
            "why_relevant": r.get("why", ""),
        })

    return results
