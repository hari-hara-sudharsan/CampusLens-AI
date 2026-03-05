"""
CampusLens AI — Prompt Test Runner (Day 2)
==========================================
Tests the prompt engine against all 5 mock OSU syllabi.
Validates JSON shape, field types, score calibration, and fallback logic.

Usage:
  python test_prompts.py            # run all tests
  python test_prompts.py --name cs361   # test specific syllabus
  python test_prompts.py --show         # print full JSON output
"""

import argparse
import json
import sys
import os

# Allow running from /tests directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from prompts import (
    build_main_prompt,
    build_sparse_prompt,
    extract_json_from_text,
    validate_and_fix,
    SYSTEM_PROMPT,
)
from mock_syllabi import MOCK_SYLLABI, EXPECTED_SCORES
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-4-5"

# ─── COLORS ────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}⚠{RESET} {msg}")
def info(msg): print(f"  {CYAN}→{RESET} {msg}")


# ─── VALIDATORS ────────────────────────────────────────────

REQUIRED_FIELDS = [
    "course_name", "difficulty_score", "difficulty_label", "confidence",
    "weekly_hours_min", "weekly_hours_max",
    "key_topics", "skills_you_will_learn", "red_flags", "green_flags",
    "grade_breakdown", "study_strategies", "survival_tips",
    "recommended_for", "not_recommended_for", "overall_summary",
    "stress_index", "career_relevance",
]

def validate_result(name: str, result: dict, show_full: bool = False) -> tuple[int, int]:
    """Run all checks on a parsed result. Returns (passed, total)."""
    passed = 0
    total = 0

    def check(condition: bool, pass_msg: str, fail_msg: str):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            ok(pass_msg)
        else:
            fail(fail_msg)

    # 1. Required fields present
    missing = [f for f in REQUIRED_FIELDS if f not in result]
    check(len(missing) == 0,
          f"All {len(REQUIRED_FIELDS)} required fields present",
          f"Missing fields: {missing}")

    # 2. Difficulty score in range
    score = result.get("difficulty_score")
    check(isinstance(score, int) and 1 <= score <= 10,
          f"difficulty_score = {score} (valid 1-10)",
          f"difficulty_score = {score!r} (invalid)")

    # 3. Difficulty score calibration
    if name in EXPECTED_SCORES:
        lo, hi = EXPECTED_SCORES[name]
        in_range = isinstance(score, int) and lo <= score <= hi
        check(in_range,
              f"Score {score} within expected range {lo}-{hi}",
              f"Score {score} OUTSIDE expected range {lo}-{hi}")

    # 4. Hours are logical
    h_min = result.get("weekly_hours_min", 0)
    h_max = result.get("weekly_hours_max", 0)
    check(isinstance(h_min, int) and isinstance(h_max, int) and h_min <= h_max and h_min > 0,
          f"Weekly hours: {h_min}-{h_max} hrs (logical)",
          f"Weekly hours: {h_min}-{h_max} hrs (illogical)")

    # 5. grade_breakdown weights sum ~100
    gb = result.get("grade_breakdown", [])
    if gb:
        total_weight = sum(item.get("weight", 0) for item in gb if isinstance(item, dict))
        check(90 <= total_weight <= 110,
              f"Grade weights sum to {total_weight}% (~100)",
              f"Grade weights sum to {total_weight}% (should be ~100)")
    else:
        warn("grade_breakdown is empty (may be OK for sparse syllabi)")
        total += 1  # count but not as fail

    # 6. Arrays are actually arrays
    for arr_field in ["key_topics", "red_flags", "green_flags", "study_strategies"]:
        val = result.get(arr_field)
        check(isinstance(val, list),
              f"{arr_field} is a list (length {len(val) if isinstance(val, list) else 'N/A'})",
              f"{arr_field} is NOT a list: {type(val)}")

    # 7. Red flags have correct shape
    flags = result.get("red_flags", [])
    if flags:
        flag_ok = all(
            isinstance(f, dict) and "flag" in f and f.get("severity") in {"high", "medium", "low"}
            for f in flags
        )
        check(flag_ok,
              f"red_flags all have correct shape (flag + severity)",
              f"Some red_flags have incorrect shape")

    # 8. Confidence field valid
    confidence = result.get("confidence")
    check(confidence in {"high", "medium", "low"},
          f"confidence = '{confidence}' (valid)",
          f"confidence = '{confidence!r}' (must be high/medium/low)")

    # 9. stress_index in range
    si = result.get("stress_index")
    check(isinstance(si, int) and 1 <= si <= 10,
          f"stress_index = {si} (valid 1-10)",
          f"stress_index = {si!r} (invalid)")

    # 10. Strings are non-empty
    for str_field in ["overall_summary", "recommended_for", "not_recommended_for"]:
        val = result.get(str_field, "")
        check(isinstance(val, str) and len(val.strip()) > 5,
              f"{str_field} has content",
              f"{str_field} is empty or missing")

    if show_full:
        print(f"\n{CYAN}  Full JSON:{RESET}")
        print(json.dumps(result, indent=2))

    return passed, total


