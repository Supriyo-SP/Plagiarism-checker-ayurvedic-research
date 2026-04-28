import os

mock_text_1 = """Abstract
Ayurveda is a traditional system of medicine. Triphala churna is widely used for digestive health. It contains three fruits: amla, bibhitaki, and haritaki.
Introduction
The use of withania somnifera (ashwagandha) has shown significant stress reduction.
Methods
We extracted the alkaloids from tulsi leaves and measured their concentration.
Results
Bacopa monnieri (brahmi) improved memory retention in subjects.
Conclusion
Traditional Ayurvedic formulations are effective.
References
1. Gupta et al. Medicine. 2021.
2. Singh, Journal of Ayurveda.
"""

mock_text_2 = """Abstract
This paper reviews the efficacy of Ayurvedic formulations.
Introduction
Stress is a common ailment. Ashwagandha acts as an adaptogen to reduce cortisol levels.
Body
The antacid properties of Emblica officinalis (amla) are well documented. Ocimum sanctum (tulsi) also provides immunomodulatory effects.
We also observed memory improvements from Brahmi extracts.
Conclusion
Ayurvedic herbs provide broad-spectrum benefits.
Bibliography
Smith J. Herbs and Health. 2022.
"""

def generate():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "texts")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "article_1.txt"), "w") as f:
        f.write(mock_text_1)
    with open(os.path.join(out_dir, "article_2.txt"), "w") as f:
        f.write(mock_text_2)

if __name__ == "__main__":
    generate()
