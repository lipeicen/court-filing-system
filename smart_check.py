import asyncio
from core.browser_controller import CourtBrowser

async def smart_check():
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        # 访问保全页面
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
        
        # 等待页面加载 - 多种策略
        print("等待页面加载...")
        
        # 策略1: 等待特定元素
        for i in range(10):
            await asyncio.sleep(1)
            
            # 检查是否有表单元素
            inputs = await browser.page.query_selector_all("input, select, .uni-input, .uni-select")
            print(f"  尝试 {i+1}: 找到 {len(inputs)} 个输入元素")
            
            if len(inputs) > 0:
                print("找到表单！")
                break
                
            # 检查页面文本
            text = await browser.page.evaluate("() => document.body.innerText")
            if "保全" in text or "申请" in text:
                print(f"页面包含关键词，文本长度: {len(text)}")
        
        # 截图查看
        await browser.screenshot(name="baqx_page")
        print("已截图: baqx_page.png")
        
        # 获取所有可见文本
        text = await browser.page.evaluate("() => document.body.innerText")
        print("页面文本 (前500字符):")
        print(text[:500])
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(smart_check())
