import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from PIL import Image

async def ocr_login():
    """使用 OCR 自动识别验证码登录（支持重试）"""
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - OCR 自动登录")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 1. 先点击"律师用户"标签
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
        
        # 2. 点击"密码登录"
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
        
        # 5. 截图并裁剪验证码区域
        if len(inputs) >= 3:
            # 截图全屏
            full_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_full.png")
            await browser.page.screenshot(path=full_path)
            
            # 裁剪验证码区域（根据实际位置调整）
            img = Image.open(full_path)
            width, height = img.size
            
            # 验证码位置: x=1471, y=467, w=100, h=51 (在1920x1080分辨率下)
            # 根据实际分辨率调整
            scale_x = width / 1920
            scale_y = height / 1080
            
            left = int((1471 - 5) * scale_x)
            top = int((467 - 5) * scale_y)
            right = int((1471 + 100 + 5) * scale_x)
            bottom = int((467 + 51 + 5) * scale_y)
            
            captcha_img = img.crop((left, top, right, bottom))
            captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_ocr.png")
            captcha_img.save(captcha_path)
            print(f"[5/6] 验证码截图已保存: {captcha_path}")
            
            # 6. 使用 OCR 识别
            try:
                import ddddocr
                
                print("[6/6] 使用 OCR 识别验证码...")
                ocr = ddddocr.DdddOcr()
                
                with open(captcha_path, 'rb') as f:
                    image_bytes = f.read()
                
                captcha_code = ocr.classification(image_bytes)
                print(f"OCR 识别结果: {captcha_code}")
                
                # 如果识别结果太短，尝试其他方法
                if not captcha_code or len(captcha_code) < 3:
                    print("OCR 识别结果太短，尝试放大后重新识别...")
                    # 放大图片
                    enlarged = captcha_img.resize((captcha_img.width * 2, captcha_img.height * 2), Image.Resampling.LANCZOS)
                    enlarged_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_enlarged.png")
                    enlarged.save(enlarged_path)
                    
                    with open(enlarged_path, 'rb') as f:
                        image_bytes = f.read()
                    
                    captcha_code = ocr.classification(image_bytes)
                    print(f"放大后 OCR 识别结果: {captcha_code}")
                
                if captcha_code and len(captcha_code) >= 3:
                    # 清理识别结果（只保留字母和数字）
                    import re
                    captcha_code = re.sub(r'[^a-zA-Z0-9]', '', captcha_code)
                    print(f"清理后的验证码: {captcha_code}")
                    
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
                        print("\n登录成功!")
                        await browser.save_session()
                        print("会话已保存")
                        
                        # 测试访问保全页面
                        print("\n测试访问保全页面...")
                        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
                        await asyncio.sleep(3)
                        
                        if "login" not in browser.page.url:
                            print("✓ 可以正常访问保全页面")
                        else:
                            print("✗ 被重定向到登录页")
                    else:
                        print("\n登录失败，OCR 识别可能错误")
                        # 保存失败截图
                        await browser.page.screenshot(path="C:/court-auto-filing/screenshots/login_failed.png")
                        print("失败截图: screenshots/login_failed.png")
                        
                        # 显示验证码供手动输入
                        print(f"\n识别的验证码是: {captcha_code}")
                        print("请检查 screenshots/captcha_ocr.png")
                else:
                    print("OCR 识别失败，未获取到有效验证码")
                    
            except ImportError:
                print("错误: 未安装 ddddocr")
                print("请运行: pip install ddddocr")
            except Exception as e:
                print(f"OCR 识别错误: {e}")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(ocr_login())
