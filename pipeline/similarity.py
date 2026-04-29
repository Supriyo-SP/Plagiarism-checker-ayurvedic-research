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
        
        try:
            self.faiss_index = faiss.read_index(os.path.join(index_dir, "vector.index"))
            with open(os.path.join(index_dir, "bm25.pkl"), "rb") as f:
                self.bm25 = pickle.load(f)
            with open(os.path.join(index_dir, "metadata.json"), "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load index data: {e}")
            self.metadata = []
            self.faiss_index = None
            self.bm25 = None
        
    def detect(self, query_text):
        if not self.metadata:
            return {"overall_score": 0, "top_matches": []}
            
        # Chunk the query to match the indexing strategy
        query_words = query_text.split()
        chunk_size = 250
        overlap = 50
        query_chunks = []
        
        if len(query_words) > chunk_size:
            for i in range(0, len(query_words), chunk_size - overlap):
                chunk = " ".join(query_words[i:i + chunk_size])
                if len(chunk.split()) > 20:
                    query_chunks.append(chunk)
        else:
            query_chunks = [query_text]
            
        if not query_chunks:
            return {"overall_score": 0, "top_matches": []}
            
        all_results = []
        max_score_overall = 0.0
        
        # We will keep track of how many chunks are highly plagiarized for a better overall score
        highly_plagiarized_chunks = 0
        
        for q_chunk in query_chunks:
            # 1. Semantic Search
            query_embedding = self.model.encode([q_chunk], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            k = min(5, len(self.metadata))
            sem_scores, sem_indices = self.faiss_index.search(query_embedding, k)
            
            chunk_max_sem = max(sem_scores[0]) if len(sem_scores[0]) > 0 else 0
            
            # 2. Lexical Search (BM25)
            tokenized_query = q_chunk.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            top_k_bm25 = np.argsort(bm25_scores)[::-1][:k]
            
            chunk_max_lex = max(bm25_scores) if len(bm25_scores) > 0 else 0
            
            # Normalize BM25 assuming ~30.0 is a very high match
            norm_lex = min(1.0, chunk_max_lex / 30.0)
            
            # Blend lexical and semantic
            chunk_overall = max(chunk_max_sem, norm_lex)
            if chunk_overall > max_score_overall:
                max_score_overall = chunk_overall
                
            if chunk_overall > 0.85: # Threshold for high confidence plagiarism
                highly_plagiarized_chunks += 1
            
            for idx in top_k_bm25:
                if bm25_scores[idx] > 0:
                    meta = self.metadata[idx]
                    all_results.append({
                        "type": "Lexical",
                        "source": meta["source"],
                        "section": meta["section"],
                        "score": float(bm25_scores[idx]),
                        "text": meta["text"],
                        "q_chunk": q_chunk
                    })
                    
            for i, idx in enumerate(sem_indices[0]):
                meta = self.metadata[idx]
                all_results.append({
                    "type": "Semantic",
                    "source": meta["source"],
                    "section": meta["section"],
                    "score": float(sem_scores[0][i]),
                    "text": meta["text"],
                    "q_chunk": q_chunk
                })
                
        # To ensure an exact uploaded PDF gives 100%, we look at max_score_overall
        if max_score_overall < 0.45:
            overall_score = 0.0
        else:
            # Scale 0.45 -> 1.0 to 0 -> 100%
            overall_score = min(100.0, ((max_score_overall - 0.45) / 0.55) * 100.0)
            
        # Filter out noisy matches
        filtered_results = [r for r in all_results if (r["type"] == "Semantic" and r["score"] >= 0.45) or (r["type"] == "Lexical" and r["score"] >= 5.0)]
        
        # Sort by semantic score
        sorted_semantic = sorted([r for r in filtered_results if r["type"] == "Semantic"], key=lambda x: x["score"], reverse=True)
        other_results = sorted([r for r in filtered_results if r["type"] == "Lexical"], key=lambda x: x["score"], reverse=True)
        
        # Make a combined list of unique sources
        top_matches = []
        seen = set()
        for r in sorted_semantic + other_results:
            fingerprint = f"{r['source']}_{r['text'][:20]}"
            if fingerprint not in seen:
                seen.add(fingerprint)
                
                # Calculate new metrics for the UI based on the specific query chunk
                q_words = r["q_chunk"].lower().split()
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
                    sim_pct = max(0.0, min(100.0, ((r["score"] - 0.45) / 0.55) * 100.0))
                else:
                    sim_pct = min(100.0, (r["score"] / 30.0) * 100.0)
                    
                r["consecutive_percentage"] = consecutive_pct
                r["exact_match"] = exact_match_str
                r["exact_match_percentage"] = exact_match_pct
                r["similarity_percentage"] = sim_pct
                
                top_matches.append(r)
                if len(top_matches) >= 5:
                    break
                
        return {
            "overall_score": overall_score,
            "top_matches": top_matches
        }

# Simple test if run directly
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    index_dir = os.path.join(base_dir, "data", "index")
    detector = PlagiarismDetector(index_dir)
    res = detector.detect("Ashwagandha has been shown to reduce stress through cortisol reduction")
    print("Test Query Result:")
    print(json.dumps(res, indent=2))
