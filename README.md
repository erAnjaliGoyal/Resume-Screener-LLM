# 🔍 LLM Resume Screener

![CI](https://github.com/erAnjaliGoyal/Resume-Screener-LLM/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/erAnjaliGoyal/Resume-Screener-LLM)

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

## Run it in 1 minute

**Option A — GitHub Codespaces (nothing to install):** click the Codespaces badge above, wait for setup, then in the terminal:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
make demo
```

**Option B — Docker:**
```bash
docker build -t resume-screener .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... resume-screener
# open http://localhost:8000/docs
```

**Option C — local install:** see Quickstart below.

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
make test        # or: pip install pytest && pytest
```
Tests run automatically on every push via GitHub Actions (see badge above).

## How I built this: design decisions

**Why an LLM instead of keyword matching or classic NLP?** Keyword filters reject candidates who phrase the same skill differently, and TF-IDF/embedding similarity alone gives a score with no explanation. An LLM can judge semantic fit *and* justify it. The trade-off is cost and latency per resume, which is acceptable for screening (an inherently batch, non-realtime task).

**Structured output over free text.** The screener forces Claude to return a strict JSON schema (scores, matched/missing skills, recommendation) rather than prose. This makes results sortable, exportable to CSV/ATS, and comparable across candidates. The parser strips markdown fences and falls back to extracting the outermost JSON object, because LLMs occasionally wrap output despite instructions — defensive parsing matters.

**Explainability as a feature, not an afterthought.** Every score ships with a recruiter-readable summary, missing skills, and transferable strengths. A ranking a recruiter can't interrogate is a ranking they won't trust.

**Bias guardrails in the prompt.** The system prompt explicitly instructs the model not to penalize career gaps or infer anything from names, schools, gender, or ethnicity. This doesn't eliminate bias — see Responsible use — but it's a deliberate, auditable mitigation layer, and the prompt lives in version control where it can be reviewed.

**Two interfaces, one engine.** The scoring logic lives in `screener.py` with zero knowledge of CLI or HTTP. `cli.py` and `api.py` are thin adapters, so adding a new surface (Slack bot, batch job) means wiring, not rewriting.

**Lazy imports for graceful degradation.** The package imports the Anthropic SDK only when scoring is actually used, so parsing and tests work in environments without API dependencies installed.

**Testing strategy.** Unit tests cover the deterministic layer (parsing all three formats, metadata extraction, error handling) and run free in CI. The LLM layer is validated with the bundled sample dataset — six resumes engineered to produce a known ranking order, since exact scores are non-deterministic but ordering should be stable.

**What I'd do next.** Caching (identical resume+JD pairs shouldn't re-bill), async batch screening for large volumes, score-distribution audits across candidate groups, and a lightweight recruiter UI.

## Responsible use

This tool is a **decision-support aid, not a decision-maker**. LLM judgments can reflect biases in training data. Always keep a human in the loop, audit score distributions across candidate groups, and comply with local hiring regulations (e.g., NYC Local Law 144, EU AI Act) before using automated screening in production.

## License

MIT
