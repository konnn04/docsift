from src.utils import estimate_chunks, estimate_tokens


def test_estimate_tokens_scales_with_length():
    short = estimate_tokens("a" * 40)
    long = estimate_tokens("a" * 4000)
    assert long > short
    assert short >= 1


def test_estimate_chunks_single_chunk_for_short_text():
    assert estimate_chunks("hello world", chunk_size_tokens=800, overlap_tokens=400) == 1


def test_estimate_chunks_scales_with_stride():
    # 16000 chars / 4 chars-per-token ~= 4000 tokens, stride = 800-400=400 -> ~10 chunks
    text = "a" * 16000
    chunks = estimate_chunks(text, chunk_size_tokens=800, overlap_tokens=400)
    assert 8 <= chunks <= 12


def test_estimate_chunks_never_zero():
    assert estimate_chunks("", chunk_size_tokens=800, overlap_tokens=400) >= 1
