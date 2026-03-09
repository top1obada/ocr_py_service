from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import asyncio
import logging
import os
import subprocess
import glob


class FastUniversalOCR:
    def __init__(self):
        self.logger = logging.getLogger("FastUniversalOCR")
        self.default_languages = 'ara+eng+fra'

        # تعيين المسار الصحيح بالقوة
        correct_path = '/usr/share/tesseract-ocr/5/tessdata/'
        os.environ['TESSDATA_PREFIX'] = correct_path

        # تأكد من وجود الملفات
        ara_file = os.path.join(correct_path, 'ara.traineddata')
        if os.path.exists(ara_file):
            self.logger.info(f"✅ ملف العربية موجود: {ara_file}")
        else:
            self.logger.error(f"❌ ملف العربية غير موجود: {ara_file}")

        # اختبار Tesseract
        try:
            # جرب مسار Tesseract
            result = subprocess.run(['tesseract', '--version'],
                                    capture_output=True, text=True)
            self.logger.info(f"✅ Tesseract version: {result.stdout.split(chr(10))[0]}")

            # جرب قائمة اللغات
            langs = subprocess.run(['tesseract', '--list-langs'],
                                   capture_output=True, text=True)
            self.logger.info(f"✅ Languages from tesseract: {langs.stdout}")

            # إذا نجح الاختبار، استخدم pytesseract
            pytesseract.get_tesseract_version()
            self.logger.info("✅ pytesseract يعمل بشكل صحيح")

        except Exception as e:
            self.logger.error(f"❌ خطأ في Tesseract: {e}")

    async def ocr_image_fast(self, image: Image.Image, languages=None):
        try:
            if languages is None:
                lang = self.default_languages
            else:
                if isinstance(languages, list):
                    lang = '+'.join(languages)
                else:
                    lang = languages

            self.logger.info(f"🔍 بدء OCR باللغة: {lang}")

            # استخدام pytesseract مع تعيين المسار مباشرة
            text = pytesseract.image_to_string(image, lang=lang)

            return text.strip()

        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            # محاولة بالإنجليزية
            try:
                text = pytesseract.image_to_string(image, lang='eng')
                return text.strip() + f"\n\n[⚠️ تم استخدام الإنجليزية]"
            except:
                return f"❌ فشل OCR: {str(e)}"

    async def ocr_pdf_fast(self, pdf_path: str, languages=None):
        try:
            if languages is None:
                lang = self.default_languages
            else:
                if isinstance(languages, list):
                    lang = '+'.join(languages)
                else:
                    lang = languages

            self.logger.info(f"🔍 بدء OCR لـ PDF باللغة: {lang}")

            # تحويل PDF إلى صور
            pages = convert_from_path(pdf_path)
            self.logger.info(f"✅ تم تحويل {len(pages)} صفحة")

            texts = []
            for i, page in enumerate(pages):
                try:
                    self.logger.info(f"🔄 معالجة الصفحة {i + 1}")
                    page_text = pytesseract.image_to_string(page, lang=lang)
                    texts.append(page_text)
                except Exception as e:
                    self.logger.error(f"❌ خطأ في الصفحة {i + 1}: {e}")
                    texts.append(f"[خطأ في الصفحة {i + 1}]")

                await asyncio.sleep(0)

            return "\n".join(texts)

        except Exception as e:
            self.logger.error(f"❌ خطأ: {e}")
            return f"❌ فشل: {str(e)}"

    async def check_tesseract_status(self):
        """التحقق من حالة Tesseract"""
        result = {
            "tesseract_version": None,
            "languages": [],
            "tessdata_prefix": os.environ.get('TESSDATA_PREFIX', 'غير معرف'),
            "ara_file_exists": False,
            "error": None
        }

        try:
            # نسخة Tesseract
            version = subprocess.run(['tesseract', '--version'],
                                     capture_output=True, text=True)
            result["tesseract_version"] = version.stdout.split('\n')[0]

            # اللغات المثبتة
            langs = subprocess.run(['tesseract', '--list-langs'],
                                   capture_output=True, text=True)
            if langs.stdout:
                result["languages"] = [l for l in langs.stdout.strip().split('\n') if l][1:]

            # هل ملف العربية موجود؟
            ara_path = '/usr/share/tesseract-ocr/5/tessdata/ara.traineddata'
            result["ara_file_exists"] = os.path.exists(ara_path)

        except Exception as e:
            result["error"] = str(e)

        return result