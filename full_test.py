import asyncio
from core.browser_controller import CourtBrowser
from config import settings

async def full_test():
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        # 1. 先登录
        print("步骤1: 登录...")
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(2)
        
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
        
        # 填写账号密码
        inputs = await browser.page.query_selector_all(".uni-input-input")
        print(f"找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 2:
            await inputs[0].fill(settings.COURT_USERNAME)
            await inputs[1].fill(settings.COURT_PASSWORD)
            print("已填写账号密码")
        
        # 保存验证码截图并等待输入
        if len(inputs) >= 3:
            # 查找验证码图片
            captcha_img = await browser.page.query_selector("img")
            if captcha_img:
                await captcha_img.screenshot(path="C:/court-auto-filing/screenshots/captcha_login.png")
                print("验证码已保存到: captcha_login.png")
                print("请查看截图并手动输入验证码...")
                
                # 这里需要手动输入，我们先跳过
                print("跳过验证码输入，测试其他功能...")
                return
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(full_test())
