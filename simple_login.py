import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

# ========== 在这里填写验证码 ==========
CAPTCHA_CODE = ""  # 例如: "1234"
# =====================================

async def simple_login():
    if not CAPTCHA_CODE:
        print("错误: 请先编辑脚本，填写 CAPTCHA_CODE")
        print("步骤:")
        print("1. 运行此脚本（会打开浏览器并截图）")
        print("2. 查看 screenshots\captcha_login.png")
        print("3. 编辑此脚本，填写 CAPTCHA_CODE = '你的验证码'")
        print("4. 再次运行此脚本")
        return
    
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        print("法院自动立案系统 - 登录")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
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
        print(f"找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("已填写账号密码")
        
        if len(inputs) >= 3 and CAPTCHA_CODE:
            await inputs[2].fill(CAPTCHA_CODE)
            print(f"已填写验证码: {CAPTCHA_CODE}")
            
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
            print("已点击登录")
            
            await asyncio.sleep(5)
            
            if "login" not in browser.page.url:
                print("\n登录成功!")
                await browser.save_session()
                print("会话已保存到 court_session.json")
            else:
                print("\n登录失败")
        
        # 截图查看结果
        await browser.page.screenshot(path="C:/court-auto-filing/screenshots/login_result.png")
        print("结果截图: screenshots/login_result.png")
        
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_login())
