# Product Requirements Document (PRD)
**Product:** Ayurvedic Plagiarism Engine (v5.0)

## Problem Statement
Plagiarism detection is exceptionally difficult for Ayurvedic research compared to standard academic fields. The domain relies heavily on universal ancient canonical texts (e.g., *Charaka Samhita*), meaning genuine researchers frequently cite the exact same Sanskrit slokas or principles. Furthermore, there is massive terminology fragmentation: a single concept might be referred to by its Sanskrit name (*Ashwagandha*), its English common name (*Winter Cherry*), or its botanical nomenclature (*Withania somnifera*). 

Standard plagiarism checkers fail here in two ways:
1. **False Positives:** They flag standard domain terms, historical citations, and bibliography sections as "plagiarized," burying the reviewer in noise.
2. **False Negatives:** Plagiarists can easily defeat simple lexical checkers (like Turnitin) by simply running a "Find and Replace" to swap Sanskrit terms with English botanical equivalents.

## Target User
**Editors of Ayurvedic medical journals, academic peer-reviewers, and university research committee members.** These users are highly technical but time-constrained. They need to quickly verify the originality of a submitted manuscript without being bogged down by expected domain-specific overlap.

## Core Features (What v1 Does)
- **Dual-Engine Similarity Detection:** Combines Semantic paraphrasing detection (via Sentence Transformers) with strict Lexical overlap (via BM25) to catch both copy-pasting and idea-theft.
- **Ayurvedic Canonicalization:** Automatically normalizes over 20+ interchangeable Ayurvedic/botanical terms (e.g., `Tulsi` → `Ocimum sanctum`, `Haritaki` → `Terminalia chebula`) before searching, preventing synonym-swapping plagiarism.
- **Section Smart Filtering:** Automatically strips "References" and "Bibliography" sections from both the corpus and the query to eliminate the most common source of false flags.
- **Explainable Metrics Grid:** Provides a clear Overall Confidence Score, Exact Match %, and Consecutive Match %, backed by an expander showing the exact overlapping text snippets for human verification.
- **Format Flexibility:** Accepts both raw text pasting and direct PDF uploads.

## Scope Boundaries (What it explicitly does NOT do)
- **No Image/Table OCR:** It purely extracts text. Plagiarism disguised inside images, charts, or complex tabular data will bypass the radar entirely.
- **Not an Internet Scraper:** It does not blindly scrape the open web. It strictly checks submissions against a highly curated, trusted offline database (the uploaded Corpus of Ayurvedic journals).
- **No Automated Rejections:** It does not make the final call to reject a paper. It acts strictly as a "signal detection grid" to assist and accelerate the human reviewer's decision.
- **No Full-Document Deep Scans:** To ensure instant performance on standard hardware, submissions are capped at 1000 words per check (acting as a spot-check rather than an hours-long thesis scan).

## Technical Approach
- **Backend Language:** Python 3.9+
- **Semantic Engine (Embeddings):** `sentence-transformers/all-MiniLM-L6-v2`. Chosen because it is lightweight, runs fast on CPU, and is highly capable of capturing paraphrased intent.
- **Vector Database:** `FAISS` (Facebook AI Similarity Search). Chosen over heavy cloud vector DBs (like Pinecone) to allow the app to run completely locally and fast via a lightweight `vector.index` file.
- **Lexical Engine:** `rank-bm25` for lightning-fast statistical TF-IDF text matching.
- **Frontend & Hosting:** `Streamlit` & `Streamlit Community Cloud`. Chosen for rapid, 72-hour prototyping, native PDF upload capabilities, and seamless serverless hosting.
- **Data Engineering:** PDF extraction handled by `pdfplumber`. Corpus is pre-processed into a lightweight `chunks.json` file, allowing the deployment server to "cold-start" instantly without needing to host raw PDFs.

## Success Metrics
1. **False Positive Reduction:** The system must not trigger a "High Risk" alert for documents that only share standard Ayurvedic terms or references (verified via the exact match threshold logic).
2. **High Recall on Paraphrased Theft:** Catching texts that have >80% semantic similarity despite malicious lexical swapping.
3. **Latency:** Checking a 1000-word submission against the local corpus should return an analyzed risk score and highlighted snippets in under 5 seconds to ensure a smooth, uninterrupted reviewer experience.
