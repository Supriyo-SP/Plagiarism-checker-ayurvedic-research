import requests
import json
import os
import time
import re

def search_europe_pmc(query="Ayurveda", max_results=10):
    # Query for articles with PDF available
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query} AND HAS_PDF:Y&resultType=lite&format=json&pageSize={max_results}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Search failed", response.text)
        return []
    data = response.json()
    return data.get('resultList', {}).get('result', [])

def download_pdf(pmcid, output_path):
    url = f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.content.startswith(b"%PDF"):
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    return False

if __name__ == "__main__":
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    
    print("Searching for Ayurveda papers on EuropePMC...")
    results = search_europe_pmc("Ayurveda AND OPEN_ACCESS:Y", 10)
    print(f"Found {len(results)} candidate papers.")
    
    downloaded = 0
    for res in results:
        if downloaded >= 5:
            break
            
        pmcid = res.get("pmcid")
        title = res.get("title", "Unknown")
        safe_title = re.sub(r'[^\w\-_\. ]', '_', title)[:50]
        
        if pmcid:
            output_file = os.path.join(pdf_dir, f"{pmcid}_{safe_title}.pdf")
            if os.path.exists(output_file):
                print(f"Already downloaded: {pmcid}")
                downloaded += 1
                continue
                
            print(f"Downloading {pmcid} - {title[:40]}...")
            success = download_pdf(pmcid, output_file)
            if success:
                print(f" -> Successfully saved {output_file}")
                downloaded += 1
            else:
                print(f" -> Failed to download PDF for {pmcid}")
            time.sleep(1)
            
    print(f"\nDone. Downloaded {downloaded} PDFs to {pdf_dir}")
