import os
import json
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

def build_index(chunks_file, out_dir):
    if not os.path.exists(chunks_file):
        print(f"Chunks file {chunks_file} not found.")
        return
        
    with open(chunks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    flat_chunks = []
    metadata = []
    
    for doc_idx, doc in enumerate(data):
        source = doc["source"]
        for chunk_idx, chunk in enumerate(doc["chunks"]):
            flat_chunks.append(chunk["text"])
            metadata.append({
                "source": source,
                "section": chunk["section"],
                "text": chunk["text"],
                "doc_idx": doc_idx,
                "chunk_idx": chunk_idx
            })
            
    if not flat_chunks:
        print("No chunks found to index.")
        return

    print("Loading SentenceTransformer model...")
    # Using all-MiniLM-L6-v2 as a fast and effective baseline semantic model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Encoding {len(flat_chunks)} chunks...")
    embeddings = model.encode(flat_chunks, convert_to_numpy=True)
    
    # Initialize FAISS index
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim) # Inner product for cosine sim (requires normalized L2)
    faiss.normalize_L2(embeddings)
    faiss_index.add(embeddings)
    
    # Build BM25 index
    print("Building BM25 index...")
    # Basic tokenization
    tokenized_chunks = [chunk.lower().split() for chunk in flat_chunks]
    bm25_index = BM25Okapi(tokenized_chunks)
    
    # Save everything
    os.makedirs(out_dir, exist_ok=True)
    
    faiss.write_index(faiss_index, os.path.join(out_dir, "vector.index"))
    
    with open(os.path.join(out_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(os.path.join(out_dir, "bm25.pkl"), "wb") as f:
        pickle.dump(bm25_index, f)
        
    print(f"Indexing complete. Saved {faiss_index.ntotal} chunks into FAISS, Metadata, and BM25.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    chunks_file = os.path.join(base_dir, "data", "chunks.json")
    out_dir = os.path.join(base_dir, "data", "index")
    build_index(chunks_file, out_dir)
