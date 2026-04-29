import os
import json
import faiss
import numpy as np
import pickle
import difflib
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
        
        # Adjusting the raw cosine similarity into a 0-100% "severity" scale.
        # all-MiniLM-L6-v2 typically scores ~0.1 - 0.4 for completely unrelated text.
        # We treat < 0.45 as 0% plagiarism.
        if max_semantic < 0.45:
            overall_score = 0.0
        else:
            overall_score = min(100.0, ((max_semantic - 0.45) / 0.50) * 100.0)
            
        # Filter out noisy, unrelated semantic matches from muddying the results
        results = [r for r in results if (r["type"] == "Semantic" and r["score"] >= 0.45) or (r["type"] == "Lexical")]
        
        # Return top matches, sorted by semantic score for simplicity
        sorted_semantic = [r for r in results if r["type"] == "Semantic"]
        
        # Make a combined list of unique sources
        top_matches = []
        seen = set()
        for r in sorted_semantic + results:
            fingerprint = f"{r['source']}_{r['text'][:20]}"
            if fingerprint not in seen:
                seen.add(fingerprint)
                
                # Calculate new metrics for the UI
                q_words = query_text.lower().split()
                t_words = r["text"].lower().split()
                
                if q_words and t_words:
                    matcher = difflib.SequenceMatcher(None, q_words, t_words)
                    match = matcher.find_longest_match(0, len(q_words), 0, len(t_words))
                    
                    consecutive_pct = (match.size / len(q_words)) * 100.0
                    longest_match_words = q_words[match.a : match.a + match.size]
                    exact_match_str = " ".join(longest_match_words)
                    
                    matching_blocks = matcher.get_matching_blocks()
                    exact_words = sum(block.size for block in matching_blocks if block.size >= 3)
                    exact_match_pct = (exact_words / len(q_words)) * 100.0
                else:
                    consecutive_pct = 0.0
                    exact_match_str = ""
                    exact_match_pct = 0.0
                    
                if r["type"] == "Semantic":
                    sim_pct = max(0.0, min(100.0, ((r["score"] - 0.45) / 0.50) * 100.0))
                else:
                    sim_pct = min(100.0, (r["score"] / 20.0) * 100.0)
                    
                r["consecutive_percentage"] = consecutive_pct
                r["exact_match"] = exact_match_str
                r["exact_match_percentage"] = exact_match_pct
                r["similarity_percentage"] = sim_pct
                
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
