"""Command-line interface: screen a folder of resumes against a job description."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .parser import parse_directory, parse_resume
from .screener import ResumeScreener

RECOMMENDATION_ICONS = {"strong_match": "++", "potential_match": "+ ", "weak_match": "- "}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="resume-screener",
        description="Screen resumes against a job description using an LLM.",
    )
    parser.add_argument("resumes", help="Path to a resume file or a directory of resumes")
    parser.add_argument("--jd", required=True, help="Path to the job description (.txt/.md)")
    parser.add_argument("--model", default="claude-sonnet-5-5", help="Anthropic model to use")
    parser.add_argument("--out", help="Optional output path (.json or .csv) for full results")
    parser.add_argument("--top", type=int, default=0, help="Only display the top N candidates")
    args = parser.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8")

    resume_path = Path(args.resumes)
    resumes = parse_directory(resume_path) if resume_path.is_dir() else [parse_resume(resume_path)]
    if not resumes:
        sys.exit("No supported resume files found (.pdf, .docx, .txt).")

    print(f"Screening {len(resumes)} resume(s)...\n")
    screener = ResumeScreener(model=args.model)
    results = screener.screen_batch(resumes, jd_text)

    shown = results[: args.top] if args.top else results
    for rank, r in enumerate(shown, start=1):
        icon = RECOMMENDATION_ICONS.get(r.recommendation, "? ")
        print(f"{rank:>2}. [{icon}] {r.candidate_name:<28} {r.overall_score:>3}/100  ({r.recommendation})")
        print(f"      {r.summary}")
        if r.missing_skills:
            print(f"      Missing: {', '.join(r.missing_skills[:5])}")
        print()

    if args.out:
        out = Path(args.out)
        if out.suffix == ".csv":
            _write_csv(out, results)
        else:
            out.write_text(json.dumps([r.to_dict() for r in results], indent=2), encoding="utf-8")
        print(f"Full results written to {out}")


def _write_csv(path: Path, results) -> None:
    rows = [r.to_dict() for r in results]
    for row in rows:
        for key, value in row.items():
            if isinstance(value, list):
                row[key] = "; ".join(value)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
