import asyncio
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

async def find_captcha():
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 点击律师用户
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
        
        # 点击密码登录
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
        
        # 查找所有图片元素
        images = await browser.page.query_selector_all("img")
        print(f"找到 {len(images)} 个图片元素")
        
        for i, img in enumerate(images):
            try:
                src = await img.evaluate("el => el.src")
                bbox = await img.bounding_box()
                if bbox:
                    print(f"  图片 {i}: src={src[:50] if src else 'None'}...")
                    print(f"    位置: x={bbox['x']:.0f}, y={bbox['y']:.0f}, w={bbox['width']:.0f}, h={bbox['height']:.0f}")
            except:
                pass
        
        # 查找包含验证码文本的元素
        elements = await browser.page.query_selector_all("*")
        for el in elements:
            try:
                text = await el.evaluate("el => el.textContent")
                if text and "验证码" in text:
                    bbox = await el.bounding_box()
                    if bbox:
                        print(f"  验证码元素: {text.strip()}")
                        print(f"    位置: x={bbox['x']:.0f}, y={bbox['y']:.0f}")
            except:
                pass
        
        # 截图全屏
        await browser.page.screenshot(path="C:/court-auto-filing/screenshots/full_login.png")
        print("全屏截图: screenshots/full_login.png")
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_captcha())
