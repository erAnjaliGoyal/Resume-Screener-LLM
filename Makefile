.PHONY: install test demo api docker

install:
	pip install -e . && pip install pytest

test:
	pytest -v

demo:
	resume-screener examples/resumes/ --jd examples/job_description.txt --top 6

api:
	uvicorn resume_screener.api:app --reload

docker:
	docker build -t resume-screener .
	docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY) resume-screener
