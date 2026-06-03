import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from PIL import Image

async def retry_login(max_attempts=5):
    """多次尝试 OCR 登录"""
    browser = CourtBrowser()
    
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - 多次重试登录")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 1. 点击律师用户
        print("[1/5] 点击律师用户标签...")
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
        print("[2/5] 点击密码登录...")
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
        print(f"[3/5] 找到 {len(inputs)} 个输入框")
        
        # 4. 填写账号密码
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("[4/5] 已填写账号密码")
        
        # 5. 多次尝试验证码
        if len(inputs) >= 3:
            import ddddocr
            ocr = ddddocr.DdddOcr()
            
            for attempt in range(1, max_attempts + 1):
                print(f"\n[5/5] 第 {attempt}/{max_attempts} 次尝试...")
                
                # 刷新验证码（点击验证码图片）
                if attempt > 1:
                    print("刷新验证码...")
                    await browser.page.evaluate("""
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
                
                # 截图
                full_path = os.path.join(settings.SCREENSHOT_DIR, f"captcha_full_{attempt}.png")
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
                captcha_path = os.path.join(settings.SCREENSHOT_DIR, f"captcha_{attempt}.png")
                captcha_img.save(captcha_path)
                
                # OCR 识别
                with open(captcha_path, 'rb') as f:
                    image_bytes = f.read()
                
                captcha_code = ocr.classification(image_bytes)
                print(f"OCR 识别: {captcha_code}")
                
                if captcha_code and len(captcha_code) >= 3:
                    # 清理
                    import re
                    captcha_code = re.sub(r'[^a-zA-Z0-9]', '', captcha_code)
                    
                    # 清空并填写验证码
                    await inputs[2].fill("")
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
                    
                    await asyncio.sleep(5)
                    
                    # 检查登录结果
                    if "login" not in browser.page.url:
                        print(f"\n✓ 第 {attempt} 次尝试成功!")
                        await browser.save_session()
                        print("✓ 会话已保存")
                        
                        # 测试保全页面
                        print("\n测试访问保全页面...")
                        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
                        await asyncio.sleep(3)
                        
                        if "login" not in browser.page.url:
                            print("✓ 可以正常访问保全页面")
                        else:
                            print("✗ 被重定向到登录页")
                        
                        return True
                    else:
                        print(f"✗ 第 {attempt} 次失败")
                        
                        # 检查是否有错误提示
                        error_text = await browser.page.evaluate("""
                            () => {
                                const elements = document.querySelectorAll('*');
                                for (const el of elements) {
                                    if (el.textContent && (
                                        el.textContent.includes('错误') ||
                                        el.textContent.includes('失败') ||
                                        el.textContent.includes('验证码')
                                    )) {
                                        return el.textContent.trim();
                                    }
                                }
                                return '';
                            }
                        """)
                        if error_text:
                            print(f"  错误提示: {error_text}")
            
            print(f"\n✗ {max_attempts} 次尝试均失败")
            print("建议:")
            print("1. 检查账号密码是否正确")
            print("2. 使用 manual_login.py 手动输入验证码")
            print("3. 购买 2Captcha 服务")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        return False
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(retry_login())
