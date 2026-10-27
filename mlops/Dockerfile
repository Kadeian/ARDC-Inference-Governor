FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY c4l ./c4l
RUN pip install --no-cache-dir . && useradd --uid 10001 --create-home app
USER 10001
EXPOSE 8000
CMD ["uvicorn", "c4l.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--limit-concurrency", "32"]
