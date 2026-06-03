import requests
import base64
import io
import asyncio
import logging
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class CaptchaHandler:
    # 验证码处理器
    
    def __init__(self, service: str = "2captcha", api_key: str = ""):
        self.service = service.lower()
        self.api_key = api_key
        self._fallback_services = ["2captcha", "local", "manual"]
    
    async def solve_from_element(self, page: Page, selector: str) -> str:
        # 从页面元素识别验证码
        element = await page.query_selector(selector)
        if not element:
            raise Exception("验证码元素未找到")
        
        screenshot = await element.screenshot()
        image = Image.open(io.BytesIO(screenshot))
        return await self.solve(image)
    
    async def solve(self, image: Image.Image) -> str:
        # 识别验证码（带备用方案）
        services = [self.service] + [s for s in self._fallback_services if s != self.service]
        
        for service in services:
            try:
                logger.info(f"尝试使用 {service} 识别验证码...")
                result = await self._solve_with_service(image, service)
                if result:
                    logger.info(f"{service} 识别成功: {result}")
                    return result
            except Exception as e:
                logger.warning(f"{service} 识别失败: {e}")
                continue
        
        raise Exception("所有验证码识别方案均失败")
    
    async def _solve_with_service(self, image: Image.Image, service: str) -> str:
        # 使用指定服务识别
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        if service == "2captcha":
            return await self._solve_2captcha(img_base64)
        elif service == "local":
            return await self._solve_local(image)
        elif service == "manual":
            return await self._solve_manual(image)
        else:
            raise ValueError(f"不支持的验证码服务: {service}")
    
    async def _solve_2captcha(self, img_base64: str) -> str:
        # 2Captcha服务
        if not self.api_key:
            raise ValueError("未配置2Captcha API密钥")
        
        # 提交验证码
        resp = requests.post("http://2captcha.com/in.php", data={
            "key": self.api_key,
            "method": "base64",
            "body": img_base64,
            "json": 1,
            "phrase": 0,
            "regsense": 1,
        }, timeout=30)
        result = resp.json()
        
        if result.get("status") != 1:
            raise Exception(f"2Captcha提交失败: {result}")
        
        captcha_id = result["request"]
        
        # 轮询结果
        for i in range(30):
            await asyncio.sleep(5)
            check = requests.get("http://2captcha.com/res.php", params={
                "key": self.api_key,
                "action": "get",
                "id": captcha_id,
                "json": 1
            }, timeout=30)
            check_result = check.json()
            
            if check_result.get("status") == 1:
                return check_result["request"]
            
            if check_result.get("request") == "CAPCHA_NOT_READY":
                continue
            
            raise Exception(f"2Captcha识别失败: {check_result}")
        
        raise Exception("2Captcha识别超时")
    
    async def _solve_local(self, image: Image.Image) -> str:
        # 本地OCR识别
        try:
            import pytesseract
            
            # 图像预处理
            processed = self._preprocess_image(image)
            
            # OCR识别
            text = pytesseract.image_to_string(
                processed,
                config="--psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )
            result = text.strip().replace(" ", "").replace("\n", "")
            
            if len(result) >= 4:  # 验证码通常至少4位
                return result
            else:
                raise Exception(f"识别结果太短: {result}")
                
        except ImportError:
            raise Exception("未安装pytesseract，请执行: pip install pytesseract")
        except Exception as e:
            raise Exception(f"本地OCR失败: {e}")
    
    async def _solve_manual(self, image: Image.Image) -> str:
        # 手动输入
        # 保存图片供用户查看
        temp_path = "temp_captcha.png"
        image.save(temp_path)
        print(f"\n验证码已保存: {temp_path}")
        
        # 在异步环境中获取输入
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: input("请输入验证码: "))
        return result.strip()
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        # 图像预处理
        # 1. 转换为灰度图
        gray = image.convert("L")
        
        # 2. 增强对比度
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)
        
        # 3. 二值化
        threshold = 128
        binary = enhanced.point(lambda x: 0 if x < threshold else 255, "1")
        
        # 4. 去噪
        denoised = binary.filter(ImageFilter.MedianFilter(size=3))
        
        return denoised
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        # 增强图像质量
        # 调整大小
        width, height = image.size
        if width < 200:
            image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        
        # 锐化
        sharpened = image.filter(ImageFilter.SHARPEN)
        
        return sharpened
