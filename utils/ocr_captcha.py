import ddddocr
import os
import logging

logger = logging.getLogger(__name__)

class CaptchaOCR:
    """本地 OCR 验证码识别"""
    
    def __init__(self):
        try:
            self.ocr = ddddocr.DdddOcr(show_ad=False)
            logger.info("OCR 引擎初始化成功")
        except Exception as e:
            logger.error(f"OCR 引擎初始化失败: {e}")
            self.ocr = None
    
    def recognize(self, image_path):
        """识别验证码图片"""
        if not self.ocr:
            logger.error("OCR 引擎未初始化")
            return None
        
        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            result = self.ocr.classification(image_bytes)
            logger.info(f"OCR 识别结果: {result}")
            return result
        except Exception as e:
            logger.error(f"OCR 识别失败: {e}")
            return None
    
    def recognize_bytes(self, image_bytes):
        """从字节流识别验证码"""
        if not self.ocr:
            return None
        
        try:
            result = self.ocr.classification(image_bytes)
            return result
        except Exception as e:
            logger.error(f"OCR 识别失败: {e}")
            return None

# 全局实例
ocr_solver = CaptchaOCR()
