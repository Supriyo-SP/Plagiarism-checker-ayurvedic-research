import pytest
from pipeline.preprocess import remove_references, normalize_text, chunk_text

def test_remove_references():
    text = "Introduction\nSome text here that should be kept.\nReferences\n1. Smith et al."
    assert "References" not in remove_references(text)
    assert "Some text here" in remove_references(text)

def test_normalize_text_word_boundary():
    # Should replace amla but not amlodipine
    text = "The plant amla is different from amlodipine."
    normalized = normalize_text(text)
    assert "emblica officinalis" in normalized
    assert "amlodipine" in normalized
    assert "emblica officinalisodipine" not in normalized

def test_chunk_text_min_size():
    text = "This is a very short text with less than twenty words here."
    chunks = chunk_text(text)
    # Should be empty because length < 20
    assert len(chunks) == 0
