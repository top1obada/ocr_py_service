from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import asyncio
from ocr_service_fast import FastUniversalOCR
import logging

app = FastAPI(title="Super Fast OCR API (PDF+Images)")
ocr = FastUniversalOCR()
logger = logging.getLogger("OCR API")

@app.on_event("startup")
async def startup():
    logger.info("🔄 تحميل النماذج مسبقاً...")
    asyncio.create_task(preload_models())

async def preload_models():
    ocr.load_default_reader()
    logger.info("✅ النماذج جاهزة!")

@app.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...), language: str = Form("ar")):
    contents = await file.read()
    from PIL import Image
    import io
    import numpy as np
    image = Image.open(io.BytesIO(contents))
    if image.mode in ('RGBA','LA','P'):
        rgb = Image.new('RGB', image.size, (255,255,255))
        rgb.paste(image, mask=image.split()[-1] if image.mode=='RGBA' else None)
        image = rgb
    image_np = np.array(image)
    text = await ocr.ocr_image_fast(image_np, [language])
    return JSONResponse({"text": text, "type": "image"})

@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), language: str = Form("ar")):
    contents = await file.read()
    text = await ocr.ocr_pdf_fast(contents, [language])
    return JSONResponse({"text": text, "type": "pdf"})