import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from PIL import Image

class SmartOCR:
    """智能 OCR - 自动修正常见混淆字符"""
    
    # 常见混淆字符映射
    CONFUSION_MAP = {
        'o': '0',  # 字母o -> 数字0
        'O': '0',  # 字母O -> 数字0
        'l': '1',  # 字母l -> 数字1
        'I': '1',  # 字母I -> 数字1
        'i': '1',  # 字母i -> 数字1
        'z': '2',  # 字母z -> 数字2
        'Z': '2',  # 字母Z -> 数字2
        's': '5',  # 字母s -> 数字5
        'S': '5',  # 字母S -> 数字5
        'b': '6',  # 字母b -> 数字6
        'B': '8',  # 字母B -> 数字8
        'g': '9',  # 字母g -> 数字9
        'q': '9',  # 字母q -> 数字9
    }
    
    def __init__(self):
        import ddddocr
        self.ocr = ddddocr.DdddOcr()
    
    def recognize(self, image_path):
        """识别验证码"""
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        result = self.ocr.classification(image_bytes)
        return result
    
    def fix_confusion(self, text):
        """修正混淆字符"""
        fixed = []
        for char in text:
            if char in self.CONFUSION_MAP:
                fixed.append(self.CONFUSION_MAP[char])
            else:
                fixed.append(char)
        return ''.join(fixed)
    
    def recognize_with_fix(self, image_path):
        """识别并修正"""
        raw = self.recognize(image_path)
        fixed = self.fix_confusion(raw)
        return raw, fixed

async def smart_ocr_login():
    """使用智能 OCR 登录"""
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - 智能 OCR 自动登录")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 1. 点击律师用户
        print("[1/6] 点击律师用户标签...")
        await browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '律师用户') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(2)
        
        # 2. 点击密码登录
        print("[2/6] 点击密码登录...")
        await browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '密码登录') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(2)
        
        # 3. 获取输入框
        inputs = await browser.page.query_selector_all(".uni-input-input")
        print(f"[3/6] 找到 {len(inputs)} 个输入框")
        
        # 4. 填写账号密码
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("[4/6] 已填写账号密码")
        
        # 5. 截图验证码
        if len(inputs) >= 3:
            full_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_full.png")
            await browser.page.screenshot(path=full_path)
            
            img = Image.open(full_path)
            width, height = img.size
            
            # 裁剪验证码区域
            scale_x = width / 1920
            scale_y = height / 1080
            
            left = int((1471 - 5) * scale_x)
            top = int((467 - 5) * scale_y)
            right = int((1471 + 100 + 5) * scale_x)
            bottom = int((467 + 51 + 5) * scale_y)
            
            captcha_img = img.crop((left, top, right, bottom))
            captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_ocr.png")
            captcha_img.save(captcha_path)
            print(f"[5/6] 验证码截图已保存")
            
            # 6. 使用智能 OCR 识别
            print("[6/6] 使用智能 OCR 识别验证码...")
            smart_ocr = SmartOCR()
            
            raw, fixed = smart_ocr.recognize_with_fix(captcha_path)
            print(f"原始识别: {raw}")
            print(f"修正后:   {fixed}")
            
            # 尝试使用修正后的验证码
            captcha_code = fixed
            
            if captcha_code and len(captcha_code) >= 3:
                await inputs[2].fill(captcha_code)
                
                # 点击登录
                await browser.page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        for (const el of elements) {
                            if (el.textContent && el.textContent.trim() === '登录') {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                print("已点击登录按钮")
                
                await asyncio.sleep(5)
                
                # 检查登录结果
                if "login" not in browser.page.url:
                    print("\n✓ 登录成功!")
                    await browser.save_session()
                    print("✓ 会话已保存")
                    
                    # 测试访问保全页面
                    print("\n测试访问保全页面...")
                    await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
                    await asyncio.sleep(3)
                    
                    if "login" not in browser.page.url:
                        print("✓ 可以正常访问保全页面")
                    else:
                        print("✗ 被重定向到登录页")
                else:
                    print("\n✗ 登录失败")
                    await browser.page.screenshot(path="C:/court-auto-filing/screenshots/login_failed.png")
                    print("失败截图已保存")
                    
                    # 提示手动输入
                    print(f"\n自动识别的验证码: {captcha_code}")
                    print("如果识别错误，请:")
                    print("1. 查看 screenshots/captcha_ocr.png")
                    print("2. 运行 manual_login.py 手动输入")
            else:
                print("OCR 识别失败")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(smart_ocr_login())
