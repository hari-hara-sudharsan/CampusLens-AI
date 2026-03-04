"""
CampusLens AI — Prompt Engineering Module (Day 2)
==================================================
All prompt construction, JSON schema validation,
fallback chains, and response repair logic live here.
"""

import json
import re
from typing import Optional

# ─────────────────────────────────────────────────────────────
#  SCORING RUBRIC  (injected into system prompt)
#  Calibrated against 5 OSU syllabus types:
#  CS, Math, Writing, Science Lab, Group-Project courses
# ─────────────────────────────────────────────────────────────

DIFFICULTY_RUBRIC = """
DIFFICULTY SCORING RUBRIC (1–10) — use ALL criteria together:

Score 1–2  (Easy):
  - No exams OR only one low-stakes quiz
  - Attendance/participation is the main grade
  - <4 hrs/week total commitment
  - Flexible late policy

Score 3–4  (Moderate-Easy):
  - Weekly assignments but straightforward
  - 1 midterm + 1 final, standard format
  - 4–7 hrs/week
  - Some flexibility on deadlines

Score 5–6  (Moderate):
  - Regular problem sets or lab reports
  - Multiple exams, cumulative final possible
  - 7–10 hrs/week
  - Strict late policy or limited drops

Score 7–8  (Hard):
  - Heavy project load OR proof-based work OR lab-intensive
  - 3+ assessments counting >20% each
  - 10–15 hrs/week
  - Minimal or zero late tolerance
  - Group work with peer evaluation

Score 9–10 (Very Hard):
  - Graduate-style expectations in undergrad course
  - Research paper, thesis-level project, OR 4+ major exams
  - 15+ hrs/week
  - No drops, strict attendance, participation grade
  - Multiple compounding deadlines per week
"""

RED_FLAG_GUIDE = """
RED FLAG DETECTION — flag ONLY real issues found in the text:

HIGH severity:
  - "No late work accepted" or "zero credit after deadline"
  - Attendance counted in grade >10%
  - Ambiguous grading criteria ("at instructor's discretion")
  - Curve at instructor discretion with no formula
  - >40% of grade from a single deliverable

MEDIUM severity:
  - Group project with peer evaluation affecting individual grade
  - Multiple exams in same week based on schedule
  - Required expensive materials not mentioned until syllabus
  - Office hours <2 hrs/week for a hard course
  - Vague project requirements ("TBD")

LOW severity:
  - Late policy with <24hr grace period
  - No explicit study guide or exam format described
  - Participation grade without clear rubric
"""

GREEN_FLAG_GUIDE = """
GREEN FLAG DETECTION — note genuine positives:
  - Explicit rubrics provided for all assignments
  - Drop lowest grade policy
  - Multiple office hours slots or async support
  - Clear learning objectives per week
  - Practice exams or review sessions mentioned
  - Reasonable late policy (24–72hr window)
  - Collaborative learning explicitly encouraged
"""

# ─────────────────────────────────────────────────────────────
#  JSON SCHEMA  (strict — used for validation + prompt)
# ─────────────────────────────────────────────────────────────

RESPONSE_SCHEMA = {
    "course_name": "string — full course name",
    "course_code": "string like 'CS 361' or null",
    "instructor": "string or null",
    "credits": "integer or null",
    "term": "string like 'Winter 2026' or null",
    "difficulty_score": "integer 1-10",
    "difficulty_label": "one of: Easy | Moderate | Hard | Very Hard",
    "confidence": "one of: high | medium | low — how much useful text was in the syllabus",
    "weekly_hours_min": "integer — realistic minimum total hours per week",
    "weekly_hours_max": "integer — realistic maximum total hours per week",
    "workload_breakdown": {
        "lectures": "e.g. '3 hrs/week' or null",
        "assignments": "e.g. '2-4 hrs/week' or null",
        "projects": "e.g. '1 major project' or null",
        "exams": "e.g. '2 midterms + final' or null",
        "lab": "e.g. '2 hrs/week' or null — omit key if no lab"
    },
    "grade_breakdown": [
        {"component": "string", "weight": "integer 0-100"}
    ],
    "key_topics": ["list of 4-7 specific topics covered"],
    "skills_you_will_learn": ["list of 3-5 transferable skills"],
    "prerequisites_implied": ["list of implied knowledge — empty array if none"],
    "red_flags": [
        {"flag": "specific issue found in syllabus text", "severity": "high|medium|low"}
    ],
    "green_flags": ["list of positives — empty array if none"],
    "exam_schedule": [
        {"exam": "string", "week": "string or null", "weight": "integer or null"}
    ],
    "study_strategies": ["3-5 specific strategies for THIS course"],
    "survival_tips": ["2-3 blunt, honest tips"],
    "recommended_for": "1 sentence — student profile that would thrive",
    "not_recommended_for": "1 sentence — student profile that would struggle",
    "overall_summary": "2-3 honest sentences about this course",
    "stress_index": "integer 1-10 — emotional/stress load (distinct from difficulty)",
    "career_relevance": ["2-3 job titles or fields where this course is directly useful"]
}

