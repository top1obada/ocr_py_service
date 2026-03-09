import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import asyncio
import logging
import os
import subprocess


class FastUniversalOCR:

    def init(self):

        self.logger = logging.getLogger("FastUniversalOCR")
        logging.basicConfig(level=logging.INFO)

        correct_path = "/usr/share/tesseract-ocr/5/tessdata/"
        os.environ["TESSDATA_PREFIX"] = correct_path

        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True
            )

            self.logger.info(result.stdout.split("\n")[0])

        except Exception as e:
            self.logger.error(e)

    async def ocr_image_fast(self, image: Image.Image, languages=None):

        try:

            if languages is None:
                lang = "eng"
            else:
                if isinstance(languages, list):
                    lang = "+".join(languages)
                else:
                    lang = languages

            text = await asyncio.to_thread(
                pytesseract.image_to_string,
                image,
                lang=lang
            )

            return text.strip()

        except Exception as e:
            self.logger.error(e)
            return str(e)

    async def ocr_pdf_fast(self, pdf_path: str, languages=None):

        try:

            if languages is None:
                lang = "eng"
            else:
                if isinstance(languages, list):
                    lang = "+".join(languages)
                else:
                    lang = languages

            if not os.path.exists(pdf_path):
                return "PDF not found"

            self.logger.info("Converting PDF to images")

            pages = await asyncio.to_thread(
                convert_from_path,
                pdf_path
            )

            async def process_page(page):

                return await asyncio.to_thread(
                    pytesseract.image_to_string,
                    page,
                    lang=lang
                )

            tasks = []

            for page in pages:
                tasks.append(process_page(page))

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