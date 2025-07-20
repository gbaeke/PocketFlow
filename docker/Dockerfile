FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source package
COPY src/ ./src/

# Set Python path to include src directory and run as module
ENV PYTHONPATH="/app/src"
CMD ["python", "-m", "tech_doc_generator.a2a.server"] 