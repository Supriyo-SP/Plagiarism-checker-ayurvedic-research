import os
import pytest
from pipeline.extract import extract_text_from_pdf, extract_all

def test_extract_text_from_pdf_empty(tmp_path):
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b"") # Invalid PDF
    assert extract_text_from_pdf(str(empty_pdf)) == ""

def test_extract_all_missing_dir():
    assert extract_all("invalid_dir_xyz", "out_dir_xyz") == []
