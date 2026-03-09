from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from ocr_service_fast import FastUniversalOCR
import asyncio
from PIL import Image
import io
import tempfile

app = FastAPI(title="Super Fast OCR API with Tesseract")
ocr = FastUniversalOCR()

@app.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...), language: str = "ar"):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    if image.mode in ('RGBA', 'LA', 'P'):
        rgb = Image.new('RGB', image.size, (255, 255, 255))
        rgb.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = rgb
    text = await ocr.ocr_image_fast(image, [language])
    return JSONResponse({"text": text, "time": "fast"})

@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), language: str = "ar"):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp.flush()
        text = await ocr.ocr_pdf_fast(tmp.name, [language])
    return JSONResponse({"text": text, "time": "fast"})

@app.get("/debug/tesseract")
async def debug_tesseract():
    """مسار لتشخيص حالة Tesseract"""
    status = await ocr.check_tesseract_status()
    return JSONResponse(status)


@app.get("/test")
async def test():
    return {"message": "Hello World"}