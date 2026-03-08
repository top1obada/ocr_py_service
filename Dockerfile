# ============================ Stage 1: Build ============================
FROM python:3.12-slim AS build
WORKDIR /app

# تثبيت الأدوات مع حزم اللغات (مع إجبار عدم استخدام cache)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

# ============================ Stage 2: Runtime ============================
FROM python:3.12-slim
WORKDIR /app

# تثبيت الأدوات مع حزم اللغات (مع إجبار عدم استخدام cache)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra && \
    rm -rf /var/lib/apt/lists/*

# تأكد من وجود اللغات المطلوبة
RUN tesseract --list-langs

# نسخ الملفات من مرحلة البناء
COPY --from=build /install /usr/local
COPY --from=build /app .

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]