# ─────────────────────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are CampusLens AI, an expert academic advisor with 15 years of experience 
helping college students at Oregon State University evaluate courses before enrollment.

Your job is to analyze syllabus text and produce a STRUCTURED JSON analysis that is:
- HONEST: Don't sugarcoat heavy workloads. Students depend on accurate info.
- SPECIFIC: Reference actual content from the syllabus, not generic advice.
- CALIBRATED: Use the difficulty rubric consistently across all courses.

{DIFFICULTY_RUBRIC}

{RED_FLAG_GUIDE}

{GREEN_FLAG_GUIDE}

STRICT OUTPUT RULES:
1. Return ONLY valid JSON — no markdown, no explanation, no preamble.
2. Never invent information not present in the syllabus.
3. If a field cannot be determined, use null for strings/numbers or [] for arrays.
4. grade_breakdown weights MUST sum to 100 (or close). If they don't add up in the syllabus, estimate proportionally.
5. weekly_hours should include lecture time + out-of-class work realistically.
6. stress_index is about EMOTIONAL load (ambiguity, group work, harsh policies) — separate from raw difficulty.
"""

# ─────────────────────────────────────────────────────────────
#  PROMPT BUILDER  (main + fallback variants)
# ─────────────────────────────────────────────────────────────

def build_main_prompt(syllabus_text: str) -> str:
    """Full-detail prompt for complete syllabi (>500 chars)."""
    schema_str = json.dumps(RESPONSE_SCHEMA, indent=2)
    # Use first 10,000 chars — covers most syllabi fully
    truncated = syllabus_text[:10000]
    truncation_note = ""
    if len(syllabus_text) > 10000:
        truncation_note = f"\n[Note: syllabus truncated at 10,000 chars. Full length: {len(syllabus_text)} chars]"

    return f"""Analyze this university course syllabus and return a JSON object matching the schema below EXACTLY.

SYLLABUS TEXT:
\"\"\"
{truncated}{truncation_note}
\"\"\"

REQUIRED JSON SCHEMA (follow field names and types exactly):
{schema_str}

Remember: Return ONLY the JSON object. No markdown. No explanation."""


def build_sparse_prompt(syllabus_text: str) -> str:
    """Reduced prompt for sparse/short syllabi (<500 chars of real content)."""
    return f"""This appears to be a minimal or incomplete course syllabus. 
Extract what you can and make reasonable estimates for missing fields based on context clues.
Mark confidence as "low" for this analysis.

SYLLABUS TEXT:
\"\"\"
{syllabus_text[:4000]}
\"\"\"

Return ONLY a JSON object with these fields (null if truly unknown):
{{
  "course_name": null,
  "course_code": null,
  "instructor": null,
  "credits": null,
  "term": null,
  "difficulty_score": 5,
  "difficulty_label": "Moderate",
  "confidence": "low",
  "weekly_hours_min": 5,
  "weekly_hours_max": 10,
  "workload_breakdown": {{}},
  "grade_breakdown": [],
  "key_topics": [],
  "skills_you_will_learn": [],
  "prerequisites_implied": [],
  "red_flags": [],
  "green_flags": [],
  "exam_schedule": [],
  "study_strategies": [],
  "survival_tips": [],
  "recommended_for": "Students interested in the subject matter",
  "not_recommended_for": "Students needing detailed structure upfront",
  "overall_summary": "Limited syllabus information available. Analysis is based on partial data.",
  "stress_index": 5,
  "career_relevance": []
}}"""


def build_repair_prompt(bad_json: str, error_msg: str) -> str:
    """Ask Claude to fix its own malformed JSON."""
    return f"""The following JSON is malformed. Fix it and return ONLY valid JSON.

ERROR: {error_msg}

BROKEN JSON:
\"\"\"
{bad_json[:3000]}
\"\"\"

Rules:
- Return ONLY valid JSON
- Keep all original field names and values
- Fix syntax errors only (missing quotes, trailing commas, etc.)
- Do not add or remove fields"""


def build_compare_prompt(analysis_a: dict, analysis_b: dict) -> str:
    """Side-by-side comparison prompt."""
    return f"""You are comparing two university courses for a student deciding which to take.
Be direct and opinionated — students need a clear recommendation.

COURSE A: {json.dumps(analysis_a, indent=2)[:3500]}

COURSE B: {json.dumps(analysis_b, indent=2)[:3500]}

