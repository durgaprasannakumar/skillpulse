import google.generativeai as genai
from src.config import Config

def enrich_skills_with_ai(description):
    if not Config.GEMINI_API_KEY:
        return []

    genai.configure(api_key=Config.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Extract the top 5 standardized technical skills from this job description.
    Return as a comma-separated list.

    Description:
    {description[:2000]}
    """

    response = model.generate_content(prompt)
    skills = response.text.strip().split(",")
    return [s.strip().lower() for s in skills]