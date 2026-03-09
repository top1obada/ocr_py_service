FROM python:3.12-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت Tesseract مع اللغات المطلوبة و poppler-utils لتحويل PDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي المشروع
COPY . .

# تعيين متغير البيئة للـ tessdata
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# فتح المنفذ
EXPOSE 8080

# أمر التشغيل
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080","--workers","4"]