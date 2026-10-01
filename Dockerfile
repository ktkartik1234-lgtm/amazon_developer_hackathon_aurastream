FROM python:3.13-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml README.md ./
COPY core ./core
COPY client ./client
COPY run.py ./

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]
