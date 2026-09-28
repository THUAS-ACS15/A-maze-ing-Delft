# Use a lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered terminal output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy dependency requirements first to leverage caching
COPY requirements.txt .

# Install dependencies if present
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy the application source code
COPY . .

# Run the terminal application (replace main.py with your entry point file)
CMD ["python", "main.py"]