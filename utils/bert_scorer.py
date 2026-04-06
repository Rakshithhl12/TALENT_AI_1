"""
utils/bert_scorer.py — TF-IDF cosine similarity scorer.
No sentence-transformers / BERT needed. Works fully offline.
"""

from __future__ import annotations
import re
import math
from collections import Counter


def _tokenize(text: str) -> list:
    return re.findall(r"[a-z]{2,}", text.lower())


def compute_score(resume_text: str, job_description: str) -> float:
    """Return cosine similarity score in [0, 1] using TF-IDF."""
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    ta, tb = _tokenize(resume_text), _tokenize(job_description)
    if not ta or not tb:
        return 0.0

    vocab = set(ta) | set(tb)
    ca, cb = Counter(ta), Counter(tb)

    def tfidf(counter, token, other):
        tf  = counter[token] / max(len(counter), 1)
        idf = math.log((2 + 1) / (1 + int(token in counter and token in other)))
        return tf * idf

    va = [tfidf(ca, t, cb) for t in vocab]
    vb = [tfidf(cb, t, ca) for t in vocab]
    dot = sum(x * y for x, y in zip(va, vb))
    na  = math.sqrt(sum(x * x for x in va))
    nb  = math.sqrt(sum(y * y for y in vb))
    return dot / (na * nb) if na * nb else 0.0


def backend_label() -> str:
    return "TF-IDF Cosine Similarity"
