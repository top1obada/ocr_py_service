# ============================ Stage 1: Build ============================
FROM python:3.12-slim AS build
ARG CACHEBUST=1
RUN echo "Build started at $(date)"
WORKDIR /app

# تثبيت الأدوات اللازمة وحزم اللغات
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra && \
    rm -rf /var/lib/apt/lists/*

# نسخ وتثبيت المتطلبات
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# ============================ Stage 2: Runtime ============================
FROM python:3.12-slim
ARG CACHEBUST=1
WORKDIR /app

# تثبيت الأدوات وحزم اللغات runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra && \
    rm -rf /var/lib/apt/lists/*

# إنشاء مسار tessdata وضمان وجود الملفات مع صلاحيات صحيحة
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata/ && \
    cp /usr/share/tesseract-ocr/5/ara.traineddata /usr/share/tesseract-ocr/5/tessdata/ || true && \
    cp /usr/share/tesseract-ocr/5/eng.traineddata /usr/share/tesseract-ocr/5/tessdata/ || true && \
    cp /usr/share/tesseract-ocr/5/fra.traineddata /usr/share/tesseract-ocr/5/tessdata/ || true && \
    chmod 644 /usr/share/tesseract-ocr/5/tessdata/*.traineddata && \
    echo "ملفات اللغة الموجودة في tessdata:" && ls -la /usr/share/tesseract-ocr/5/tessdata/

# تعيين متغير البيئة للمسار الصحيح
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# نسخ المتطلبات والكود من مرحلة البناء
COPY --from=build /install /usr/local
COPY --from=build /app .

# فتح البورت
EXPOSE 8080

# بدء التطبيق
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]