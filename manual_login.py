import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

async def manual_login():
    """手动登录 - 保存截图，等待外部输入验证码"""
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - 手动登录")
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
            # 截图整个页面（包含验证码）
            captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_login.png")
            await browser.page.screenshot(path=captcha_path)
            print(f"[4/4] 页面截图已保存: {captcha_path}")
            
            # 尝试打开图片（Windows）
            try:
                os.startfile(captcha_path)
                print("已打开截图")
            except Exception as e:
                print(f"无法自动打开图片: {e}")
            
            # 检查是否有验证码文件
            captcha_file = os.path.join(settings.SCREENSHOT_DIR, "captcha_code.txt")
            
            print(f"\n请查看截图，然后将验证码写入文件: {captcha_file}")
            print("等待验证码文件...")
            
            # 等待用户创建验证码文件（最多等待120秒）
            for i in range(24):
                if os.path.exists(captcha_file):
                    with open(captcha_file, 'r', encoding='utf-8') as f:
                        captcha_code = f.read().strip()
                    
                    if captcha_code:
                        print(f"读取到验证码: {captcha_code}")
                        
                        # 删除文件
                        os.remove(captcha_file)
                        
                        # 填写验证码
                        await inputs[2].fill(captcha_code)
                        
                        # 点击登录按钮
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
                            
                            # 测试访问立案页面
                            print("\n测试访问保全页面...")
                            await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
                            await asyncio.sleep(3)
                            
                            if "login" not in browser.page.url:
                                print("可以正常访问保全页面")
                            else:
                                print("被重定向到登录页，会话可能无效")
                        else:
                            print("\n登录失败，请检查验证码")
                        
                        break
                    else:
                        print("验证码文件为空")
                        os.remove(captcha_file)
                
                await asyncio.sleep(5)
                print(f"等待中... ({i+1}/24)")
            else:
                print("\n等待超时，未收到验证码")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(manual_login())
