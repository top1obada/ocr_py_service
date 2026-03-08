FROM python:3.12-slim

WORKDIR /app

# تثبيت Tesseract و poppler لتحويل PDF إلى صور
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev poppler-utils && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]