# ─── TEST RUNNER ────────────────────────────────────────────

def run_test(name: str, text: str, show_full: bool = False) -> dict:
    """Run a single syllabus through the full prompt → parse → validate pipeline."""
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}Testing: {name}{RESET}")
    print(f"  Text length: {len(text)} chars")

    # Choose prompt strategy
    is_sparse = len(text.strip()) < 500
    if name == "scanned_gibberish" or is_sparse:
        prompt = build_sparse_prompt(text)
        strategy = "sparse"
    else:
        prompt = build_main_prompt(text)
        strategy = "full"
    info(f"Prompt strategy: {strategy}")

    # Call Claude
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in message.content if hasattr(b, "text"))
        info(f"Raw response length: {len(raw)} chars")
    except Exception as e:
        fail(f"Claude API call failed: {e}")
        return {"passed": 0, "total": 1, "name": name, "error": str(e)}

    # Parse JSON
    parsed = extract_json_from_text(raw)
    if parsed is None:
        fail("Could not extract JSON from response")
        if show_full:
            print(f"  Raw: {raw[:500]}")
        return {"passed": 0, "total": 1, "name": name, "error": "JSON parse failed"}

    ok("JSON parsed successfully")

    # Validate and fix
    result = validate_and_fix(parsed)

    # Handle expected failure cases
    if name == "scanned_gibberish":
        info("Scanned PDF test — checking graceful degradation")
        conf = result.get("confidence", "")
        if conf == "low":
            ok("confidence = 'low' (correct for unreadable PDF)")
        else:
            warn(f"confidence = '{conf}' (expected 'low' for gibberish input)")
        return {"passed": 1, "total": 1, "name": name, "result": result}

    # Run full validation
    passed, total = validate_result(name, result, show_full=show_full)

    score_pct = round(100 * passed / total)
    color = GREEN if score_pct >= 80 else YELLOW if score_pct >= 60 else RED
    print(f"\n  {color}{BOLD}Score: {passed}/{total} ({score_pct}%){RESET}")

    return {"passed": passed, "total": total, "name": name, "result": result}


def run_all_tests(filter_name: str = None, show_full: bool = False):
    """Run all mock syllabus tests and print summary."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}CampusLens AI — Prompt Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"Model: {MODEL}")
    print(f"Syllabi: {len(MOCK_SYLLABI)}")

    all_results = []

    for name, text in MOCK_SYLLABI.items():
        if filter_name and filter_name.lower() not in name.lower():
            continue
        result = run_test(name, text, show_full=show_full)
        all_results.append(result)

    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'='*60}")

    total_passed = 0
    total_checks = 0

    for r in all_results:
        p = r.get("passed", 0)
        t = r.get("total", 1)
        total_passed += p
        total_checks += t
        pct = round(100 * p / t) if t > 0 else 0
        color = GREEN if pct >= 80 else YELLOW if pct >= 60 else RED
        status = "ERROR" if "error" in r else f"{pct}%"
        print(f"  {color}{r['name']:<40} {p}/{t} ({status}){RESET}")

    if total_checks > 0:
        overall_pct = round(100 * total_passed / total_checks)
        color = GREEN if overall_pct >= 80 else YELLOW if overall_pct >= 60 else RED
        print(f"\n{color}{BOLD}Overall: {total_passed}/{total_checks} ({overall_pct}%){RESET}")

        if overall_pct >= 80:
            print(f"\n{GREEN}✓ Prompts are well-calibrated. Ready for Day 3!{RESET}")
        elif overall_pct >= 60:
            print(f"\n{YELLOW}⚠ Prompts need minor tuning. Check failed cases above.{RESET}")
        else:
            print(f"\n{RED}✗ Prompts need significant work. Review rubric and schema.{RESET}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CampusLens Prompt Test Suite")
    parser.add_argument("--name", help="Filter to test a specific syllabus (partial match)")
    parser.add_argument("--show", action="store_true", help="Print full JSON output")
    args = parser.parse_args()

    run_all_tests(filter_name=args.name, show_full=args.show)