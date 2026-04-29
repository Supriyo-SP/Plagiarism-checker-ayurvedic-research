# Ayurvedic Plagiarism Checker [v4.0] 🌿

An AI-powered Plagiarism Detection Tool specifically tailored for Ayurvedic Research Articles. It combines semantic search (using Sentence Transformers) and lexical overlap (using BM25) to detect both exact copying and heavy paraphrasing. 

## Version History
- **v1**: Initial implementation (BM25 + Semantic Search pipeline).
- **v2**: Calibrated semantic scaling (adjusting `all-MiniLM-L6-v2` baseline noise to fix false positives).
- **v3**: Stable & Working Perfectly. Robust regex improvements to automatically strip unstructured "References" sections natively, plus a high-visibility Electric Lime Tech-Core UI.
- **v4**: Document-wide chunking algorithm, new match percentage metrics, 1000-word performance cap, and a built-in UI button for Rebuilding Database.

## Features
- **Dual Similarity Engine:** Employs BM25 for strict lexical overlapping and `all-MiniLM-L6-v2` for semantic similarities.
- **Ayurveda Canonicalization:** Normalizes specific Ayurvedic terms (e.g. `ashwagandha` → `withania somnifera`).
- **Section Smart:** Ignores "References/Bibliography" sections to prevent false positives.
- **Detailed Match Metrics:** Provides Similarity, Exact Match, and Consecutive Match percentages for absolute clarity.
- **Explainable Output:** Highlights both the risk score and the longest exact matching snippets with sources.
- **Fast Execution & Word Limits:** Submissions are capped at 1000 words by default to guarantee instant performance. (Note: You can easily increase this limit in `app.py` for full-document scanning).

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
   python -m streamlit run app.py
   ```

## Adding More PDFs to the Corpus
To expand your database with new papers:
1. Drop the new `.pdf` files directly into the `data/pdfs/` folder.
2. Open the Streamlit App (`python -m streamlit run app.py`).
3. In the sidebar on the left, click **Rebuild Database**. The app will extract the text, build the FAISS vectors, and restart automatically.

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
