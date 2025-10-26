import os
from typing import List
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def get_embedding(text: str) -> List[float]:
    """Return an embedding vector for the given text.
    Falls back to an empty vector on error. Model configurable via env.
    """
    model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    try:
        client = _get_client()
        resp = client.embeddings.create(model=model, input=text)
        return resp.data[0].embedding
    except Exception:
        return []
