# 🎓 CampusLens AI — Day 2
> Prompt Engineering, Testing & Fallback Handling

---

## 🆕 What's New in Day 2

### Prompt Engine (`backend/prompts.py`)
- **Calibrated difficulty rubric** — scoring guide from 1–10 with OSU-specific examples
- **Red flag detection guide** — high/medium/low severity criteria built into system prompt
- **Green flag guide** — consistent positive detection logic
- **Strict JSON schema** — 20+ fields defined with types, nullability, and constraints
- **Sparse syllabus detection** → lighter prompt for minimal syllabi
- **JSON repair loop** — if Claude returns malformed JSON, asks Claude to fix it (up to 2 retries)
- **Multi-strategy JSON extraction** — 4 fallback parsing strategies before giving up
- **Post-parse validator** — auto-fixes missing fields, clamps scores, repairs grade weights

### New Fields Added
| Field | Description |
|---|---|
| `confidence` | high/medium/low — how complete was the syllabus text |
| `stress_index` | 1-10 emotional/stress load (separate from difficulty) |
| `career_relevance` | job titles/fields where this course is useful |
| `prerequisites_implied` | knowledge assumed by the course |
| `exam_schedule` | individual exams with week and weight |
| `_meta` | extraction method, quality, timing, warnings |

### PDF Extractor (`backend/pdf_extractor.py`)
- **Table extraction** — converts grade tables to readable text for Claude
- **Text quality scoring** — assesses char density and keyword hits
- **Multi-strategy fallback chain** — pdfplumber+tables → pdfplumber standard → graceful error
- **Text cleaning** — fixes hyphenation, normalizes unicode, removes page numbers
- **Extraction metadata** returned with every analysis

### Test Suite (`tests/`)
- **5 realistic OSU mock syllabi** covering CS, Math, Writing, Orgo, Econ
- **2 edge cases** — sparse (3-line syllabus) and scanned gibberish
- **10 validation checks** per syllabus — fields, types, calibration, sums
- **Expected score ranges** per course for calibration testing
- **Colorized output** with pass/fail per check

### Backend (`backend/main.py`)
- `POST /analyze` — now returns `_meta` extraction info and all new fields
- `POST /compare` — now runs both analyses in parallel, richer comparison
- `POST /batch` — NEW: analyze up to 5 syllabi at once, sorted by difficulty
- JSON repair built into every Claude call

### Frontend (`frontend/index.html`)
- **Compare Mode tab** — drop two PDFs, get head-to-head breakdown
- **Dual rings** — Difficulty + Stress Index displayed together
- **Confidence badge** — shows analysis reliability
- **Exam schedule section** — dedicated timeline view
- **Extraction warnings** — shown if PDF quality was low
- **Meta strip** — shows extraction method, page count, timing
- **Career Relevance** and **Prerequisites** sections
- All new `_meta` fields displayed for transparency

---

## 🚀 Setup (Same as Day 1)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

Then open `frontend/index.html` in your browser.

---

## 🧪 Running the Prompt Tests

```bash
cd tests

# Run all 7 syllabus tests
python test_prompts.py

# Test only one syllabus
python test_prompts.py --name cs361

# Print full JSON output for a test
python test_prompts.py --name orgo --show

# All available test names:
#   cs361_software_engineering
#   math341_linear_algebra
#   wr327_technical_writing
#   ch331_organic_chemistry
#   econ201_microeconomics
#   sparse_minimal
#   scanned_gibberish
```

### Expected Test Output
```
============================================================
CampusLens AI — Prompt Test Suite
============================================================
Model: claude-opus-4-5
Syllabi: 7

────────────────────────────────────────────────────────────
Testing: ch331_organic_chemistry
  Text length: 3241 chars
  → Prompt strategy: full
  → Raw response length: 2180 chars
  ✓ All 21 required fields present
  ✓ difficulty_score = 9 (valid 1-10)
  ✓ Score 9 within expected range 8-10
  ✓ Weekly hours: 15-20 hrs (logical)
  ✓ Grade weights sum to 100% (~100)
  ...

  Score: 10/10 (100%)
```

---

## 📁 Day 2 File Structure

```
campuslens/
├── backend/
│   ├── main.py              ← Updated: parallel compare, batch, JSON repair
│   ├── prompts.py           ← NEW: all prompt logic, schema, validators
│   ├── pdf_extractor.py     ← NEW: multi-strategy extraction + fallback
│   └── requirements.txt
├── frontend/
│   └── index.html           ← Updated: Compare tab, stress ring, meta strip
├── tests/
│   ├── mock_syllabi.py      ← NEW: 7 realistic test syllabi
│   └── test_prompts.py      ← NEW: automated test runner
└── README_DAY2.md
```

---

## 🔧 API Changes

### `/analyze` — new response fields
```json
{
  "confidence": "high",
  "stress_index": 9,
  "career_relevance": ["Pre-med", "Biochemistry", "Pharmacy"],
  "prerequisites_implied": ["CH 232", "General Chemistry"],
  "exam_schedule": [
    {"exam": "Exam 1", "week": "Week 3", "weight": 15},
    {"exam": "Final", "week": "Finals", "weight": 25}
  ],
  "_meta": {
    "filename": "ch331_syllabus.pdf",
    "page_count": 4,
    "char_count": 3241,
    "extraction_method": "pdfplumber+tables",
    "extraction_quality": "good",
    "prompt_strategy": "full",
    "analysis_time_seconds": 4.2,
    "warnings": []
  }
}
```

### `/batch` — NEW endpoint
```bash
curl -X POST http://localhost:8000/batch \
  -F "files=@cs361.pdf" \
  -F "files=@math341.pdf" \
  -F "files=@wr327.pdf"
```
Returns analyses sorted easiest → hardest with `easiest` and `hardest` course names.

---

## 🏆 (Resume Talking Points)

> "I engineered a multi-layer prompt system with a calibrated difficulty rubric, 
> automated JSON repair loop, and 4-strategy PDF fallback chain — then validated 
> it against 7 test cases covering every course type at OSU."

- **Prompt engineering**: rubric-driven, schema-enforced, multi-turn repair
- **Robustness**: handles scanned PDFs, sparse syllabi, malformed JSON gracefully  
- **Testing mindset**: 70+ automated checks across 7 realistic test cases
- **Full-stack thinking**: extraction → prompt → parse → validate → display