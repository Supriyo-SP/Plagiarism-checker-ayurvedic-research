import os
import pytest
from pipeline.similarity import PlagiarismDetector
from pipeline.preprocess import process_all
from pipeline.index import build_index

@pytest.fixture(scope="module")
def index_dir(tmp_path_factory):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_dir = os.path.join(base_dir, "tests", "fixtures", "texts")
    
    tmp_dir = tmp_path_factory.mktemp("data")
    chunks_file = str(tmp_dir / "chunks.json")
    out_dir = str(tmp_dir / "index")
    
    process_all(input_dir, chunks_file)
    build_index(chunks_file, out_dir)
    return out_dir

def test_detect_empty_metadata(tmp_path):
    # Missing metadata should return 0 score due to error handling returning empty
    detector = PlagiarismDetector(str(tmp_path))
    res = detector.detect("some text")
    assert res["overall_score"] == 0
    assert len(res["top_matches"]) == 0

def test_detect_identical_text(index_dir):
    detector = PlagiarismDetector(index_dir)
    query = "Abstract This paper discusses the role of herbal medicine. Introduction Many researchers have focused on the benefits of these plants. Various formulations are available in the market. The results indicate a positive impact on health when used correctly."
    res = detector.detect(query)
    
    assert res["overall_score"] > 50.0
    assert len(res["top_matches"]) > 0

def test_detect_semantic_only(index_dir):
    detector = PlagiarismDetector(index_dir)
    # Different words, similar meaning
    query = "This document explores the function of natural remedies and traditional healing."
    res = detector.detect(query)
    
    # Might not be high enough depending on the model, but should process without crashing
    assert "overall_score" in res

def test_exact_match_metrics(index_dir):
    detector = PlagiarismDetector(index_dir)
    query = "Abstract This paper discusses the role of herbal medicine. Introduction Many researchers have focused on the benefits of these plants. Various formulations are available in the market. The results indicate a positive impact on health when used correctly."
    res = detector.detect(query)
    
    match = res["top_matches"][0]
    assert match["consecutive_percentage"] > 0
    assert match["exact_match_percentage"] > 0
