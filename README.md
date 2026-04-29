# 🌿 Ayurvedic Plagiarism Engine [v5.0]

<p align="center">
  <img src="https://img.shields.io/badge/Status-Deployed-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Sentence--Transformers-orange?style=for-the-badge" />
</p>

An advanced, AI-powered Plagiarism Detection Tool specifically tailored for Ayurvedic Research Articles. It features a dual-engine architecture combining **Semantic Search** (Sentence Transformers + FAISS) and **Lexical Overlap** (BM25) to detect exact copy-pasting, heavy paraphrasing, and canonical Ayurvedic term substitutions.

🚀 **Live Deployment:** [https://ai-garage-assignment2-by-supriya-pal.streamlit.app/](https://ai-garage-assignment2-by-supriya-pal.streamlit.app/)

---

## 🚀 Version Evolution (Pros, Cons & Fixes)

### [v1.0] The Prototype
- **Pros:** Established the core dual-engine idea (BM25 + Semantic Search).
- **Cons:** Very noisy. False positives on generic words.
- **Fixes:** Basic pipeline established.

### [v2.0] Semantic Calibration
- **Pros:** Better understanding of paraphrased text.
- **Cons:** Still flagged references and generic medical terms.
- **Fixes:** Scaled the `all-MiniLM-L6-v2` baseline noise to eliminate low-level false positives.

### [v3.0] The Clean & Beautiful Update
- **Pros:** Beautiful "Electric Lime Tech-Core" UI. Extremely clean text processing.
- **Cons:** Only checked the first 5000 characters of a document. Canonical replacement was flawed (replaced substrings inside unrelated words).
- **Fixes:** Implemented robust regex stripping to automatically remove unstructured "References" and "Bibliography" sections, preventing massive false positives. 

### [v4.0] High-Fidelity & Document Chunking
- **Pros:** Can process entire documents via 250-word sliding windows. Added detailed metrics (Consecutive Match %, Exact Match %).
- **Cons:** Scaling BM25 alongside Semantic Search caused a math bug where long documents triggered 100% plagiarism false positives. Cold-starting the app on empty deployments crashed it.
- **Fixes:** Added the "Rebuild Database" sidebar button. Replaced character-truncation with a 1000-word performance cap.

### [v5.0] The Production-Ready Engine (Current)
- **Pros:** 100% stable. Flawless mathematical scoring. Cold-start deployment safety.
- **Cons:** Dependent on local `chunks.json` for lightweight deployments.
- **Fixes:** 
  - **Cold-Start Fix:** Deploys instantly via a pre-processed `chunks.json` without needing to push heavy, private PDF files to GitHub.
  - **Math Fix:** Removed unbounded BM25 normalization causing false 100% positives. Overall Confidence is now safely anchored to strictly-bounded Semantic similarity, while Exact Match percentage drives the Lexical UI.
  - **Bug Fix:** Protected `PlagiarismDetector` initialization so missing indexes degrade gracefully instead of throwing C++ `faiss` crashes.

---

## ⚠️ Flaws & Current Limitations
1. **Model Domain Knowledge:** `all-MiniLM-L6-v2` is a general-purpose semantic model. While we use canonical term replacement (e.g. `ashwagandha` → `withania somnifera`), a deeply fine-tuned Ayurvedic BioBERT would yield superior semantic nuance.
2. **Hard Word Limits:** Currently capped at **1000 words** per submission to prevent Streamlit from timing out on massive PDFs. This can be manually increased in `app.py`, but it slows down performance linearly.
3. **Table & Image Extraction:** The system purely extracts text via `pdfplumber`. Any plagiarism disguised as images or complex tables will bypass the radar entirely.
4. **Memory Intensive:** Generating and searching massive FAISS vectors completely in RAM means the app might struggle if scaled to millions of documents without a dedicated vector database (like Pinecone or Milvus).

---

## 🛠️ Features
- **Dual Similarity Engine:** Strict lexical overlap (BM25) + paraphrased idea capture (MiniLM).
- **Ayurveda Canonicalization:** Standardizes scientific terminology before searching.
- **Section Smart:** Automatically ignores reference/bibliography sections to prevent false flags.
- **Detailed Match Metrics:** UI provides granular breakdown: Similarity, Exact Match, and Consecutive Match percentages.
- **Serverless-Friendly:** Optimized to deploy seamlessly on Streamlit Community Cloud using pre-processed `chunks.json`.

---

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "Ayurvedic plagiarism checker"
   ```

2. **Setup Virtual Environment (Python 3.9+):**
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

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## 📚 Managing the Corpus
**How to add new PDFs to your database:**
1. Drop your new `.pdf` files into the `data/pdfs/` folder on your local machine.
2. Start the app locally (`streamlit run app.py`).
3. Open the left sidebar and click **Rebuild Database**. The app will automatically extract the text, build the FAISS index, and update `data/chunks.json`.
4. *Important for Deployment:* Run `git commit -am "added new pdfs"` and push to deploy. Streamlit will use the updated `chunks.json` instantly without needing the PDFs!
