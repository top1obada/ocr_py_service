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
        """
        استخراج النص من صورة
        """
        try:
            # تحديد اللغة - تأكد من أن اللغة المطلوبة موجودة أولاً
            if languages is None:
                # استخدم الإنجليزية كلغة افتراضية بدلاً من العربية
                lang = 'eng'
                self.logger.info(f"🔍 استخدام اللغة الافتراضية: {lang}")
            else:
                if isinstance(languages, list):
                    # تأكد من أن العربية موجودة في القائمة
                    if 'ar' in languages:
                        # جرب العربية أولاً، لكن إذا فشلت استخدم الإنجليزية
                        try:
                            # اختبر إذا كانت العربية تعمل
                            test_langs = pytesseract.get_languages()
                            if 'ara' in test_langs:
                                lang = '+'.join(languages)
                            else:
                                self.logger.warning("⚠️ العربية غير متوفرة، استخدام الإنجليزية")
                                lang = 'eng'
                        except:
                            lang = 'eng'
                    else:
                        lang = '+'.join(languages)
                else:
                    lang = languages

            self.logger.info(f"🔍 بدء OCR لصورة باللغة: {lang}")

            # تنفيذ OCR
            text = pytesseract.image_to_string(image, lang=lang)

            self.logger.info(f"✅ تم استخراج {len(text)} حرف من الصورة")
            return text.strip()

        except Exception as e:
            self.logger.error(f"❌ خطأ في OCR الصورة: {e}")

            # محاولة بديلة بالإنجليزية فقط (بدون أي تحذير)
            try:
                self.logger.info("🔄 محاولة بديلة بالإنجليزية...")
                text = pytesseract.image_to_string(image, lang='eng')
                return text.strip()  # بدون تحذير
            except Exception as e2:
                self.logger.error(f"❌ فشلت المحاولة البديلة: {e2}")
                return f"❌ فشل OCR: {str(e)}"

    async def ocr_pdf_fast(self, pdf_path: str, languages=None):
        """
        استخراج النص من ملف PDF
        """
        try:
            # تحديد اللغة - نفس المنطق أعلاه
            if languages is None:
                lang = 'eng'
                self.logger.info(f"🔍 استخدام اللغة الافتراضية: {lang}")
            else:
                if isinstance(languages, list):
                    if 'ar' in languages:
                        try:
                            test_langs = pytesseract.get_languages()
                            if 'ara' in test_langs:
                                lang = '+'.join(languages)
                            else:
                                self.logger.warning("⚠️ العربية غير متوفرة، استخدام الإنجليزية")
                                lang = 'eng'
                        except:
                            lang = 'eng'
                    else:
                        lang = '+'.join(languages)
                else:
                    lang = languages

            self.logger.info(f"🔍 بدء OCR لملف PDF باللغة: {lang}")

            # تحقق من وجود الملف
            if not os.path.exists(pdf_path):
                return "❌ ملف PDF غير موجود"

            # تحويل PDF إلى صور
            self.logger.info("🔄 جاري تحويل PDF إلى صور...")
            try:
                pages = convert_from_path(pdf_path)
                self.logger.info(f"✅ تم تحويل {len(pages)} صفحة")
            except Exception as e:
                self.logger.error(f"❌ فشل تحويل PDF: {e}")
                return f"❌ فشل تحويل PDF: {str(e)}"

            texts = []
            for i, page in enumerate(pages):
                try:
                    self.logger.info(f"🔄 معالجة الصفحة {i + 1}/{len(pages)}")
                    page_text = pytesseract.image_to_string(page, lang=lang)
                    texts.append(page_text)
                    self.logger.info(f"✅ تم استخراج {len(page_text)} حرف من الصفحة {i + 1}")
                except Exception as e:
                    self.logger.error(f"❌ خطأ في الصفحة {i + 1}: {e}")
                    texts.append(f"[خطأ في الصفحة {i + 1}]")

                await asyncio.sleep(0)

            result = "\n".join(texts)
            self.logger.info(f"✅ تم استخراج إجمالي {len(result)} حرف من PDF")
            return result.strip()

        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة PDF: {e}")
            return f"❌ فشل معالجة PDF: {str(e)}"

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