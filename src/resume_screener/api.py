"""FastAPI service: upload resumes + a job description, get ranked results back.

Run with:  uvicorn resume_screener.api:app --reload
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from .parser import parse_resume
from .screener import ResumeScreener

app = FastAPI(
    title="Resume Screener API",
    description="LLM-based resume screening: upload resumes and a job description, get ranked, explainable matches.",
    version="1.0.0",
)

screener = ResumeScreener()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/screen")
async def screen(
    job_description: str = Form(..., description="The full job description text"),
    resumes: list[UploadFile] = File(..., description="One or more resumes (.pdf, .docx, .txt)"),
) -> dict:
    if not job_description.strip():
        raise HTTPException(status_code=422, detail="Job description must not be empty.")

    parsed = []
    for upload in resumes:
        suffix = Path(upload.filename or "resume.txt").suffix or ".txt"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await upload.read())
            tmp_path = Path(tmp.name)
        try:
            resume = parse_resume(tmp_path)
            resume.source_file = upload.filename or resume.source_file
            parsed.append(resume)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"{upload.filename}: {exc}") from exc
        finally:
            tmp_path.unlink(missing_ok=True)

    results = screener.screen_batch(parsed, job_description)
    return {
        "job_description_preview": job_description[:200],
        "candidates_screened": len(results),
        "results": [r.to_dict() for r in results],
    }
