import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from PIL import Image

class FixedFiling:
    """修复版 - 正确处理验证码"""
    
    def __init__(self):
        self.browser = CourtBrowser()
        self.max_retries = 10
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统")
            print("=" * 60)
            
            if not await self.login():
                return False
            
            print("\n✓ 登录成功！")
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            return False
        finally:
            await self.browser.close()
    
    async def login(self):
        print("\n访问登录页面...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 点击律师用户
        print("点击律师用户...")
        await self.browser.page.evaluate("""
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
        
        # 点击密码登录
        print("点击密码登录...")
        await self.browser.page.evaluate("""
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
        
        # 获取输入框
        inputs = await self.browser.page.query_selector_all(".uni-input-input")
        if len(inputs) < 3:
            print("未找到足够的输入框")
            return False
        
        # 填写账号密码
        await inputs[0].fill(settings.COURT_USERNAME)
        await inputs[1].fill(settings.COURT_PASSWORD)
        print("已填写账号密码")
        
        # 尝试验证码
        for attempt in range(1, self.max_retries + 1):
            print(f"\n第 {attempt} 次尝试...")
            
            # 等待验证码加载完成（没有刷新图标）
            print("等待验证码加载...")
            await asyncio.sleep(2)
            
            # 检查是否有刷新/加载图标
            has_loading = await self.browser.page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    for (const img of images) {
                        if (img.src && img.src.includes('data:image')) {
                            // 检查是否有覆盖的刷新图标
                            const rect = img.getBoundingClientRect();
                            const centerX = rect.left + rect.width / 2;
                            const centerY = rect.top + rect.height / 2;
                            const elementAtCenter = document.elementFromPoint(centerX, centerY);
                            if (elementAtCenter && elementAtCenter !== img) {
                                return true;  // 有覆盖元素
                            }
                        }
                    }
                    return false;
                }
            """)
            
            if has_loading:
                print("验证码还在加载中，等待...")
                await asyncio.sleep(3)
            
            # 识别验证码
            captcha_code = await self.recognize_captcha()
            if not captcha_code:
                print("验证码识别失败")
                if attempt < self.max_retries:
                    print("刷新验证码...")
                    await self.refresh_captcha()
                continue
            
            print(f"验证码: {captcha_code}")
            
            # 填写验证码
            await inputs[2].fill("")
            await inputs[2].fill(captcha_code)
            await asyncio.sleep(1)
            
            # 点击登录
            print("点击登录...")
            await self.browser.page.evaluate("""
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
            
            await asyncio.sleep(5)
            
            # 检查登录结果
            if "login" not in self.browser.page.url:
                print("✓ 登录成功！")
                await self.browser.save_session()
                return True
            
            print("登录失败")
            
            # 分析错误
            error_text = await self.get_error_text()
            if error_text:
                print(f"错误: {error_text}")
                if "验证码" not in error_text:
                    print("非验证码错误，停止重试")
                    return False
            
            # 刷新验证码继续尝试
            if attempt < self.max_retries:
                print("刷新验证码重试...")
                await self.refresh_captcha()
        
        print(f"\n{self.max_retries} 次尝试均失败")
        return False
    
    async def recognize_captcha(self):
        """识别验证码"""
        try:
            import ddddocr
            ocr = ddddocr.DdddOcr()
            
            # 截图全屏
            full_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_full.png")
            await self.browser.page.screenshot(path=full_path)
            
            # 裁剪验证码区域（根据实际位置调整）
            img = Image.open(full_path)
            
            # 验证码在右侧登录框内，大约在 x=1400-1600, y=450-550
            # 根据之前的分析，验证码图片位置大约在 (1471, 467, 100, 51)
            # 但刷新按钮会遮挡，我们需要等待加载完成后截图
            
            # 使用固定的裁剪区域
            left, top, right, bottom = 1460, 460, 1580, 530
            
            captcha_img = img.crop((left, top, right, bottom))
            captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha.png")
            captcha_img.save(captcha_path)
            
            # OCR识别
            with open(captcha_path, 'rb') as f:
                image_bytes = f.read()
            
            result = ocr.classification(image_bytes)
            
            # 清理
            import re
            result = re.sub(r'[^a-zA-Z0-9]', '', result)
            
            return result if len(result) >= 3 else None
            
        except Exception as e:
            print(f"OCR错误: {e}")
            return None
    
    async def refresh_captcha(self):
        """刷新验证码"""
        await self.browser.page.evaluate("""
            () => {
                const images = document.querySelectorAll('img');
                for (const img of images) {
                    if (img.src && img.src.includes('data:image')) {
                        img.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(2)
    
    async def get_error_text(self):
        """获取错误提示"""
        return await self.browser.page.evaluate("""
            () => {
                const selectors = ['.fd-error-tip', '.uni-toast', '[class*="error"]'];
                for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el && el.textContent.trim()) {
                        return el.textContent.trim();
                    }
                }
                return '';
            }
        """)

async def main():
    filing = FixedFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
