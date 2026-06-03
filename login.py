import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from utils.ocr_captcha import ocr_solver

async def login_with_ocr():
    """使用 OCR 自动识别验证码登录"""
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - OCR 自动登录")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
        print("[1/4] 选择律师用户...")
        await browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.includes('律师用户')) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(1)
        
        # 获取输入框
        inputs = await browser.page.query_selector_all(".uni-input-input")
        print(f"[2/4] 找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("[3/4] 已填写账号密码")
        
        # 处理验证码
        if len(inputs) >= 3:
            # 尝试找到验证码图片
            print("[4/4] 查找验证码图片...")
            
            # 方法1: 查找所有图片
            images = await browser.page.query_selector_all("img")
            print(f"找到 {len(images)} 个图片")
            
            captcha_code = None
            
            for i, img in enumerate(images):
                try:
                    # 截图每个图片
                    img_path = os.path.join(settings.SCREENSHOT_DIR, f"captcha_img_{i}.png")
                    await img.screenshot(path=img_path)
                    
                    # OCR 识别
                    code = ocr_solver.recognize(img_path)
                    print(f"  图片 {i}: {code}")
                    
                    # 如果识别结果是4位数字或字母，可能是验证码
                    if code and len(code) == 4 and code.isalnum():
                        captcha_code = code
                        print(f"  找到验证码: {captcha_code}")
                        break
                except Exception as e:
                    print(f"  图片 {i} 截图失败: {e}")
            
            # 如果没有找到，尝试整个页面截图
            if not captcha_code:
                print("尝试识别整个页面...")
                page_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_page.png")
                await browser.page.screenshot(path=page_path)
                captcha_code = ocr_solver.recognize(page_path)
                print(f"页面识别结果: {captcha_code}")
            
            if captcha_code and len(captcha_code) >= 3:
                print(f"使用验证码: {captcha_code}")
                
                # 填写验证码
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
                current_url = browser.page.url
                if "login" not in current_url:
                    print("登录成功!")
                    await browser.save_session()
                    print("会话已保存")
                    return True
                else:
                    print("OCR 识别可能错误，登录失败")
                    return False
            else:
                print("未能识别有效验证码")
                return False
        
        return False
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_with_ocr())
