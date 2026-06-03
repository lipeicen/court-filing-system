import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class CheckSource:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("检查页面源代码")
            print("=" * 60)
            
            # 导航到保全页面
            print("\n[1] 导航到保全页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
            await asyncio.sleep(5)
            
            print(f"当前URL: {self.browser.page.url}")
            
            # 获取页面源代码
            print("\n[2] 获取页面源代码...")
            
            # 获取HTML
            html = await self.browser.page.content()
            print(f"\nHTML长度: {len(html)}")
            print("\nHTML前1000字符:")
            print(html[:1000])
            
            # 检查是否有script标签包含保全相关代码
            print("\n[3] 查找相关脚本...")
            
            scripts = await self.browser.page.query_selector_all('script')
            print(f"\n脚本数量: {len(scripts)}")
            
            for i, script in enumerate(scripts[:5]):
                try:
                    src = await script.get_attribute('src')
                    if src:
                        print(f"  Script {i}: {src}")
                except:
                    pass
            
            # 检查localStorage/sessionStorage
            print("\n[4] 检查存储...")
            
            storage = await self.browser.page.evaluate("""
                () => {
                    return {
                        localStorage: Object.keys(localStorage),
                        sessionStorage: Object.keys(sessionStorage)
                    };
                }
            """)
            print(f"LocalStorage keys: {storage['localStorage']}")
            print(f"SessionStorage keys: {storage['sessionStorage']}")
            
            # 检查是否有错误信息
            print("\n[5] 检查控制台错误...")
            
            # 获取页面文本
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"\n页面文本长度: {len(page_text)}")
            
            # 查找是否有错误提示
            if "错误" in page_text or "失败" in page_text or "无权" in page_text:
                print("! 页面可能包含错误信息")
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()

async def main():
    check = CheckSource()
    success = await check.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
