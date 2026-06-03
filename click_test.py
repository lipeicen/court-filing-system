import asyncio
from core.browser_controller import CourtBrowser

async def click_test():
    browser = CourtBrowser()
    try:
        await browser.launch()
        
        # 访问保全页面
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
        await asyncio.sleep(3)
        
        # 截图初始状态
        await browser.screenshot(name="baqx_initial")
        print("初始截图已保存")
        
        # 查找并点击"创建保全申请"按钮
        print("查找创建保全申请按钮...")
        
        # 方法1: 通过文本查找
        btn = await browser.page.query_selector("text=创建保全申请")
        if btn:
            print("找到按钮(方法1)")
            await btn.click()
        else:
            # 方法2: JavaScript查找
            result = await browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.includes('创建保全申请')) {
                            el.click();
                            return { found: true, text: el.textContent };
                        }
                    }
                    return { found: false };
                }
            """)
            print(f"方法2结果: {result}")
        
        await asyncio.sleep(3)
        
        # 截图点击后
        await browser.screenshot(name="baqx_after_click")
        print("点击后截图已保存")
        
        # 检查表单元素
        inputs = await browser.page.query_selector_all("input, select, textarea, .uni-input")
        print(f"点击后找到 {len(inputs)} 个表单元素")
        
        # 获取页面文本
        text = await browser.page.evaluate("() => document.body.innerText")
        print("页面文本 (前800字符):")
        print(text[:800])
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_test())
