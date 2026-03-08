# ============================ Stage 1: Build ============================
FROM python:3.12-slim AS build
WORKDIR /app

# تثبيت الأدوات لنظام البناء
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# نسخ الملفات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

# ============================ Stage 2: Runtime ============================
FROM python:3.12-slim
WORKDIR /app

# تثبيت الأدوات للنظام فقط
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# نسخ كل شيء من مرحلة البناء
COPY --from=build /install /usr/local
COPY --from=build /app .

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]