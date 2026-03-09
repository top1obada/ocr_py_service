from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from ocr_service_fast import FastUniversalOCR
from PIL import Image
import io
import tempfile
import asyncio

app = FastAPI(title="Fast OCR API")

ocr = FastUniversalOCR()


@app.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...), language: str = None):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents))

    if image.mode in ("RGBA", "LA", "P"):

        rgb = Image.new("RGB", image.size, (255, 255, 255))

        rgb.paste(
            image,
            mask=image.split()[-1] if image.mode == "RGBA" else None
        )

        image = rgb

    text = await ocr.ocr_image_fast(image, [language])

    return JSONResponse({
        "text": text
    })


@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...), language: str = None):

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:

        tmp.write(await file.read())
        tmp.flush()

        text = await ocr.ocr_pdf_fast(tmp.name, [language])

    return JSONResponse({
        "text": text
    })


@app.get("/debug/tesseract")
async def debug_tesseract():

    status = await ocr.check_tesseract_status()

    return JSONResponse(status)


@app.get("/")
async def root():

    return {
        "message": "OCR API is running"
    }