import os
from openai import OpenAI

client = OpenAI()

OPENAI_TIMEOUT_SECONDS = float(os.getenv('OPENAI_TIMEOUT_SECONDS', '30'))


def score_lead(lead: dict) -> dict:
    prompt = (
        "Rate this lead from 1–10 based on relevance, company size, and engagement potential. "
        "Respond only with a JSON object containing {score, reason}.\nLead:\n" + str(lead)
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert B2B sales analyst."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        content = resp.choices[0].message.content
        import json
        try:
            return json.loads(content)
        except Exception:
            return {"score": 5, "reason": content[:300]}
    except Exception:
        return {"score": 5, "reason": "Fallback score due to model error."}
