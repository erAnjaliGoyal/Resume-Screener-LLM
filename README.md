# 🔍 LLM Resume Screener

An LLM-based resume screening system that parses resumes (PDF/DOCX/TXT), scores them against a job description using **semantic matching** — not just keywords — and returns ranked candidates with **explainable match summaries** for recruiters.

## Why

First-pass resume screening is slow and inconsistent. Keyword filters miss strong candidates who describe the same skill in different words ("built REST services in Flask" vs "API development"). This tool uses an LLM to judge *semantic fit*, surface transferable strengths, and explain every ranking — so recruiters review a short, trustworthy shortlist instead of a full inbox.

## Features

- **Multi-format parsing** — extracts text and contact metadata from `.pdf`, `.docx`, and `.txt` resumes
- **Semantic scoring** — overall, skills, experience, and education scores (0–100) judged by Claude, with guidance to recognize transferable experience
- **Explainable results** — every candidate gets matched/missing skills, transferable strengths, red flags, and a recruiter-readable summary
- **Batch ranking** — screen a whole folder of resumes and get a ranked shortlist
- **Bias guardrails** — the scoring prompt explicitly instructs the model not to penalize career gaps or infer anything from names, schools, gender, or ethnicity
- **Two interfaces** — a CLI for quick runs and a FastAPI service for integration
- **Export** — results to JSON or CSV for your ATS or spreadsheet

## Quickstart

```bash
git clone https://github.com/<your-username>/resume-screener.git
cd resume-screener
python -m venv .venv && source .venv/bin/activate
pip install -e .

export ANTHROPIC_API_KEY=sk-ant-...   # or copy .env.example to .env
```

### CLI

```bash
# Screen one resume
resume-screener examples/resumes/priya_sharma.txt --jd examples/job_description.txt

# Screen the whole sample dataset (6 resumes: PDF, DOCX, TXT)
resume-screener examples/resumes/ --jd examples/job_description.txt --out results.csv

# Screen a folder, show top 10, export everything to CSV
resume-screener ./resumes/ --jd job.txt --top 10 --out results.csv
```

Example output:

```
 1. [++] Priya Sharma                  87/100  (strong_match)
      Strong backend profile with direct LLM API integration experience...
      Missing: vector databases
```

### API

```bash
uvicorn resume_screener.api:app --reload
```

```bash
curl -X POST http://localhost:8000/screen \
  -F "job_description=<examples/job_description.txt" \
  -F "resumes=@examples/resumes/priya_sharma.txt"
```

Interactive docs at `http://localhost:8000/docs`.

## How it works

```
resumes (.pdf/.docx/.txt)
        │
        ▼
┌──────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   Parser      │───▶│  LLM Screener        │───▶│  Ranked results   │
│ text + meta   │    │  Claude + structured │    │  scores, skills,  │
│ extraction    │    │  JSON scoring rubric │    │  summary, flags   │
└──────────────┘    └─────────────────────┘    └──────────────────┘
```

1. **Parse** — `parser.py` extracts normalized text plus name/email/phone heuristics
2. **Score** — `screener.py` sends the resume + JD to Claude with a strict JSON rubric (semantic fit, recency weighting, fairness constraints) and validates the structured output
3. **Rank** — `screen_batch` sorts candidates by overall score; CLI/API format the shortlist

## Project structure

```
src/resume_screener/
├── parser.py      # PDF/DOCX/TXT extraction + metadata heuristics
├── screener.py    # LLM scoring engine with structured-output parsing
├── cli.py         # command-line interface
└── api.py         # FastAPI service
examples/          # sample dataset: 1 JD + 6 fictional resumes (PDF/DOCX/TXT)
tests/             # unit tests (pytest)
```

## Sample dataset

The repo ships with a ready-made test set in [`examples/`](examples/): a backend-engineer job description and six fictional resumes (PDF, DOCX, and TXT) ranging from strong matches to a deliberately wrong-field candidate — so you can verify the ranking behaves sensibly in one command. See [`examples/README.md`](examples/README.md) for the expected ordering.

## Running tests

```bash
pip install pytest
pytest
```

## Responsible use

This tool is a **decision-support aid, not a decision-maker**. LLM judgments can reflect biases in training data. Always keep a human in the loop, audit score distributions across candidate groups, and comply with local hiring regulations (e.g., NYC Local Law 144, EU AI Act) before using automated screening in production.

## License

MIT
