"""LLM-based resume screening system."""

from .parser import ParsedResume, parse_directory, parse_resume

__all__ = ["ParsedResume", "parse_resume", "parse_directory", "ResumeScreener", "ScreeningResult"]
__version__ = "1.0.0"


def __getattr__(name):
    # Lazy import so parsing works even if the `anthropic` SDK isn't installed.
    if name in {"ResumeScreener", "ScreeningResult"}:
        from .screener import ResumeScreener, ScreeningResult

        return {"ResumeScreener": ResumeScreener, "ScreeningResult": ScreeningResult}[name]
    raise AttributeError(f"module 'resume_screener' has no attribute {name!r}")
