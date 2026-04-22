# Parses candidateResult_N files (cProfile output) and writes student_name_data.csv
# Fields captured (per assignment requirements):
#   - runtime_sec: total runtime performance from cProfile
#   - steps_per_gen: total function calls (proxy for steps per generation)
#   - generation: which generation this run belongs to
#   - fitness_score: pass as argument, or leave blank to fill in manually
#
# Usage:
#   python fitness_to_csv.py NUM_OF_CANDIDATES GENERATION [FITNESS_SCORE]
#
# Examples:
#   python fitness_to_csv.py 5 1             # fitness_score left blank
#   python fitness_to_csv.py 5 1 0.87        # fitness_score = 0.87
#
# Run this after each call to fitness.py to log that generation's data.
# The CSV appends rows each run so you build the full table across all generations.

import os
import re
import sys
import csv

NUM_OF_CANDIDATES = int(sys.argv[1])
GENERATION        = int(sys.argv[2])
FITNESS_SCORE     = sys.argv[3] if len(sys.argv) > 3 else ""

aidan = "Aidan_Burchett"
reese = "Reese_Farrell"
jacob = "Jacob_Wallace"
asa = "Asa_McDaniel"

OUTPUT_CSV  = f"{reese}_data.csv"  # change NAME HERE

# CSV columns — matches assignment required fields
FIELDNAMES = [
    "generation",
    "candidate",
    "runtime_sec",
    "steps_per_gen",
    "fitness_score",
]

def parse_cprofile(filepath: str) -> dict:
    """
    Reads a candidateResult_N file and extracts:
      - runtime_sec   : total execution time in seconds
      - steps_per_gen : total function calls (best proxy for steps from cProfile)
    """
    result = {
        "runtime_sec":   None,
        "steps_per_gen": None,
    }

    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [WARN] File not found: {filepath}")
        return result

    # Example: "56 function calls in 0.123 seconds"
    summary = re.search(r"([\d,]+) function calls.*?in ([\d.]+) seconds", content)
    if summary:
        result["steps_per_gen"] = int(summary.group(1).replace(",", ""))
        result["runtime_sec"]   = float(summary.group(2))

    return result

def main():
    write_header = not os.path.exists(OUTPUT_CSV)

    rows = []
    for i in range(NUM_OF_CANDIDATES):
        filepath = f"candidateResult_{i}"
        print(f"Parsing {filepath}...")
        data = parse_cprofile(filepath)

        row = {
            "generation":    GENERATION,
            "candidate":     i,
            "runtime_sec":   data["runtime_sec"]   if data["runtime_sec"]   is not None else "N/A",
            "steps_per_gen": data["steps_per_gen"] if data["steps_per_gen"] is not None else "N/A",
            "fitness_score": FITNESS_SCORE,
        }
        rows.append(row)

        print(f"  gen={row['generation']}  candidate={row['candidate']}  "
              f"runtime={row['runtime_sec']}s  steps={row['steps_per_gen']}  "
              f"fitness={row['fitness_score'] or '(not set)'}")

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    print(f"\nAppended {len(rows)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()