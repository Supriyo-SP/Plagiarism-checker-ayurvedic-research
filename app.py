import streamlit as st
import os
import tempfile
from pipeline.similarity import PlagiarismDetector

# Ensure pipeline modules can be found
st.set_page_config(page_title="Ayurvedic Plagiarism Checker", layout="wide", page_icon="🌿")

@st.cache_resource
def load_detector():
    base_dir = os.path.dirname(__file__)
    index_dir = os.path.join(base_dir, "data", "index")
    
    # Cold-start Deployment Fix: Bootstrap data if it doesn't exist
    if not os.path.exists(os.path.join(index_dir, "vector.index")):
        with st.spinner("Initializing AI Core... Building FAISS Semantic Index (This only happens once on deployment)..."):
            from pipeline.extract import extract_all
            from pipeline.preprocess import process_all
            from pipeline.index import build_index
            
            pdf_dir = os.path.join(base_dir, "data", "pdfs")
            texts_dir = os.path.join(base_dir, "data", "texts")
            chunks_file = os.path.join(base_dir, "data", "chunks.json")
            
            # Automatically extract raw text from any PDFs uploaded to the corpus
            if os.path.exists(pdf_dir):
                extract_all(pdf_dir, texts_dir)
                
            # Preprocess the data into canonical chunks
            process_all(texts_dir, chunks_file)
            
            # Build embeddings and FAISS/BM25 indexes
            build_index(chunks_file, index_dir)
            
            st.success("✅ AI Engine Initialized!")
            # Streamlit rerun is not needed because it will just fall through and load the detector below
            
    from pipeline.similarity import PlagiarismDetector
    return PlagiarismDetector(index_dir)

def main():
    # Inject Custom Tech Core CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    /* Background and fonts */
    .stApp {
        background-color: #050505;
    }
    html, body, [class*="css"]  {
        font-family: 'Share Tech Mono', monospace !important;
        color: #a0a0a0;
    }
    
    /* Electric Lime Accents for Headers */
    h1, h2, h3, h4, h5, p {
        color: #ccff00 !important;
        font-family: 'Share Tech Mono', monospace;
    }
    
    /* Metric Score Text */
    div[data-testid="stMetricValue"] {
        color: #ccff00 !important;
        text-shadow: 0 0 10px rgba(204, 255, 0, 0.4);
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #050505;
        color: #ccff00;
        border: 1px solid #ccff00;
        box-shadow: 0 0 4px rgba(204,255,0,0.3);
        border-radius: 0;
        transition: 0.3s all ease-in-out;
        font-family: 'Share Tech Mono', monospace;
    }
    .stButton>button:hover {
        background-color: rgba(204, 255, 0, 0.1);
        color: #e6ff66;
        border-color: #e6ff66;
        box-shadow: 0 0 10px rgba(204,255,0,0.5);
    }
    
    /* Text Area Override */
    .stTextArea textarea {
        background-color: #111 !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 2px;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .stTextArea textarea:focus {
        border: 1px solid #ccff00 !important;
        box-shadow: 0 0 5px rgba(204,255,0,0.3);
        color: #ffffff !important;
    }
    
    /* Dashboard Expanders */
    div[data-testid="stExpander"] {
        border-color: #333 !important;
        background-color: #0a0a0a;
    }
    
    /* Decorative UI Elements */
    hr {
        border-color: #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; text-transform: uppercase;'>[ Ayurvedic Plagiarism Engine // v4.0 ]</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #777 !important;'>Semantic + Lexical Signal Detection Grid</p><hr/>", unsafe_allow_html=True)
    
    detector = load_detector()
    
    if detector is None:
        st.warning("⚠️ Index not found. Please run the indexing pipeline first.")
        return

    # Add Sidebar for Rebuilding Index
    st.sidebar.markdown("## System Controls")
    if st.sidebar.button("Rebuild Database", help="Use this if you added new PDFs to the data/pdfs folder", type="primary", use_container_width=True):
        with st.spinner("Rebuilding FAISS and BM25 Indexes from PDFs..."):
            base_dir = os.path.dirname(__file__)
            index_dir = os.path.join(base_dir, "data", "index")
            pdf_dir = os.path.join(base_dir, "data", "pdfs")
            texts_dir = os.path.join(base_dir, "data", "texts")
            chunks_file = os.path.join(base_dir, "data", "chunks.json")
            
            from pipeline.extract import extract_all
            from pipeline.preprocess import process_all
            from pipeline.index import build_index
            
            extract_all(pdf_dir, texts_dir)
            process_all(texts_dir, chunks_file)
            build_index(chunks_file, index_dir)
            
            st.sidebar.success("Database Rebuilt Successfully!")
            st.cache_resource.clear()
            st.rerun()
        
    st.markdown("### Submission Input")
    input_method = st.radio("Choose input method:", ("Plain Text", "PDF Upload"))
    
    query_text = ""
    if input_method == "Plain Text":
        query_text = st.text_area("Paste text here...", height=200, placeholder="Enter an abstract or section of an Ayurvedic research paper...")
    else:
        uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
                
            from pipeline.extract import extract_text_from_pdf
            st.info("Extracting text from PDF...")
            raw_text = extract_text_from_pdf(tmp_path)
            os.remove(tmp_path)
            
            if raw_text:
                st.success(f"Extracted {len(raw_text.split())} words.")
                query_text = raw_text
                with st.expander("Show extracted text"):
                    st.write(query_text)
            else:
                st.error("Failed to extract text from PDF.")
                
    if st.button("🔍 Check Plagiarism", type="primary", use_container_width=True):
        if len(query_text.split()) < 10:
            st.error("Please enter at least 10 words to analyze.")
            return
            
        with st.spinner("Analyzing against Ayurvedic Database..."):
            res = detector.detect(query_text[:5000]) # analyzing up to 5000 chars for demo
            
        score = res["overall_score"]
        
        st.markdown("---")
        st.markdown("## Analysis Results")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if score >= 80:
                color = "red"
                risk = "HIGH RISK"
            elif score >= 50:
                color = "orange"
                risk = "MODERATE RISK"
            else:
                color = "green"
                risk = "LOW RISK"
                
            st.metric(label="Overall Plagiarism Confidence", value=f"{score:.1f}%")
            st.markdown(f"<h3 style='color: {color};'>{risk}</h3>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("### Top Matched Sources")
            if not res["top_matches"]:
                st.info("No substantial matches found in the corpus.")
            else:
                for match in res["top_matches"]:
                    with st.expander(f"📄 Source: {match['source']} | Match: {match['type']} | Sim: {match['similarity_percentage']:.1f}%"):
                        st.markdown(f"**Section Matched:** {match['section']}")
                        
                        col_m1, col_m2, col_m3 = st.columns(3)
                        col_m1.metric("Similarity", f"{match['similarity_percentage']:.1f}%")
                        col_m2.metric("Exact Match", f"{match['exact_match_percentage']:.1f}%")
                        col_m3.metric("Consecutive Match", f"{match['consecutive_percentage']:.1f}%")
                        
                        if match['exact_match'] and len(match['exact_match'].split()) >= 3:
                            st.markdown(f"**Longest Exact Match Segment:**\n> {match['exact_match']}")
                            
                        st.markdown(f"**Overlapping Context:**\n> {match['text']}")
                        
        st.info("💡 **How it works:** Dual-engine architecture. **Semantic Search** captures paraphrased ideas using sentence-transformers, while **Lexical BM25 Search** catches direct copy-pasting.")

if __name__ == "__main__":
    main()
