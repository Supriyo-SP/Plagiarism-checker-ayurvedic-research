# Ayurvedic Plagiarism Checker - Product Requirements Document (PRD)

## 1. Problem Statement
Ayurvedic research articles present a unique challenge for traditional plagiarism checkers. Because these texts frequently rely on standard classical phrases from ancient sources, standard lexical checkers (like Turnitin) often flag legitimate references as plagiarism (False Positives). Furthermore, authors frequently translate Sanskrit terms into varying English forms (e.g., *Withania somnifera* vs. *Ashwagandha*), making it easy to disguise copied ideas using heavy paraphrasing (False Negatives). There is a need for a specialized plagiarism detection engine that understands Ayurvedic domain knowledge and can detect semantic paraphrasing.

## 2. Target User
- **Journal Editors & Peer Reviewers**: Who need to verify the originality of submitted Ayurvedic research manuscripts.
- **Academic Institutions**: Universities reviewing student thesis submissions in Alternative Medicine/Ayurveda disciplines.

## 3. Core Features
1. **Dual Similarity Engine**: A combination of Lexical Matching (BM25) to catch direct copy-pasting, and Semantic Similarity (`all-MiniLM-L6-v2`) to catch heavy paraphrasing.
2. **Ayurvedic Canonicalization**: An automated normalization layer that maps common Sanskrit terms to a canonical English/Scientific representation so paraphrasing cannot hide behind synonyms.
3. **Smart Sectioning**: Automatically ignores "References" and "Bibliography" sections to drastically reduce false positives.
4. **Explainable AI Output**: Rather than just a binary "Plagiarized/Not Plagiarized" score, the system provides an overall risk percentage alongside exactly *which* sections matched and the specific overlapping text snippets, providing human-readable evidence.
5. **Zero-Config Deployment**: The system can bootstrap itself. If deployed to a fresh cloud instance, it automatically synthesizes baseline data, generates word chunks, calculates high-dimensional vector embeddings, and builds the FAISS indexes on startup.

## 4. What it does NOT do (Out of Scope)
- **Image/Chart Plagiarism**: The system only processes raw text extracted from PDFs.
- **Real-time Web Scraping**: It checks against a local curated corpus of established Ayurvedic literature (simulated for the demo), not the entire live internet.
- **OCR on Scanned PDFs**: It requires text-selectable PDFs (it does not perform Optical Character Recognition on raw images).

## 5. Technical Architecture & Approach

### Data Pipeline (`pipeline/`)
1. **Extraction (`extract.py`)**: Uses `pdfplumber` to extract text from user-uploaded PDFs.
2. **Preprocessing (`preprocess.py`)**: 
   - Uses robust Regular Expressions to strip out References sections.
   - Normalizes unicode and lowercases text.
   - Translates Sanskrit terms into Canonical English.
   - Splits the large document into sliding windows of 200-300 word "chunks" for precise detection.
3. **Indexing (`index.py`)**:
   - Converts every chunk into a mathematical vector (embedding) using HuggingFace's `Sentence-Transformers`.
   - Stores these vectors in a **FAISS** (Facebook AI Similarity Search) index for lightning-fast retrieval.
   - Also builds a **BM25** statistical index for robust exact-word matching.

### Similarity Engine (`similarity.py`)
When a user uploads a new document, the engine:
1. Converts the new document into an embedding vector.
2. Uses FAISS Cosine Similarity to find the closest vectors in the database (Semantic).
3. Uses BM25 to score exact n-gram overlaps (Lexical).
4. Normalizes the mathematical cosine score (which usually hovers around 0.1 - 0.4 for completely unrelated text due to baseline noise) into a human-readable 0-100% scale.

### Frontend Layer (`app.py`)
- Built using **Streamlit**.
- Implements a highly customized, hardware-accelerated "Tech-Core" UI aesthetic using injected CSS (Electric Lime color palette and Terminal fonts) to provide a premium user experience.

## 6. Success Metrics
- **Speed**: Processing a 5-page PDF and returning a plagiarism score in `< 5 seconds`.
- **Accuracy**: Successfully detecting paraphrased overlaps that standard Turnitin/Lexical checkers would miss.
- **False Positive Reduction**: Zero matches triggered by the bibliography section.
