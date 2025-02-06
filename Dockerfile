# Build stage
FROM cgr.dev/chainguard/python:latest-dev AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a virtual environment
RUN python -m venv /app/venv

# Set the path to the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy and install requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY echo-server.py ./

# Clean up any python cache
RUN find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

# Runtime stage with minimal image
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# Copy only the necessary files from builder
COPY echo-server.py ./
COPY --from=builder /app/venv /venv

# Port configuration
EXPOSE 8000

# Run the application with -B flag to prevent writing pyc files
# CMD ["/usr/bin/python", "-B", "/app/echo-server.py"]
ENTRYPOINT [ "python", "/app/echo-server.py" ]