import asyncio
import os
from utils.ocr_captcha import ocr_solver
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

"""自动登录 - 使用 OCR"""
async def main():
    
    browser = CourtBrowser()
    
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - 自动登录 (OCR)")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
        print("[1/5] 选择律师用户...")
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
        print(f"[2/5] 找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("[3/5] 已填写账号密码")
        
        # 处理验证码
        if len(inputs) >= 3:
            captcha_img = await browser.page.query_selector("img")
            if captcha_img:
                captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_auto.png")
                await captcha_img.screenshot(path=captcha_path)
                print(f"[4/5] 验证码已保存: {captcha_path}")
                
                # 使用本地 OCR 识别
                captcha_code = ocr_solver.recognize(captcha_path)
                
                if captcha_code:
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
                    print("[5/5] 已点击登录按钮")
                    
                    await asyncio.sleep(5)
                    
                    # 检查登录结果
                    if "login" not in browser.page.url:
                        print("\n✓ 登录成功!")
                        await browser.save_session()
                        print("✓ 会话已保存")
                    else:
                        print("\n✗ 登录失败，验证码可能识别错误")
                else:
                    print("\n✗ 验证码识别失败")
            else:
                print("未找到验证码图片")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(auto_login())
