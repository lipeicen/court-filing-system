import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class DirectBaoquan:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统 - 直接访问保全")
            print("=" * 60)
            
            # 1. 检查会话
            if not await self.check_session():
                return False
            
            # 2. 尝试直接访问保全申请URL
            if not await self.direct_access_baoquan():
                return False
            
            print("\n✓ 完成")
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def check_session(self):
        print("\n[1] 检查会话...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        if "login" in self.browser.page.url:
            print("✗ 会话过期")
            return False
        
        print("✓ 会话有效")
        return True
    
    async def direct_access_baoquan(self):
        print("\n[2] 直接访问保全申请页面...")
        
        # 尝试多个可能的URL
        urls = [
            "https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index",
            "https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/baoquan/index",
            "https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/apply/index",
            "https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/apply",
        ]
        
        for url in urls:
            print(f"\n尝试: {url}")
            await self.browser.goto(url)
            await asyncio.sleep(3)
            
            # 截图
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, f"url_test_{urls.index(url)}.png"))
            
            # 检查是否被重定向
            if "login" in self.browser.page.url:
                print("✗ 需要登录")
                continue
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            
            if "保全" in page_text and "申请" in page_text:
                print("✓ 找到保全申请页面！")
                print(f"\n页面内容: {page_text[:500]}")
                return True
            else:
                print(f"页面内容: {page_text[:200]}")
        
        print("\n所有URL都未找到保全申请页面")
        return False

async def main():
    filing = DirectBaoquan()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
