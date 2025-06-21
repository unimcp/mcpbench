FROM python:3.11-slim

WORKDIR /app

# Copy template files first (these will be overwritten by version-specific files if they exist)
COPY matrix/templates/python/server /app

# Copy version-specific files (these will overwrite templates if needed)
COPY matrix/python/server/v1.9.3 /app

# Copy requirements and install dependencies
COPY matrix/python/server/v1.9.3/requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Command to run the server
CMD ["python", "-m", "basic_server"] 