from pathlib import Path

from resume_screener.parser import parse_resume

EXAMPLES = Path(__file__).parent.parent / "examples"


def test_parse_txt_resume():
    resume = parse_resume(EXAMPLES / "resumes" / "priya_sharma.txt")
    assert "FastAPI" in resume.raw_text
    assert resume.email == "priya.sharma@example.com"
    assert resume.candidate_name == "Priya Sharma"


def test_unsupported_extension(tmp_path):
    bad = tmp_path / "resume.xyz"
    bad.write_text("hello")
    try:
        parse_resume(bad)
        assert False, "should have raised"
    except ValueError as e:
        assert "Unsupported" in str(e)


def test_parse_pdf_resume():
    resume = parse_resume(EXAMPLES / "resumes" / "meera_krishnan.pdf")
    assert "FastAPI" in resume.raw_text
    assert resume.email == "meera.krishnan@example.com"


def test_parse_docx_resume():
    resume = parse_resume(EXAMPLES / "resumes" / "arjun_deshpande.docx")
    assert "pgvector" in resume.raw_text
    assert resume.candidate_name == "Arjun Deshpande"


def test_parse_directory():
    from resume_screener.parser import parse_directory

    resumes = parse_directory(EXAMPLES / "resumes")
    assert len(resumes) == 6
