"""
AgriTwin AI — Dataset Quality & Validation Engine (Phase 7).
Enforces quality gates before data enters training:
  1. Range Checks: Temperature (-10°C to 60°C), Rainfall (>=0), NDVI (-1.0 to 1.0).
  2. Structure Checks: Required keys ('instruction', 'input', 'output').
  3. Hallucination Guard: Verifies output numbers match input facts.
"""

import json
import re
from pathlib import Path

def validate_row(row: dict, idx: int) -> list[str]:
    issues = []
    
    # Key structural checks
    for key in ["instruction", "input", "output"]:
        if key not in row or not isinstance(row[key], str) or not row[key].strip():
            issues.append(f"Row {idx}: Missing or empty key '{key}'")

    input_text = row.get("input", "")
    output_text = row.get("output", "")

    # Temperature check
    temp_match = re.search(r"Current Temperature:\s*([-\d.]+)", input_text)
    if temp_match:
        temp = float(temp_match.group(1))
        if temp < -10.0 or temp > 60.0:
            issues.append(f"Row {idx}: Impossible temperature value {temp}°C")

    # Rainfall check
    rain_match = re.search(r"7-Day Rainfall:\s*([-\d.]+)", input_text)
    if rain_match:
        rain = float(rain_match.group(1))
        if rain < 0.0:
            issues.append(f"Row {idx}: Negative rainfall value {rain} mm")

    # NDVI check
    ndvi_match = re.search(r"MODIS Satellite NDVI:\s*([-\d.]+)", input_text)
    if ndvi_match:
        ndvi = float(ndvi_match.group(1))
        if ndvi < -1.0 or ndvi > 1.0:
            issues.append(f"Row {idx}: Invalid NDVI value {ndvi}")

    # Check for hallucinated numbers in output
    # Extracts numbers from output and verifies if they exist in input text
    out_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", output_text))
    in_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", input_text))
    
    for num in out_numbers:
        # Ignore common non-input numbers like percentages or status indicators (0, 100, 48)
        if num in ["0", "100", "48", "2026", "24"]:
            continue
        if num not in in_numbers:
            issues.append(f"Row {idx}: Potential hallucinated number '{num}' in output not present in input facts")

    return issues

def validate_jsonl_file(path: Path) -> tuple[int, int]:
    if not path.exists():
        print(f"Error: File {path} does not exist.")
        return 0, 1

    total_rows = 0
    total_issues = 0

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            total_rows += 1
            try:
                row = json.loads(line)
                issues = validate_row(row, idx)
                if issues:
                    total_issues += len(issues)
                    for issue in issues[:3]: # print top 3 issues
                        print(f"  [X] {issue}")
            except Exception as e:
                total_issues += 1
                print(f"  [X] Row {idx}: Invalid JSON line - {e}")

    return total_rows, total_issues

def main():
    print("=== AgriTwin AI · Dataset Quality & Hallucination Guard Validation ===")
    ai_dir = Path(__file__).resolve().parent.parent
    training_dir = ai_dir / "training"

    files = ["train.jsonl", "validation.jsonl", "test.jsonl"]
    overall_issues = 0

    for fname in files:
        fpath = training_dir / fname
        print(f"\nValidating {fname}...")
        rows, issues = validate_jsonl_file(fpath)
        print(f"Result for {fname}: {rows} rows scanned, {issues} quality issues found.")
        overall_issues += issues

    if overall_issues == 0:
        print("\n[SUCCESS] ALL DATASETS PASSED QUALITY & HALLUCINATION VALIDATION PERFECTLY!")
    else:
        print(f"\n[WARNING] Validation completed with {overall_issues} total issues.")

if __name__ == "__main__":
    main()
