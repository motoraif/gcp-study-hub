#!/usr/bin/env python3
"""Validate and tidy data/quiz-questions.json.

Usage:
    python3 scripts/add_questions.py          # validate the question bank
    python3 scripts/add_questions.py --sort    # validate, then sort by cert + id

Checks each question has the required fields, a valid answer index, a known
cert code, and a unique id. Run this before opening a PR that touches the
question bank.
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE, "data", "quiz-questions.json")

VALID_CERTS = {"CDL", "ACE", "ADP", "GWA", "PCA", "PCD", "PCDOE",
               "PCSE", "PCNE", "PCDE", "PDE", "PMLE"}
REQUIRED = {"id", "cert", "domain", "question", "options", "answer", "explanation"}


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])
    errors = []
    seen_ids = set()

    for i, q in enumerate(questions):
        where = f"question[{i}] (id={q.get('id', '?')})"
        missing = REQUIRED - set(q)
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
            continue
        if q["cert"] not in VALID_CERTS:
            errors.append(f"{where}: unknown cert '{q['cert']}' (valid: {sorted(VALID_CERTS)})")
        if q["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(q["id"])
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            errors.append(f"{where}: options must be a list of 2+ items")
        elif not isinstance(q["answer"], int) or not (0 <= q["answer"] < len(q["options"])):
            errors.append(f"{where}: answer index {q['answer']} out of range")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print(f"OK: {len(questions)} questions valid across "
          f"{len({q['cert'] for q in questions})} certifications.")

    if "--sort" in sys.argv:
        questions.sort(key=lambda q: (q["cert"], q["id"]))
        data["questions"] = questions
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("Sorted and rewrote the question bank.")


if __name__ == "__main__":
    main()
