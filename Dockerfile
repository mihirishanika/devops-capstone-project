# Dockerfile

# 1. Use a slim Python base image
FROM python:3.9-slim

# 2. Create working directory and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application code
COPY service/ ./service/

# 4. Create non-root user and switch to it
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia

# 5. Expose port and run gunicorn
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]
