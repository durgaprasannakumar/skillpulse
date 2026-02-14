import re

SKILL_KEYWORDS = [
    "python", "sql", "aws", "gcp", "azure", "machine learning",
    "deep learning", "nlp", "llm", "data science", "tableau",
    "power bi", "spark", "airflow", "product analytics"
]

def extract_skills(text):
    text = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)
    return list(found)
