
import re
import spacy
from typing import Set, Tuple
import subprocess

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading Spacy Model 'en_core_web_sm'...")
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def clean_text(text: str) -> str:
    """Sanitize resume text."""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def extract_keywords(text: str) -> Set[str]:
    """Extract prominent Nouns and Proper Nouns."""
    doc = nlp(text.lower())
    keywords = set([token.text for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop])
    # Also noun chunks?
    chunks = set([chunk.text for chunk in doc.noun_chunks])
    keywords.update(chunks)
    return keywords

def extract_years_of_experience(text: str) -> float:
    """Extract experience using regex logic."""
    # Pattern: "5+ years", "5 years", "5 yrs"
    match = re.search(r'(\d+)[\+]?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0.0
    return 0.0

def extract_education_level(text: str) -> int:
    """Determine education weight (0-10) based on keywords."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["phd", "doctorate"]):
        return 10
    if any(k in text_lower for k in ["master", "m.tech", "ms", "mba"]):
        return 8
    if any(k in text_lower for k in ["bachelor", "b.tech", "bs", "be", "btech"]):
        return 6
    if "diploma" in text_lower:
        return 4
    return 2

def extract_name(text: str, filename: str = "") -> str:
    """Extract candidate name with fallbacks."""
    # 1. Spacy NLP (Best)
    try:
        doc = nlp(text[:300]) 
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                name = ent.text.strip()
                if name.lower() not in ["resume", "curriculum vitae", "cv", "summary", "profile", "skills", "experience"]:
                    return name
    except:
        pass

    # 2. Filename Cleanup (Reliable fallback)
    if filename:
        clean = filename.rsplit('.', 1)[0]
        # Remove extension and common separators
        clean = clean.replace("_", " ").replace("-", " ")
        # Remove common noisy words
        clean = re.sub(r'\b(resume|cv|file|copy|new|\d+)\b', '', clean, flags=re.IGNORECASE)
        # Remove extra spaces
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) > 2:
            return clean.title()

    return "Unknown Candidate"