Return ONLY this JSON:
{{
  "recommended": "A or B",
  "recommendation_strength": "strong|slight|toss-up",
  "recommendation_reason": "2 specific sentences explaining the choice",
  "easier_course": "A or B",
  "more_career_valuable": "A or B",
  "head_to_head": [
    {{"category": "Workload", "winner": "A or B or Tie", "detail": "brief explanation"}},
    {{"category": "Grading Fairness", "winner": "A or B or Tie", "detail": "brief explanation"}},
    {{"category": "Skill Building", "winner": "A or B or Tie", "detail": "brief explanation"}},
    {{"category": "Exam Stress", "winner": "A or B or Tie", "detail": "brief explanation"}},
    {{"category": "Overall Value", "winner": "A or B or Tie", "detail": "brief explanation"}}
  ],
  "take_both_if": "one sentence — when it makes sense to take both",
  "avoid_both_if": "one sentence — when neither is right"
}}"""


# ─────────────────────────────────────────────────────────────
#  JSON VALIDATOR  (post-parse fixes)
# ─────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    "course_name", "difficulty_score", "difficulty_label", "confidence",
    "weekly_hours_min", "weekly_hours_max", "workload_breakdown",
    "grade_breakdown", "key_topics", "skills_you_will_learn",
    "prerequisites_implied", "red_flags", "green_flags", "exam_schedule",
    "study_strategies", "survival_tips", "recommended_for",
    "not_recommended_for", "overall_summary", "stress_index", "career_relevance"
]

ARRAY_FIELDS = [
    "key_topics", "skills_you_will_learn", "prerequisites_implied",
    "red_flags", "green_flags", "exam_schedule", "study_strategies",
    "survival_tips", "career_relevance", "grade_breakdown"
]

DEFAULTS = {
    "course_name": "Unknown Course",
    "course_code": None,
    "instructor": None,
    "credits": None,
    "term": None,
    "difficulty_score": 5,
    "difficulty_label": "Moderate",
    "confidence": "low",
    "weekly_hours_min": 5,
    "weekly_hours_max": 10,
    "workload_breakdown": {},
    "grade_breakdown": [],
    "key_topics": [],
    "skills_you_will_learn": [],
    "prerequisites_implied": [],
    "red_flags": [],
    "green_flags": [],
    "exam_schedule": [],
    "study_strategies": [],
    "survival_tips": [],
    "recommended_for": "Students interested in the subject",
    "not_recommended_for": "Students without relevant background",
    "overall_summary": "Analysis completed with limited syllabus data.",
    "stress_index": 5,
    "career_relevance": []
}


def validate_and_fix(data: dict) -> dict:
    """
    Post-parse validation and auto-repair:
    1. Fill missing required fields with defaults
    2. Coerce types (string digits → int, etc.)
    3. Clamp score fields to valid ranges
    4. Fix grade_breakdown weights to sum ~100
    5. Normalize difficulty_label to valid values
    """
    # Fill missing fields
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            if field in DEFAULTS:
                data[field] = DEFAULTS[field]

    # Ensure array fields are actually arrays
    for field in ARRAY_FIELDS:
        if not isinstance(data.get(field), list):
            data[field] = []

    # Coerce numeric fields
    for field in ["difficulty_score", "stress_index"]:
        try:
            data[field] = max(1, min(10, int(data[field])))
        except (TypeError, ValueError):
            data[field] = 5

    for field in ["weekly_hours_min", "weekly_hours_max"]:
        try:
            data[field] = max(1, int(data[field]))
        except (TypeError, ValueError):
            data[field] = 5 if "min" in field else 10

    if data["weekly_hours_min"] > data["weekly_hours_max"]:
        data["weekly_hours_min"], data["weekly_hours_max"] = \
            data["weekly_hours_max"], data["weekly_hours_min"]

    # Normalize difficulty label
    valid_labels = {"Easy", "Moderate", "Hard", "Very Hard"}
    if data.get("difficulty_label") not in valid_labels:
        score = data["difficulty_score"]
        if score <= 3:   data["difficulty_label"] = "Easy"
        elif score <= 5: data["difficulty_label"] = "Moderate"
        elif score <= 7: data["difficulty_label"] = "Hard"
        else:            data["difficulty_label"] = "Very Hard"

    # Normalize confidence
    if data.get("confidence") not in {"high", "medium", "low"}:
        data["confidence"] = "medium"

    # Fix grade_breakdown: ensure weights sum to ~100
    gb = data.get("grade_breakdown", [])
    if gb:
        total = sum(item.get("weight", 0) for item in gb if isinstance(item, dict))
        if total > 0 and abs(total - 100) > 5:
            scale = 100.0 / total
            for item in gb:
                if isinstance(item, dict) and "weight" in item:
                    item["weight"] = round(item["weight"] * scale)

    # Ensure red_flags have correct shape
    cleaned_flags = []
    for flag in data.get("red_flags", []):
        if isinstance(flag, str):
            cleaned_flags.append({"flag": flag, "severity": "medium"})
        elif isinstance(flag, dict) and "flag" in flag:
            if flag.get("severity") not in {"high", "medium", "low"}:
                flag["severity"] = "medium"
            cleaned_flags.append(flag)
    data["red_flags"] = cleaned_flags

    return data


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Multi-strategy JSON extraction:
    1. Direct parse
    2. Strip markdown fences
    3. Find first { ... } block
    4. Regex-based brace matching
    """
    # Strategy 1: direct
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: find first complete JSON object
    start = text.find("{")
    if start != -1:
        # Find matching closing brace
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":   depth += 1
            elif ch == "}": depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    break

    # Strategy 4: remove trailing commas (common Claude mistake)
    no_trailing = re.sub(r",\s*([}\]])", r"\1", cleaned)
    try:
        return json.loads(no_trailing)
    except json.JSONDecodeError:
        pass

    return None