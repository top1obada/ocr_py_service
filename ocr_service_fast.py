from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import asyncio
import logging

class FastUniversalOCR:
    def __init__(self):  # ✅ صح
        self.logger = logging.getLogger("FastUniversalOCR")
        self.default_languages = 'ara+eng+fra'

    async def ocr_image_fast(self, image: Image.Image, languages=None):
        lang = self.default_languages if languages is None else '+'.join(languages)
        text = pytesseract.image_to_string(image, lang=lang)
        return text

    async def ocr_pdf_fast(self, pdf_path: str, languages=None):
        lang = self.default_languages if languages is None else '+'.join(languages)
        pages = convert_from_path(pdf_path)
        texts = []
        for page in pages:
            texts.append(pytesseract.image_to_string(page, lang=lang))
            await asyncio.sleep(0)  # للسماح بالتبديل
        return "\n".join(texts)