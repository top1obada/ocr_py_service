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

        # تعيين مسار Tesseract
        os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata/'

        # التحقق من التثبيت عند بدء التشغيل
        try:
            # جرب تشغيل Tesseract للتحقق
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"✅ Tesseract version: {version}")

            # تحقق من اللغات المتاحة
            installed_langs = pytesseract.get_languages()
            self.logger.info(f"✅ اللغات المتاحة: {installed_langs}")

        except Exception as e:
            self.logger.error(f"❌ خطأ في التحقق من Tesseract: {e}")
            # محاولة إصلاح المسار
            self._fix_tesseract_path()

    def _fix_tesseract_path(self):
        """محاولة إصلاح مسار Tesseract"""
        try:
            # بحث عن ملفات اللغة
            ara_files = glob.glob('/usr/share/**/ara.traineddata', recursive=True)
            if ara_files:
                tessdata_dir = os.path.dirname(ara_files[0])
                os.environ['TESSDATA_PREFIX'] = tessdata_dir + '/'
                self.logger.info(f"✅ تم تعيين TESSDATA_PREFIX إلى: {tessdata_dir}")
        except Exception as e:
            self.logger.error(f"❌ فشل إصلاح المسار: {e}")

    async def ocr_image_fast(self, image: Image.Image, languages=None):
        """
        استخراج النص من صورة
        """
        try:
            # تحديد اللغة
            if languages is None:
                lang = self.default_languages
            else:
                if isinstance(languages, list):
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

            # محاولة بديلة بالإنجليزية فقط
            try:
                self.logger.info("🔄 محاولة بديلة بالإنجليزية...")
                text = pytesseract.image_to_string(image, lang='eng')
                return text.strip() + f"\n\n[⚠️ تحذير: تم استخدام الإنجليزية بدلاً من {lang}]"
            except Exception as e2:
                self.logger.error(f"❌ فشلت المحاولة البديلة: {e2}")
                return f"❌ فشل OCR: {str(e)}"

    async def ocr_pdf_fast(self, pdf_path: str, languages=None):
        """
        استخراج النص من ملف PDF
        """
        try:
            # تحديد اللغة
            if languages is None:
                lang = self.default_languages
            else:
                if isinstance(languages, list):
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
                    texts.append(f"[خطأ في الصفحة {i + 1}: {str(e)}]")

                await asyncio.sleep(0)  # للسماح بالتبديل بين المهام

            result = "\n".join(texts)
            self.logger.info(f"✅ تم استخراج إجمالي {len(result)} حرف من PDF")
            return result.strip()

        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة PDF: {e}")
            return f"❌ فشل معالجة PDF: {str(e)}"

    async def check_tesseract_status(self):
        """
        التحقق من حالة Tesseract (للتشخيص)
        """
        result = {
            "status": "unknown",
            "tesseract_version": None,
            "languages": [],
            "tessdata_prefix": os.environ.get('TESSDATA_PREFIX', 'غير معرف'),
            "ara_file_exists": False,
            "ara_file_path": None,
            "possible_paths": [],
            "error": None
        }

        try:
            # نسخة Tesseract
            version = subprocess.run(['tesseract', '--version'],
                                     capture_output=True, text=True)
            result["tesseract_version"] = version.stdout.split('\n')[0] if version.stdout else None

            # اللغات المثبتة
            langs = subprocess.run(['tesseract', '--list-langs'],
                                   capture_output=True, text=True)
            if langs.stdout:
                lines = langs.stdout.strip().split('\n')
                if len(lines) > 1:
                    result["languages"] = lines[1:]  # أول سطر هو العنوان

            # البحث عن كل ملفات اللغة
            result["possible_paths"] = glob.glob('/usr/share/**/ara.traineddata', recursive=True)

            # هل ملف العربية موجود؟
            for path in result["possible_paths"]:
                if os.path.exists(path):
                    result["ara_file_exists"] = True
                    result["ara_file_path"] = path
                    break

            result["status"] = "✅ يعمل" if result["languages"] else "⚠️ مشكلة"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "❌ خطأ"

        return result

    async def diagnose_tessdata(self):
        """
        تشخيص مشاكل مسار tessdata بشكل مفصل
        """
        result = {
            "tesseract_version": None,
            "installed_langs": [],
            "tessdata_prefix": os.environ.get('TESSDATA_PREFIX', 'غير معرف'),
            "possible_tessdata_paths": [],
            "ara_files_found": [],
            "working_path": None,
            "error": None
        }

        try:
            # نسخة Tesseract
            version = subprocess.run(['tesseract', '--version'],
                                     capture_output=True, text=True)
            result["tesseract_version"] = version.stdout.split('\n')[0] if version.stdout else None

            # بحث عن كل مجلدات tessdata
            result["possible_tessdata_paths"] = glob.glob('/usr/share/**/tessdata', recursive=True)

            # بحث عن ملف العربية
            result["ara_files_found"] = glob.glob('/usr/share/**/ara.traineddata', recursive=True)

            # محاولة تشغيل tesseract مع مسارات مختلفة
            for path in result["possible_tessdata_paths"]:
                try:
                    # تعيين المسار مؤقتاً
                    env = os.environ.copy()
                    env['TESSDATA_PREFIX'] = path + '/'

                    test_result = subprocess.run(['tesseract', '--list-langs'],
                                                 env=env,
                                                 capture_output=True, text=True)
                    if test_result.returncode == 0:
                        result["working_path"] = path
                        result["working_langs"] = test_result.stdout.strip().split('\n')[1:]
                        break
                except:
                    continue

        except Exception as e:
            result["error"] = str(e)

        return result