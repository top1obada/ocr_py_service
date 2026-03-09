import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import asyncio
import logging
import os
import subprocess

class FastUniversalOCR:
    def __init__(self):
        self.logger = logging.getLogger("FastUniversalOCR")
        logging.basicConfig(level=logging.INFO)

        # المسار الصحيح للـ tessdata
        correct_path = "/usr/share/tesseract-ocr/5/tessdata/"
        os.environ["TESSDATA_PREFIX"] = correct_path

        # التحقق من تثبيت tesseract
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True
            )
            self.logger.info(result.stdout.split("\n")[0])
        except Exception as e:
            self.logger.error(e)

        # هنا نحدد جميع اللغات المثبتة التي نريد دعمها
        self.supported_languages = ["ara", "eng", "fra"]  # أضف أي لغة تريد دعمها
        self.lang_code = "+".join(self.supported_languages)

    async def ocr_image_fast(self, image: Image.Image):
        try:
            text = await asyncio.to_thread(
                pytesseract.image_to_string,
                image,
                lang=self.lang_code
            )
            return text.strip()
        except Exception as e:
            self.logger.error(e)
            return str(e)

    async def ocr_pdf_fast(self, pdf_path: str):
        try:
            if not os.path.exists(pdf_path):
                return "PDF not found"

            self.logger.info("Converting PDF to images")
            pages = await asyncio.to_thread(convert_from_path, pdf_path)

            async def process_page(page):
                return await asyncio.to_thread(
                    pytesseract.image_to_string,
                    page,
                    lang=self.lang_code
                )

            tasks = [process_page(page) for page in pages]
            results = await asyncio.gather(*tasks)
            return "\n".join(results).strip()

        except Exception as e:
            self.logger.error(e)
            return str(e)

    async def check_tesseract_status(self):
        result = {
            "tesseract_version": None,
            "languages": [],
            "tessdata_prefix": os.environ.get("TESSDATA_PREFIX"),
            "ara_exists": False
        }
        try:
            version = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True
            )
            result["tesseract_version"] = version.stdout.split("\n")[0]

            langs = subprocess.run(
                ["tesseract", "--list-langs"],
                capture_output=True,
                text=True
            )
            result["languages"] = langs.stdout.split("\n")
            ara_path = "/usr/share/tesseract-ocr/5/tessdata/ara.traineddata"
            result["ara_exists"] = os.path.exists(ara_path)
        except Exception as e:
            result["error"] = str(e)
        return result