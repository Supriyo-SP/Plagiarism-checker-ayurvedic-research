import os
import json
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

class PlagiarismDetector:
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.faiss_index = faiss.read_index(os.path.join(index_dir, "vector.index"))
        
        with open(os.path.join(index_dir, "bm25.pkl"), "rb") as f:
            self.bm25 = pickle.load(f)
            
        with open(os.path.join(index_dir, "metadata.json"), "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        # Section weights
        self.weights = {
            "Abstract": 0.2,
            "Methods": 0.4,
            "Results": 0.3,
            "Discussion": 0.3,
            "Body": 0.3, # Fallback
            "Conclusion": 0.1
        }
        
    def detect(self, query_text):
        if not self.metadata:
            return {"overall_score": 0, "top_matches": []}
            
        # 1. Semantic Search
        query_embedding = self.model.encode([query_text], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        k = min(5, len(self.metadata))
        sem_scores, sem_indices = self.faiss_index.search(query_embedding, k)
        
        # 2. Lexical Search (BM25)
        tokenized_query = query_text.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_k_bm25 = np.argsort(bm25_scores)[::-1][:k]
        
        results = []
        for idx in top_k_bm25:
            if bm25_scores[idx] > 0:
                meta = self.metadata[idx]
                results.append({
                    "type": "Lexical",
                    "source": meta["source"],
                    "section": meta["section"],
                    "score": float(bm25_scores[idx]), # absolute BM25 score
                    "text": meta["text"]
                })
                
        for i, idx in enumerate(sem_indices[0]):
            meta = self.metadata[idx]
            results.append({
                "type": "Semantic",
                "source": meta["source"],
                "section": meta["section"],
                "score": float(sem_scores[0][i]), # Cosine sim (0-1)
                "text": meta["text"]
            })
            
        max_semantic = max(sem_scores[0]) if len(sem_scores[0]) > 0 else 0
        overall_score = min(100, max_semantic * 100)
        
        # Return top matches, sorted by semantic score for simplicity
        sorted_semantic = [r for r in results if r["type"] == "Semantic"]
        
        # Make a combined list of unique sources
        top_matches = []
        seen = set()
        for r in sorted_semantic + results:
            fingerprint = f"{r['source']}_{r['text'][:20]}"
            if fingerprint not in seen:
                seen.add(fingerprint)
                top_matches.append(r)
                
        return {
            "overall_score": overall_score,
            "top_matches": top_matches[:5]
        }

# Simple test if run directly
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    index_dir = os.path.join(base_dir, "data", "index")
    detector = PlagiarismDetector(index_dir)
    res = detector.detect("Ashwagandha has been shown to reduce stress through cortisol reduction")
    print("Test Query Result:")
    print(json.dumps(res, indent=2))
