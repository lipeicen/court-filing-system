import asyncio
from core.browser_controller import CourtBrowser

async def get_html():
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        # 访问保全页面
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
        await asyncio.sleep(3)
        
        # 获取页面内容
        html = await browser.page.content()
        
        # 保存到文件
        with open("C:/court-auto-filing/page_html.txt", "w", encoding="utf-8") as f:
            # 只保存前5000字符
            f.write(html[:5000])
        
        print(f"HTML saved, length: {len(html)}")
        
        # 查找表单元素
        inputs = await browser.page.query_selector_all("input, select, textarea")
        print(f"Found {len(inputs)} form elements")
        
        for i, inp in enumerate(inputs[:10]):
            tag = await inp.evaluate("el => el.tagName")
            type_attr = await inp.evaluate("el => el.type || ''")
            placeholder = await inp.evaluate("el => el.placeholder || ''")
            print(f"  {i}: {tag} type={type_attr} placeholder={placeholder}")
        
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_html())
