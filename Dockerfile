# Use a lightweight python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Environment variables for the OpenEnv instance
ENV WORKERS=4
ENV MAX_CONCURRENT_ENVS=100

# Expose server port
EXPOSE 8000

# Command to run the inference script
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
