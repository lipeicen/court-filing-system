import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # 访问登录页
        await page.goto("https://zxfw.court.gov.cn/zxfw/")
        print("请手动登录...")
        await asyncio.sleep(60)  # 给你60秒时间登录
        
        # 登录后，开始录制操作
        print("请手动操作：点击在线立案 -> 在线保全 -> 勾选须知 -> 点击创建保全申请")
        print("操作完成后按 Enter 继续...")
        input()
        
        # 获取当前页面的HTML结构（底部区域）
        bottom_html = await page.evaluate("""
            () => {
                const allElements = document.querySelectorAll('*');
                const bottomElements = [];
                for (const el of allElements) {
                    const rect = el.getBoundingClientRect();
                    const text = el.textContent || '';
                    // 找底部区域的元素
                    if (rect.top > window.innerHeight * 0.8 && text.length > 0) {
                        bottomElements.push({
                            tag: el.tagName.toLowerCase(),
                            text: text.trim().substring(0, 100),
                            className: el.className,
                            id: el.id,
                            rect: {
                                top: rect.top,
                                left: rect.left,
                                width: rect.width,
                                height: rect.height
                            }
                        });
                    }
                }
                return bottomElements;
            }
        """)
        
        print(f"\n找到 {len(bottom_html)} 个底部元素:")
        for i, el in enumerate(bottom_html):
            print(f"  [{i}] {el['tag']} | text='{el['text']}' | class='{el['className']}' | id='{el['id']}'")
            print(f"       位置: top={el['rect']['top']}, left={el['rect']['left']}, size={el['rect']['width']}x{el['rect']['height']}")
        
        # 截图
        await page.screenshot(path="record_bottom.png", full_page=True)
        print("\n已截图 record_bottom.png")
        
        await asyncio.sleep(30)
        await browser.close()

asyncio.run(main())