import os
import re
import json

# Canonical term dictionary for Sanskrit/Ayurvedic terms to English representation
CANONICAL_TERMS = {
    "triphala churna": "triphala",
    "ashwagandha": "withania somnifera",
    "amla": "emblica officinalis",
    "brahmi": "bacopa monnieri",
    "tulsi": "ocimum sanctum"
}

def normalize_text(text):
    """Lowercase and simple unicode normalization."""
    text = text.lower()
    for term, canonical in CANONICAL_TERMS.items():
        text = text.replace(term, canonical)
    return text

def remove_references(text):
    """Attempt to find and remove references/bibliography sections robustly."""
    # Using MULTILINE so ^ matches the start of any line, allowing optional numbering (e.g. "7. References")
    pattern = r"^(?:\d+\.?\s*)?(?:REFERENCES?|BIBLIOGRAPHY)\s*$"
    
    # Find all possible matches for the references header
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
    
    if matches:
        # Common issue: 'References' could be mentioned in the abstract or table of contents.
        # We only want the actual references section which typically appears in the last half of the document.
        for m in reversed(matches):
            if m.start() > len(text) * 0.4:
                return text[:m.start()]
                
    # Fallback: occasionally PDF parsers drop the newlines and we just get "\n References \n"
    fallback_pattern = r"\n\s*(?:REFERENCES?|BIBLIOGRAPHY)\s*\n"
    matches_fb = list(re.finditer(fallback_pattern, text, flags=re.IGNORECASE))
    if matches_fb:
        for m in reversed(matches_fb):
            if m.start() > len(text) * 0.4:
                return text[:m.start()]

    return text

def section_split(text):
    """Rudimentary section splitter."""
    sections = {}
    
    abstract_match = re.search(r"\babstract\b", text[:2000], re.IGNORECASE)
    intro_match = re.search(r"\bintroduction\b", text[:5000], re.IGNORECASE)
    
    if abstract_match and intro_match and intro_match.start() > abstract_match.start():
        sections["Abstract"] = text[abstract_match.end():intro_match.start()].strip()
        sections["Body"] = text[intro_match.end():].strip()
    else:
        sections["Body"] = text.strip()
        
    return sections

def chunk_text(text, chunk_size=250, overlap=50):
    """Chunk text into ~N words."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.split()) > 20: # Minimum chunk size constraint
            chunks.append(chunk)
            
    return chunks

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    text = remove_references(text)
    text = normalize_text(text)
    sections = section_split(text)
    
    all_chunks = []
    for section_name, section_text in sections.items():
        section_chunks = chunk_text(section_text)
        for chunk in section_chunks:
            all_chunks.append({
                "section": section_name,
                "text": chunk
            })
            
    return all_chunks

def process_all(input_dir, output_file):
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return
        
    txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    all_data = []
    
    for txt_file in txt_files:
        print(f"Processing: {txt_file}")
        chunks = process_file(os.path.join(input_dir, txt_file))
        all_data.append({
            "source": txt_file.replace(".txt", ""),
            "chunks": chunks
        })
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print(f"Preprocessing complete. Saved {len(all_data)} documents ({sum(len(d['chunks']) for d in all_data)} chunks) to {output_file}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_dir = os.path.join(base_dir, "data", "texts")
    output_file = os.path.join(base_dir, "data", "chunks.json")
    process_all(input_dir, output_file)
