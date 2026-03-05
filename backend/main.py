"""
CampusLens AI — Backend API  (Day 2 Upgrade)
============================================
FastAPI + Claude API + pdfplumber
New in Day 2:
  - Engineered prompts with difficulty rubric & flag guides
  - Multi-strategy PDF extraction with fallback chain
  - JSON repair loop (up to 2 retries on malformed output)
  - Sparse-syllabus detection → lighter prompt
  - /analyze now returns extraction metadata
  - /compare now returns head-to-head breakdown
  - /batch endpoint: analyze up to 5 syllabi at once
  - /ping health check with model info
"""

import asyncio
import json
import time
from typing import Optional
import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pdf_extractor import ExtractionResult, extract_pdf_text, get_extraction_error_message
from prompts import (
    SYSTEM_PROMPT,
    build_compare_prompt,
    build_main_prompt,
    build_repair_prompt,
    build_sparse_prompt,
    extract_json_from_text,
    validate_and_fix,
)

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="CampusLens AI",
    version="2.0.0",
    description="AI-powered syllabus analyzer for OSU students",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai.OpenAI()
MODEL = "gpt-4o-mini"
MAX_RETRIES = 2  # JSON repair attempts

# ─────────────────────────────────────────────────────────────
#  CORE AI CALLER  (with repair loop)
# ─────────────────────────────────────────────────────────────

def call_openai(user_prompt: str, max_tokens: int = 2500) -> str:
    """Call OpenAI and return raw text response."""
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
    )
    return completion.choices[0].message.content


def call_openai_with_json_repair(
    user_prompt: str,
    max_tokens: int = 2500,
) -> dict:
    """
    Call OpenAI and robustly parse JSON.
    If parsing fails, ask OpenAI to repair its own output (up to MAX_RETRIES).
    """
    raw_response = call_openai(user_prompt, max_tokens)

    # Attempt 1: direct extraction
    result = extract_json_from_text(raw_response)
    if result is not None:
        return result

    # Retry loop: ask OpenAI to fix its own JSON
    last_raw = raw_response
    for attempt in range(MAX_RETRIES):
        repair_prompt = build_repair_prompt(last_raw, "JSON parsing failed")
        last_raw = call_openai(repair_prompt, max_tokens=1500)
        result = extract_json_from_text(last_raw)
        if result is not None:
            result["_repaired"] = True
            return result

    raise ValueError(
        f"OpenAI returned invalid JSON after {MAX_RETRIES} repair attempts. "
        f"Raw response preview: {raw_response[:300]}"
    )


# ─────────────────────────────────────────────────────────────
#  SHARED ANALYSIS LOGIC
# ─────────────────────────────────────────────────────────────

async def analyze_file(upload: UploadFile) -> dict:
    """Full pipeline: validate → extract → prompt → parse → validate."""
    t_start = time.time()

    # File type check
    if not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await upload.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    # ── PDF EXTRACTION ──
    extraction: ExtractionResult = extract_pdf_text(file_bytes)

    if not extraction.is_usable and extraction.char_count < 50:
        raise HTTPException(
            status_code=422,
            detail=get_extraction_error_message(extraction),
        )

    # ── CHOOSE PROMPT STRATEGY ──
    is_sparse = extraction.char_count < 500 or extraction.quality == "poor"
    if is_sparse:
        prompt = build_sparse_prompt(extraction.text)
    else:
        prompt = build_main_prompt(extraction.text)

    # ── CALL OPENAI ──
    try:
        raw_result = call_openai_with_json_repair(prompt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except openai.APIError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")

    # ── VALIDATE & FIX ──
    result = validate_and_fix(raw_result)

    # ── ATTACH METADATA ──
    result["_meta"] = {
        "filename": upload.filename,
        "file_size_kb": round(len(file_bytes) / 1024, 1),
        "page_count": extraction.page_count,
        "char_count": extraction.char_count,
        "extraction_method": extraction.method,
        "extraction_quality": extraction.quality,
        "prompt_strategy": "sparse" if is_sparse else "full",
        "analysis_time_seconds": round(time.time() - t_start, 2),
        "warnings": extraction.warnings,
    }

    return result


# ─────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "CampusLens AI",
        "version": "2.0.0",
        "endpoints": ["/analyze", "/compare", "/batch", "/health", "/docs"],
    }


@app.post("/analyze")
async def analyze_syllabus(file: UploadFile = File(...)):
    """
    Analyze a single syllabus PDF.
    Returns full structured analysis with metadata.
    """
    result = await analyze_file(file)
    return JSONResponse(content=result)


@app.post("/compare")
async def compare_syllabi(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    Compare two syllabi side-by-side.
    Returns individual analyses + head-to-head breakdown.
    """
    # Analyze both in parallel
    analysis_a, analysis_b = await asyncio.gather(
        analyze_file(file1),
        analyze_file(file2),
    )

    # Generate comparison
    try:
        compare_raw = call_openai_with_json_repair(
            build_compare_prompt(analysis_a, analysis_b),
            max_tokens=1200,
        )
    except (ValueError, openai.APIError) as e:
        compare_raw = {
            "recommended": "A",
            "recommendation_strength": "toss-up",
            "recommendation_reason": "Could not generate comparison analysis.",
            "error": str(e),
        }

    return JSONResponse(
        content={
            "course_a": analysis_a,
            "course_b": analysis_b,
            "comparison": compare_raw,
        }
    )


@app.post("/batch")
async def batch_analyze(files: list[UploadFile] = File(...)):
    """
    Analyze up to 5 syllabi at once.
    Returns array of analyses sorted by difficulty (easiest first).
    """
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Max 5 files per batch request.")
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Send at least 2 files for batch analysis.")

    results = await asyncio.gather(
        *[analyze_file(f) for f in files],
        return_exceptions=True,
    )

    analyses = []
    errors = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            errors.append({"file": files[i].filename, "error": str(r)})
        else:
            analyses.append(r)

    # Sort by difficulty score
    analyses.sort(key=lambda x: x.get("difficulty_score", 5))

    return JSONResponse(
        content={
            "count": len(analyses),
            "analyses": analyses,
            "errors": errors,
            "easiest": analyses[0].get("course_name") if analyses else None,
            "hardest": analyses[-1].get("course_name") if analyses else None,
        }
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "model": MODEL,
        "features": ["analyze", "compare", "batch", "json_repair", "sparse_fallback"],
    }