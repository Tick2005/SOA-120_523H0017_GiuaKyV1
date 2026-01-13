# api-gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Install curl (used by docker healthchecks and internal checks)
RUN apt-get update && apt-get install -y curl \ 
	&& rm -rf /var/lib/apt/lists/*

# UI files sẽ được mount từ docker-compose volumes

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
