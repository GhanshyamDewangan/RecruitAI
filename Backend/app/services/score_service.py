
from ..core.config import get_settings
from .utils import extract_years_of_experience, extract_education_level, extract_keywords
import re

settings = get_settings()

def calculate_score(resume_text: str, jd_data: dict, semantic_score: float, page_count: int = 1) -> dict:
    # JD Data = {keywords: set, required_years: int, location: str}
    settings = get_settings()
    
    breakdown = {
        "keyword_score": 0,
        "experience_score": 0,
        "education_score": 0,
        "location_score": 0,
        "format_score": 0,
        "visual_score": 0,
        "total": 0
    }
    
    # 1. Keywords (Hybrid: Exact + Semantic)
    jd_kws = jd_data.get("keywords", set())
    exact_matches = 0
    resume_lower = resume_text.lower()
    
    if jd_kws:
        for kw in jd_kws:
            if kw.lower() in resume_lower:
                exact_matches += 1
        
        exact_ratio = exact_matches / len(jd_kws)
        # Hybrid Formula: (Exact * 0.5) + (Semantic * 0.5)
        raw_kw_score = (exact_ratio * 0.5) + (semantic_score * 0.5)
        breakdown["keyword_score"] = min(raw_kw_score * settings.keyword_weight, settings.keyword_weight)
        
    # 2. Experience
    req_years = jd_data.get("required_years", 0)
    cand_years = extract_years_of_experience(resume_text)
    
    if req_years > 0:
        ratio = min(cand_years / req_years, 1.0)
        breakdown["experience_score"] = ratio * settings.experience_weight
    else:
        breakdown["experience_score"] = settings.experience_weight # No req = full points? Or 0? Assume full if not specified.
        
    # 3. Education
    edu_level = extract_education_level(resume_text) # 0-10
    breakdown["education_score"] = (edu_level / 10) * settings.education_weight
    
    # 4. Location
    jd_loc = jd_data.get("location", "").lower()
    if jd_loc and jd_loc not in ["unknown", "remote"]:
        if jd_loc in resume_lower: 
            breakdown["location_score"] = settings.location_weight
        elif "relocate" in resume_lower:
            breakdown["location_score"] = settings.location_weight * 0.5
    elif jd_loc == "remote":
        breakdown["location_score"] = settings.location_weight
        
    # 5. Format (Simple Heuristics)
    # Check for basic headers
    headers = ["experience", "education", "skills", "projects", "summary"]
    header_count = sum(1 for h in headers if h in resume_lower)
    breakdown["format_score"] = (header_count / len(headers)) * settings.text_format_weight
    
    # 6. Formatting & Rejection Logic
    v_score = 0
    breakdown["is_rejected"] = False
    breakdown["rejection_reason"] = ""
    
    # REJECTION RULES
    if cand_years < 3 and page_count > 1:
        breakdown["is_rejected"] = True
        breakdown["rejection_reason"] = f"REJECTED: Junior Candidate ({cand_years}y exp) exceeds 1 Page limit (Has {page_count} pages)."
        return breakdown # Return immediately if rejected
        
    if page_count > 2:
        breakdown["is_rejected"] = True
        breakdown["rejection_reason"] = f"REJECTED: Resume exceeds 2 Page limit (Has {page_count} pages)."
        return breakdown

    # Penalties for formatting issues (if not rejected)
    format_penalty = 0
    if cand_years > 5 and page_count == 1:
        v_score += 5 # Bonus for conciseness
        
    # Content Structure
    bullets = resume_text.count("•") + resume_text.count("- ") 
    if bullets > 5: v_score += 10
    if header_count >= 3: v_score += 10
    if len(resume_text) > 500: v_score += 10 
    
    # Text Analysis
    alphanumeric = sum(c.isalnum() for c in resume_text)
    if len(resume_text) > 0 and (alphanumeric / len(resume_text)) < 0.5:
        format_penalty += 10 
        
    final_visual = max(0, v_score - format_penalty)
    breakdown["visual_score"] = min((final_visual / 30) * settings.visual_weight, settings.visual_weight)
    
    # TOTAL
    # Sum only the numeric score scores, NOT the rejection fields
    score_components = [
        breakdown["keyword_score"],
        breakdown["experience_score"],
        breakdown["education_score"],
        breakdown["location_score"],
        breakdown["format_score"],
        breakdown["visual_score"]
    ]
    breakdown["total"] = sum(score_components)
    
    return breakdown
