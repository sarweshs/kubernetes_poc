FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Load environment variables if .env file exists
CMD ["python", "-c", "import os; from dotenv import load_dotenv; load_dotenv(); import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=8000)"]