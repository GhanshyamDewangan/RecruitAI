import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "../../.env"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_aptitude_questions(jd_text: str):
    """
    Analyzes the Job Description and generates 25 relevant MCQ questions.
    """
    
    prompt = f"""
    You are an expert technical interviewer and recruitment specialist.
    Analyze the following Job Description (JD) and generate 25 high-quality Multiple Choice Questions (MCQs).
    
    Guidelines:
    1. The questions must be directly relevant to the skills, experience level, and responsibilities mentioned in the JD.
    2. Include a mix of:
       - Technical/Domain Knowledge (Primary focus)
       - Logical Reasoning/Problem Solving
       - Role-specific situational questions
    3. For each question, provide 4 options and clearly indicate the correct answer.
    4. Ensure the difficulty level matches the seniority level mentioned in the JD.
    5. CRITICAL: DO NOT mention any specific company names, organization names, or internal team names in the questions. The questions should be general technical/professional questions suitable for any assessment.
    
    Format: Return ONLY a JSON object with a key "questions" containing a list of objects.
    Each object in the "questions" list must have:
    - "id": (e.g., "Q1")
    - "question": "The question text"
    - "options": ["Option A", "Option B", "Option C", "Option D"]
    - "answer": "The correct option text"

    JOB DESCRIPTION:
    {jd_text}
    """

    print(f"\n--- 🚀 AGENT START: Analysing Job Description ---")
    try:
        print(f"Step 1: Connecting to Groq AI (Llama-3.3-70b)...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional hiring assessment creator. Output only valid JSON lists."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={ "type": "json_object" }
        )
        
        print(f"Step 2: Receiving AI response and parsing JSON...")
        # Parse result
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        
        # Flexible parsing in case AI wraps it in a key
        final_questions = []
        if isinstance(data, list):
            final_questions = data
        elif isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    final_questions = data[key]
                    break
        
        print(f"✅ SUCCESS: Generated {len(final_questions)} professional questions.")
        return final_questions

    except Exception as e:
        print(f"❌ AGENT ERROR: {e}")
        raise e
