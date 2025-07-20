FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ./src/

# Add src to Python path
ENV PYTHONPATH=/app/src

# Run the server
CMD ["python", "-m", "tech_doc_generator.a2a.server"]