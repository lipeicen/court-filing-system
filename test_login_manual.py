import asyncio
import os
from PIL import Image
from core.browser_controller import CourtBrowser
from config import settings

async def test_login():
    browser = CourtBrowser()
    try:
        await browser.start()
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
        lawyer_tab = await browser.page.query_selector('text=律师用户')
        if lawyer_tab:
            await lawyer_tab.click()
            await asyncio.sleep(1)
        
        # 获取所有输入框
        inputs = await browser.page.query_selector_all('input')
        print(f"找到 {len(inputs)} 个输入框")
        
        # 填写账号密码
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("已填写账号密码")
        
        # 查找验证码图片
        captcha_img = await browser.page.query_selector('img[src*="captcha"]')
        if not captcha_img:
            captcha_img = await browser.page.query_selector('.captcha-image')
        
        if captcha_img:
            captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha.png")
            await captcha_img.screenshot(path=captcha_path)
            print(f"验证码已保存: {captcha_path}")
            
            try:
                img = Image.open(captcha_path)
                img.show()
            except Exception as e:
                print(f"无法显示图片: {e}")
            
            captcha_code = input("请输入验证码: ")
            
            if len(inputs) >= 3:
                await inputs[2].fill(captcha_code)
            
            login_btn = await browser.page.query_selector('button:has-text("登录")')
            if login_btn:
                await login_btn.click()
                await asyncio.sleep(5)
                
                if "login" not in browser.page.url:
                    print("登录成功!")
                    await browser.save_session()
                else:
                    print("登录失败")
        
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
