# 🎓 CampusLens AI
> AI-powered syllabus analyzer for OSU students — know before you enroll.

Built for **GDG Winter 2026 Hackathon** @ Oregon State University.

---

## 🚀 Quick Start (5 minutes)

### 1. Clone & Enter Project
```bash
git clone https://github.com/hari-hara-sudharsan-j/CampusLens-AI.git
cd CampusLens-AI
```

### 2. Set Up Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
# Get one free at: https://console.anthropic.com/
```

### 3. Run the Backend
```bash
# Make sure you're in /backend with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
You should see: `Uvicorn running on http://0.0.0.0:8000`

### 4. Open the Frontend
```bash
# Just open in your browser — no build step needed!
open ../frontend/index.html
# OR double-click frontend/index.html in Finder/Explorer
```

### 5. Test It!
- Go to http://localhost:8000/docs for the interactive API docs (Swagger UI)
- Drop any OSU syllabus PDF into the frontend
- Watch the magic happen 🎉

---

## 📁 Project Structure
```
campuslens-ai/
├── backend/
│   ├── main.py              # FastAPI app — all routes here
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variable template
├── frontend/
│   └── index.html           # Single-file frontend (HTML/CSS/JS)
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint    | Description                        |
|--------|-------------|------------------------------------|
| POST   | `/analyze`  | Analyze a single syllabus PDF      |
| POST   | `/compare`  | Compare two syllabus PDFs          |
| GET    | `/health`   | Health check                       |
| GET    | `/docs`     | Swagger interactive API docs       |

### Example: Analyze a Syllabus
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@my_syllabus.pdf"
```

### Example Response
```json
{
  "course_name": "CS 361 - Software Engineering I",
  "course_code": "CS 361",
  "instructor": "Dr. Smith",
  "credits": 4,
  "difficulty_score": 7,
  "difficulty_label": "Hard",
  "weekly_hours_min": 10,
  "weekly_hours_max": 15,
  "workload_breakdown": {
    "lectures": "3 hrs/week",
    "assignments": "4-6 hrs/week",
    "projects": "3-5 hrs/week"
  },
  "key_topics": ["Agile", "UML", "Testing", "Git", "Design Patterns"],
  "skills_you_will_learn": ["Team collaboration", "Software design", "Version control"],
  "red_flags": [
    {"flag": "Group project with peer evaluation", "severity": "medium"},
    {"flag": "No late submissions accepted", "severity": "high"}
  ],
  "green_flags": ["Clear rubrics provided", "Weekly office hours"],
  "grade_breakdown": [
    {"component": "Assignments", "weight": 40},
    {"component": "Project", "weight": 35},
    {"component": "Final", "weight": 25}
  ],
  "study_strategies": ["Start assignments early", "Form study groups", "Attend office hours"],
  "survival_tips": ["Read the requirements twice before coding", "Git commit often"],
  "recommended_for": "Students who enjoy collaborative work and system design",
  "not_recommended_for": "Students who prefer individual work or dislike group dynamics",
  "overall_summary": "A foundational course in software engineering practices..."
}
```

---

## 🛠 Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Frontend  | HTML5, CSS3, Vanilla JS       |
| Backend   | Python 3.11+, FastAPI         |
| AI        | Anthropic Claude API          |
| PDF       | pdfplumber                    |
| Deploy    | Render (free tier)            |

---

## ☁️ Deploy to Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `ANTHROPIC_API_KEY=your_key`
6. Deploy! Update the `API` constant in `frontend/index.html` with your Render URL.

---

## 👤 Team
- Your Name · your.email@oregonstate.edu

---

## 📄 License
MIT