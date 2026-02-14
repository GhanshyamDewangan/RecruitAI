import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import generate_aptitude_questions

import json
import time
import uuid

# Load environment variables (reaching out to root .env)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "../../.env"))

# Database file at root level
DB_FILE = os.path.abspath(os.path.join(basedir, "../../assessments_db.json"))
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5500") # Default for local

def init_db():
    try:
        if not os.path.exists(DB_FILE):
            print(f"DEBUG: Creating new database at {DB_FILE}")
            with open(DB_FILE, "w") as f:
                json.dump({"assessments": [], "submissions": []}, f)
        else:
            print(f"DEBUG: Database found at {DB_FILE}")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize DB: {e}")

def get_db():
    init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print(f"DEBUG: Database saved successfully to {DB_FILE}")

app = FastAPI(title="Aptitude Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    jd_text: str

class EmailRequest(BaseModel):
    emails: list[str]
    job_title: str
    questions_count: int
    assessment_link: str
    questions: list[dict] # Full list of selected questions

@app.post("/generate-aptitude")
async def generate_aptitude(request: JDRequest):
    print(f"\n--- 🤖 REQUEST: Generate Aptitude Questions ---")
    if not request.jd_text.strip():
        print(f"❌ Error: JD text is empty")
        raise HTTPException(status_code=400, detail="Job Description text is empty")
    
    try:
        # Call the agent logic
        questions = generate_aptitude_questions(request.jd_text)
        print(f"✅ Success: Returning {len(questions)} questions to frontend.")
        return {"questions": questions}
    except Exception as e:
        print(f"Error generating aptitude: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-assessment")
async def send_assessment(request: EmailRequest, background_tasks: BackgroundTasks):
    print(f"\n--- 📧 REQUEST: Send Assessment to {len(request.emails)} candidates ---")
    
    # Load settings
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_user, smtp_password]):
        print(f"❌ Error: SMTP credentials missing in .env")
        raise HTTPException(status_code=500, detail="SMTP credentials not configured in .env.")

    # 1. Background Task for DB to avoid fetch error during reload
    def update_db_task():
        try:
            print(f"Step 1: Saving assessment data to tracking database...")
            token = request.assessment_link.split("token=")[-1]
            db = get_db()
            db["assessments"].append({
                "id": str(uuid.uuid4()),
                "token": token,
                "job_title": request.job_title,
                "emails": request.emails,
                "questions": request.questions,
                "timestamp": time.time(),
                "status": "Sent"
            })
            save_db(db)
            print(f"✅ Success: DB Updated for token {token}")
        except Exception as e:
            print(f"⚠️ DB Warning (Background): {e}")

    background_tasks.add_task(update_db_task)

    try:
        print(f"Step 2: Connecting to SMTP Server ({smtp_server})...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        print(f"Step 3: Sending professional emails to candidates...")
        for email in request.emails:
            msg = MIMEMultipart()
            # ... (rest of message logic remains same)
            msg['From'] = smtp_user
            msg['To'] = email
            msg['Subject'] = f"Career Opportunity | {request.job_title} Aptitude Assessment"

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #6366f1;">Congratulations!</h2>
                <p>Dear Candidate,</p>
                <p>We are pleased to inform you that your profile has been <strong>shortlisted</strong> for the <strong>{request.job_title}</strong> position.</p>
                <p>As the next step in our recruitment process, we would like you to complete a technical aptitude assessment.</p>
                
                <div style="background: #f4f4f9; padding: 20px; border-radius: 10px; border-left: 5px solid #6366f1; margin: 20px 0;">
                    <p><strong>Assessment Details:</strong></p>
                    <ul>
                        <li><strong>Format:</strong> Multiple Choice Questions (MCQs)</li>
                        <li><strong>Total Questions:</strong> {request.questions_count}</li>
                        <li><strong>Estimated Time:</strong> 30-40 Minutes</li>
                    </ul>

                    <div style="background: #fff5f5; border: 1px solid #feb2b2; padding: 15px; border-radius: 8px; margin-top: 15px;">
                        <p style="color: #c53030; margin-top: 0;"><strong>⚠️ AI Proctoring Rules (Strictly Monitored):</strong></p>
                        <ul style="color: #555; font-size: 0.9rem; padding-left: 20px;">
                            <li><strong>Camera Mandatory:</strong> Your camera must be ON throughout the session. Do not cover the lens.</li>
                            <li><strong>Eye Tracking:</strong> Please focus on the screen. Repeatedly looking away will trigger an alert.</li>
                            <li><strong>No Tab Switching:</strong> Do not switch tabs or windows. Doing so will log a "Suspicious Activity" report.</li>
                            <li><strong>No Collaboration:</strong> Ensure you are alone in a quiet room. Multiple faces will lead to disqualification.</li>
                        </ul>
                    </div>

                    <p style="text-align: center; margin-top: 25px;">
                        <a href="{request.assessment_link}" style="background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Start Assessment Now</a>
                    </p>
                </div>

                <p>Please ensure you complete this test within the next 48 hours. Use a stable internet connection and a laptop/desktop for the best experience.</p>
                <br>
                <p>Best Regards,<br><strong>Talent Acquisition Team</strong><br>RecruitAI</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            server.send_message(msg)
        
        server.quit()
        print(f"✅ Success: All emails delivered successfully.")
        return {"status": "success", "message": f"Emails sent to {len(request.emails)} candidates"}

    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        raise HTTPException(status_code=500, detail=f"SMTP Error: {str(e)}")

@app.get("/get-assessment/{token}")
async def get_assessment(token: str):
    db = get_db()
    assessment = next((a for a in db["assessments"] if a["token"] == token), None)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"questions": assessment["questions"], "job_title": assessment["job_title"]}

@app.post("/submit-assessment")
async def submit_assessment(data: dict):
    # data: { token, email, score, total, suspicious }
    print(f"\n--- 📝 REQUEST: Candidate Submission ({data.get('email')}) ---")
    try:
        db = get_db()
        db["submissions"].append({
            "token": data["token"],
            "email": data["email"],
            "score": data["score"],
            "total": data["total"],
            "timestamp": time.time(),
            "suspicious": data.get("suspicious", "Normal")
        })
        save_db(db)
        print(f"✅ Success: Candidate result recorded (Status: {data.get('suspicious')}).")
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error: Failed to record submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-analytics")
async def get_analytics():
    db = get_db()
    return db

@app.delete("/delete-assessment/{token}")
async def delete_assessment(token: str):
    db = get_db()
    db["assessments"] = [a for a in db["assessments"] if a["token"] != token]
    db["submissions"] = [s for s in db["submissions"] if s["token"] != token]
    save_db(db)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
