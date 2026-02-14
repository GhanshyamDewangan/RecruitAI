# 🧬 Agentic ATS Scorer Suite (v4.0)

### _The Intelligence-First Recruitment Ecosystem_

[![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)]()
[![AI Model](<https://img.shields.io/badge/AI-Llama%203.3%20(70B)-blue?style=flat-square&logo=meta&logoColor=white>)]()
[![Integration](https://img.shields.io/badge/Integration-Gmail_API-red?style=flat-square&logo=gmail&logoColor=white)]()
[![Database](https://img.shields.io/badge/VectorDB-Chroma-orange?style=flat-square)]()

---

## 🚀 Overview

The **Agentic ATS Scorer Suite** is a unified ecosystem designed to automate the complete recruitment lifecycle. It transitions from role definition to candidate performance analysis seamlessly.

### 🍱 Module Breakdown

#### 1. ✨ JD Generator (`/JD_Generator`)

The entry point of the hiring funnel. It removes the guesswork from drafting role requirements.

- **AI Engine**: Llama 3.3 (70B) via Groq.
- **Inputs**: Company Name, Industry, Role Title, Experience Level, Work Mode, and **Salary (LPA)**.
- **Features**: Generates ATS-optimized, professional JDs formatted with clear headers and bullet points.
- **Output**: Structured markdown/text JD ready for posting or analysis.

#### 2. 🧬 Resume Screening Agent (`/Backend` & `/Frontend`)

The semantic core that finds the "Perfect Match" from thousands of applications.

- **Semantic Matching**: Uses ChromaDB vector embeddings for context-aware screening.
- **Hybrid Scoring**: Combines NLP for experience extraction, keyword matching, and visual formatting analysis.
- **Integrations**: Direct Gmail API fetch to scan resumes straight from your inbox.
- **Reporting**: Generates stratified report folders (Shortlisted, Not Selected, Rejected).

#### 3. 🧠 Aptitude Generator (`/Aptitude_Generator`)

The evaluation layer that verifies candidate claims.

- **Contextual MCQs**: Reads the specific JD generated/provided and creates 25 highly relevant technical/aptitude questions.
- **Automated Delivery**: Integrates SMTP to send personalized test invites to candidates.
- **Smart Proctoring**: Includes an AI-monitored dashboard to track candidate browser behavior, score, and submission status.
- **Analytics**: Tracking dashboard for HR to view candidate performance at a glance.

---

## 🔄 End-to-End Workflow

Follow these steps to experience the full agentic recruitment journey:

1.  **Generate Role Context**: Launch the **JD Generator**. Input your requirements (including salary). AI generates a specialized JD.
2.  **Screen Talent**: Launch the **Resume Screening Agent**. Use the newly generated JD to filter resumes from local storage or Gmail. Set a 'Top N' cutoff to find your elite candidates.
3.  **Create Assessment**: Launch the **Aptitude Generator**. Paste your JD to generate 25 targeted multiple-choice questions.
4.  **Invite Candidates**: Select the best questions, enter candidate emails, and send the professional assessment link.
5.  **Evaluate & Hire**: Candidates take the AI-proctored test. Review the **Analytics Dashboard** to make final hiring decisions based on both resume score and test performance.

---

## 🖥️ System Setup & Execution

### 1. Prerequisites

- Python 3.10+
- Groq API Key (Place in `.env` in root)
- Gmail `credentials.json` (for Resume Screening)

### 2. Parallel Execution (Recommended)

You can run all backend services simultaneously using our optimized scripts:

**For Windows (Batch File):**

```powershell
.\run_backends.bat
```

**Using Python Script:**

```powershell
python run_all_backends.py
```

### 3. Service Ports

| Service                 | Module                   | Port   |
| :---------------------- | :----------------------- | :----- |
| **Recruitment Backend** | Resume Screening API     | `8000` |
| **JD Generator API**    | Job Description Creation | `8001` |
| **Aptitude API**        | Assessment & Proctoring  | `8002` |

---

## ⚙️ Directory Structure

```text
Agentic_ATS_Scorer/
├── Aptitude_Generator/    # Assessment Engine (Port 8002)
│   ├── backend/           # FastAPI Assessment Logic
│   └── frontend/          # Proctoring & Question UI
├── JD_Generator/          # Role Creation Engine (Port 8001)
│   ├── backend/           # FastAPI JD AI Logic
│   └── frontend/          # JD Creation Dashboard
├── Backend/               # Resume Screening API (Port 8000)
├── Frontend/              # Main ATS Dashboard
├── run_all_backends.py    # Multi-service runner
└── run_backends.bat       # Windows automation script
```

---

### _Refined. Automated. Agentic._

**Built with ❤️ for Modern Talent Teams**
