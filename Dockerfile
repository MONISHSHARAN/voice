FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 5000 5001

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start the application
CMD ["python", "start.py"]