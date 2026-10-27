"""Core screening engine: scores a parsed resume against a job description using an LLM."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import anthropic

from .parser import ParsedResume

SYSTEM_PROMPT = """You are an expert technical recruiter assistant. You evaluate how well a candidate's resume matches a job description.

You must respond ONLY with a valid JSON object, no markdown fences, no preamble, with this exact schema:
{
  "overall_score": <int 0-100>,
  "skill_match_score": <int 0-100>,
  "experience_match_score": <int 0-100>,
  "education_match_score": <int 0-100>,
  "matched_skills": [<strings: skills present in both resume and JD>],
  "missing_skills": [<strings: important JD skills absent from resume>],
  "transferable_strengths": [<strings: adjacent/transferable experience worth noting>],
  "red_flags": [<strings: gaps or concerns, empty list if none>],
  "summary": "<2-3 sentence explanation of the ranking, written for a recruiter>",
  "recommendation": "<one of: strong_match | potential_match | weak_match>"
}

Scoring guidance:
- Judge semantic fit, not keyword overlap (e.g. "built REST services in Flask" satisfies "API development experience").
- Weight recent, hands-on experience over listed-but-unused skills.
- Be fair: do not penalize career gaps, names, schools, or anything suggesting age, gender, or ethnicity.
"""


@dataclass
class ScreeningResult:
    candidate_name: str
    overall_score: int
    skill_match_score: int
    experience_match_score: int
    education_match_score: int
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    transferable_strengths: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    summary: str = ""
    recommendation: str = "weak_match"
    source_file: str = ""

    def to_dict(self) -> dict:
        return self.__dict__.copy()


class ResumeScreener:
    """Scores resumes against a job description with Claude."""

    def __init__(self, model: str = "claude-sonnet-5-5", api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = model

    def screen(self, resume: ParsedResume, job_description: str) -> ScreeningResult:
        user_prompt = (
            f"JOB DESCRIPTION:\n{job_description.strip()}\n\n"
            f"CANDIDATE RESUME:\n{resume.raw_text.strip()}\n\n"
            "Evaluate the candidate against the job description and respond with the JSON object."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        data = self._parse_json(text)

        return ScreeningResult(
            candidate_name=resume.candidate_name or "Unknown",
            overall_score=int(data.get("overall_score", 0)),
            skill_match_score=int(data.get("skill_match_score", 0)),
            experience_match_score=int(data.get("experience_match_score", 0)),
            education_match_score=int(data.get("education_match_score", 0)),
            matched_skills=data.get("matched_skills", []),
            missing_skills=data.get("missing_skills", []),
            transferable_strengths=data.get("transferable_strengths", []),
            red_flags=data.get("red_flags", []),
            summary=data.get("summary", ""),
            recommendation=data.get("recommendation", "weak_match"),
            source_file=resume.source_file,
        )

    def screen_batch(self, resumes: list[ParsedResume], job_description: str) -> list[ScreeningResult]:
        """Screen multiple resumes and return them ranked best-first."""
        results = [self.screen(r, job_description) for r in resumes]
        return sorted(results, key=lambda r: r.overall_score, reverse=True)

    @staticmethod
    def _parse_json(text: str) -> dict:
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fall back: grab the outermost JSON object if the model added prose.
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start != -1 and end != -1:
                return json.loads(cleaned[start : end + 1])
            raise
