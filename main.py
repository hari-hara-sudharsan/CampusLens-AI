"""
CampusLens AI - Backend API
FastAPI + Claude API + pdfplumber
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pdfplumber
import anthropic
import json
import io
import re
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="CampusLens AI", version="1.0.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from PDF bytes using pdfplumber."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n".join(text_parts)


def build_analysis_prompt(syllabus_text: str) -> str:
    return f"""You are an expert academic advisor analyzing a university course syllabus.
Analyze the following syllabus text and return ONLY a valid JSON object (no markdown, no explanation).

Syllabus Text:
\"\"\"
{syllabus_text[:8000]}
\"\"\"

Return this exact JSON structure:
{{
  "course_name": "string",
  "course_code": "string or null",
  "instructor": "string or null",
  "credits": "number or null",
  "difficulty_score": <integer 1-10>,
  "difficulty_label": "Easy | Moderate | Hard | Very Hard",
  "weekly_hours_min": <integer>,
  "weekly_hours_max": <integer>,
  "workload_breakdown": {{
    "lectures": "e.g. 3 hrs/week",
    "assignments": "e.g. 2-4 hrs/week",
    "projects": "e.g. varies",
    "exams": "e.g. 3 midterms + final"
  }},
  "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "skills_you_will_learn": ["skill1", "skill2", "skill3"],
  "red_flags": [
    {{"flag": "short description", "severity": "low|medium|high"}}
  ],
  "green_flags": ["positive aspect 1", "positive aspect 2"],
  "grade_breakdown": [
    {{"component": "Homework", "weight": 30}},
    {{"component": "Midterm", "weight": 30}},
    {{"component": "Final", "weight": 40}}
  ],
  "study_strategies": ["strategy1", "strategy2", "strategy3"],
  "survival_tips": ["tip1", "tip2"],
  "recommended_for": "string - type of student who would thrive",
  "not_recommended_for": "string - who might struggle",
  "overall_summary": "2-3 sentence honest summary of this course"
}}"""


def parse_claude_response(content: list) -> dict:
    """Extract JSON from Claude's response content blocks."""
    full_text = ""
    for block in content:
        if hasattr(block, "text"):
            full_text += block.text

    # Strip markdown fences if any
    cleaned = re.sub(r"```json|```", "", full_text).strip()
    return json.loads(cleaned)


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "CampusLens AI is running 🎓"}


@app.post("/analyze")
async def analyze_syllabus(file: UploadFile = File(...)):
    """
    Main endpoint: upload a syllabus PDF → get AI analysis back.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    # Extract text
    try:
        syllabus_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {str(e)}")

    if len(syllabus_text.strip()) < 100:
        raise HTTPException(
            status_code=422,
            detail="PDF appears to be scanned/image-based or has very little text.",
        )

    # Call Claude API
    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": build_analysis_prompt(syllabus_text),
                }
            ],
        )
        result = parse_claude_response(message.content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {str(e)}")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")

    # Add metadata
    result["filename"] = file.filename
    result["char_count"] = len(syllabus_text)
    result["pages_estimated"] = max(1, len(syllabus_text) // 2000)

    return JSONResponse(content=result)


@app.post("/compare")
async def compare_syllabi(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    BONUS FEATURE: Compare two syllabi side by side.
    """
    results = []
    for f in [file1, file2]:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"{f.filename} must be a PDF.")
        file_bytes = await f.read()
        syllabus_text = extract_text_from_pdf(file_bytes)

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": build_analysis_prompt(syllabus_text)}],
        )
        result = parse_claude_response(message.content)
        result["filename"] = f.filename
        results.append(result)

    # Ask Claude for a comparison summary
    compare_prompt = f"""Compare these two course analyses and return ONLY JSON:
Course A: {json.dumps(results[0], indent=2)[:3000]}
Course B: {json.dumps(results[1], indent=2)[:3000]}

Return JSON:
{{
  "recommendation": "A or B",
  "reason": "2-sentence explanation",
  "easier_course": "A or B",
  "more_valuable_course": "A or B",
  "key_differences": ["diff1", "diff2", "diff3"]
}}"""

    comp_msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": compare_prompt}],
    )
    comparison = parse_claude_response(comp_msg.content)

    return JSONResponse(
        content={
            "course_a": results[0],
            "course_b": results[1],
            "comparison": comparison,
        }
    )


@app.get("/health")
def health():
    return {"status": "ok", "model": "claude-opus-4-5"}