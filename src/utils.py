from __future__ import annotations
import math

CHARS_PER_TOKEN_ESTIMATE = 4


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / CHARS_PER_TOKEN_ESTIMATE))


def estimate_chunks(text: str, chunk_size_tokens: int, overlap_tokens: int) -> int:
    tokens = estimate_tokens(text)
    stride = max(1, chunk_size_tokens - overlap_tokens)
    return max(1, math.ceil(tokens / stride))
