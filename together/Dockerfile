# Use a more standard Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /app

RUN mkdir -p /root/.aws

# Install dependencies
COPY together/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -v

RUN pip install uvicorn
# Copy app files into container
COPY together/ .
COPY shared ./shared

# Command to run the application using Uvicorn
CMD ["uvicorn", "--workers", "2", "together_app:app", "--host", "0.0.0.0", "--port", "10010"]
