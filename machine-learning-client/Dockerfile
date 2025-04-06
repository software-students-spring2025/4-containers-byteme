# machine-learning-client/Dockerfile
FROM python:3.11-slim

WORKDIR /app-ml-client

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code into the container
COPY . .

# Run the ML API when the container starts
CMD ["python", "ml_client.py"]