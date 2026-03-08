import easyocr
import numpy as np
from functools import lru_cache
import asyncio
import concurrent.futures
import logging
from PIL import Image
import cv2
from pdf2image import convert_from_bytes

class FastUniversalOCR:
    def init(self):
        self.default_languages = ['ar', 'en', 'fr']
        self.reader = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.logger = logging.getLogger("FastUniversalOCR")

    def load_default_reader(self):
        if self.reader is None:
            self.logger.info("🚀 تحميل النماذج الأساسية...")
            self.reader = easyocr.Reader(
                self.default_languages,
                gpu=False,
                model_storage_directory='/tmp/ocr_models',
                download_enabled=True
            )
        return self.reader

    @lru_cache(maxsize=32)
    def get_reader(self, lang_tuple):
        languages = list(lang_tuple)
        return easyocr.Reader(
            languages,
            gpu=False,
            model_storage_directory='/tmp/ocr_models'
        )

    async def ocr_image_fast(self, image, languages=['ar','en']):
        if set(languages) == set(self.default_languages):
            reader = self.load_default_reader()
        else:
            lang_tuple = tuple(sorted(languages))
            reader = self.get_reader(lang_tuple)

        loop = asyncio.get_event_loop()

        if image.shape[0] > 1000 or image.shape[1] > 1000:
            scale = 1000 / max(image.shape)
            new_width = int(image.shape[1] * scale)
            new_height = int(image.shape[0] * scale)
            image = cv2.resize(image, (new_width, new_height))

        result = await loop.run_in_executor(
            self.executor,
            reader.readtext,
            image,
            '',
            '',
            False,
            0.3
        )
        texts = [item[1] for item in result if len(item) >= 2]
        return " ".join(texts)

    async def ocr_pdf_fast(self, pdf_bytes, languages=['ar','en']):
        images = convert_from_bytes(pdf_bytes)
        tasks = []
        for img in images:
            image_np = np.array(img)
            tasks.append(self.ocr_image_fast(image_np, languages))
        results = await asyncio.gather(*tasks)
        return "\n".join(results)