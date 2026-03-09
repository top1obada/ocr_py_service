# ============================ Stage 1: Build ============================
FROM python:3.12-slim AS build
ARG CACHEBUST=1
RUN echo "Build started at $(date)"
WORKDIR /app

# تثبيت الأدوات مع حزم اللغات
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
ARG CACHEBUST=1
RUN echo "Build started at $(date)"
WORKDIR /app

# تثبيت الأدوات مع حزم اللغات
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra && \
    rm -rf /var/lib/apt/lists/*

# إنشاء المجلد المطلوب ونسخ ملفات اللغة إليه
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata/ && \
    find /usr/share -name "*.traineddata" -exec cp {} /usr/share/tesseract-ocr/5/tessdata/ \; 2>/dev/null || true && \
    echo "ملفات اللغة في المسار الجديد:" && ls -la /usr/share/tesseract-ocr/5/tessdata/ | grep -E "ara|eng|fra"

# تعيين متغير البيئة للمسار الصحيح
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# التحقق من التثبيت
RUN echo "اللغات المثبتة:" && tesseract --list-langs

# نسخ الملفات من مرحلة البناء
COPY --from=build /install /usr/local
COPY --from=build /app .

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]