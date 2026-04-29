import os
import pytest
from pipeline.index import build_index

def test_build_index_no_chunks(tmp_path):
    # Should exit gracefully
    build_index("nonexistent_chunks.json", str(tmp_path))
    assert not os.path.exists(os.path.join(str(tmp_path), "vector.index"))

def test_build_index_creates_files(tmp_path):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_dir = os.path.join(base_dir, "tests", "fixtures", "texts")
    chunks_file = str(tmp_path / "chunks.json")
    out_dir = str(tmp_path / "index")
    
    # Process texts to create chunks
    from pipeline.preprocess import process_all
    process_all(input_dir, chunks_file)
    
    # Build index
    build_index(chunks_file, out_dir)
    
    assert os.path.exists(os.path.join(out_dir, "vector.index"))
    assert os.path.exists(os.path.join(out_dir, "metadata.json"))
    assert os.path.exists(os.path.join(out_dir, "bm25.pkl"))
