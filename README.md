# Ayurvedic Plagiarism Checker 🌿

An AI-powered Plagiarism Detection Tool specifically tailored for Ayurvedic Research Articles. It combines semantic search (using Sentence Transformers) and lexical overlap (using BM25) to detect both exact copying and heavy paraphrasing. 

## Features
- **Dual Similarity Engine:** Employs BM25 for strict lexical overlapping and `all-MiniLM-L6-v2` for semantic similarities.
- **Ayurveda Canonicalization:** Normalizes specific Ayurvedic terms (e.g. `ashwagandha` → `withania somnifera`).
- **Section Smart:** Ignores "References/Bibliography" sections to prevent false positives.
- **Explainable Output:** Highlights both the risk score and the matching snippets with sources.
- **Fast Execution:** Streamlit caching ensures the application returns results securely under 2 seconds.

## Installation & Setup

1. **Clone the repository:**
   Ensure you have configured Python 3.9+.

2. **Setup Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Data Generation / Mocking:**
   Generate the local corpus and indexes.
   ```bash
   # Generate mock texts
   python pipeline/mock_texts.py
   
   # Preprocess texts
   python pipeline/preprocess.py
   
   # Build FAISS and BM25 Indexes
   python pipeline/index.py
   ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Tech Stack
- **Python Backend:** Core logic
- **Sentence-Transformers & FAISS:** For vector embeddings & clustering.
- **Rank-BM25:** Fast statistical lexical scoring.
- **Streamlit:** Frontend.
- **pdfplumber:** PDF extraction wrapper.

## Folder Structure
- `app.py`: Streamlit Application File.
- `pipeline/`: Core modules (`extract.py`, `preprocess.py`, `index.py`, `similarity.py`).
- `data/`: Contains extracted pdfs, text chunks, and vector index (FAISS). 
