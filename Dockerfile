FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e .

COPY examples/ examples/

EXPOSE 8000
CMD ["uvicorn", "resume_screener.api:app", "--host", "0.0.0.0", "--port", "8000"]
