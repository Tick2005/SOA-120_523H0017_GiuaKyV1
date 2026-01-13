FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl (used by docker healthchecks)
RUN apt-get update && apt-get install -y curl \ 
	&& rm -rf /var/lib/apt/lists/*

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8006

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
