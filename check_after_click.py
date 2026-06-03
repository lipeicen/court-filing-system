import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class CheckAfterClick:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("检查点击后的状态")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            if not await self.navigate_to_filing():
                return False
            
            await self.close_popup()
            
            # 点击"在线保全"
            print("\n[4] 点击'在线保全'...")
            await self.browser.page.click("text=在线保全", timeout=5000)
            print("✓ 点击成功")
            
            # 等待更长时间
            print("\n等待10秒...")
            await asyncio.sleep(10)
            
            # 检查URL
            print(f"\n当前URL: {self.browser.page.url}")
            
            # 检查页面标题
            title = await self.browser.page.title()
            print(f"页面标题: {title}")
            
            # 获取页面完整内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"\n页面内容长度: {len(page_text)}")
            print("\n页面内容:")
            print(page_text[:1500])
            
            # 检查是否有加载指示器
            loading = await self.browser.page.evaluate("""
                () => {
                    const loaders = document.querySelectorAll('.loading, .el-loading, [class*="loading"], [class*="Loading"]');
                    return loaders.length;
                }
            """)
            print(f"\n加载指示器数量: {loading}")
            
            # 检查是否有错误信息
            errors = await self.browser.page.evaluate("""
                () => {
                    const errorElements = document.querySelectorAll('.error, [class*="error"], [class*="Error"]');
                    return Array.from(errorElements).map(el => el.textContent).filter(text => text.length > 0);
                }
            """)
            print(f"\n错误信息: {errors}")
            
            # 截图
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "after_click_check.png"))
            print("\n✓ 已保存截图")
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def check_session(self):
        print("[1] 检查会话...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        if "login" in self.browser.page.url:
            print("✗ 会话过期")
            return False
        
        print("✓ 会话有效")
        return True
    
    async def navigate_to_filing(self):
        print("\n[2] 导航到在线立案...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
        await asyncio.sleep(3)
        
        if "login" in self.browser.page.url:
            print("✗ 需要登录")
            return False
        
        print("✓ 已加载案件类型选择页面")
        return True
    
    async def close_popup(self):
        print("\n[3] 关闭弹窗...")
        
        await self.browser.page.evaluate("""
            () => {
                document.querySelectorAll('.el-dialog, .el-overlay, .modal, .popup').forEach(el => {
                    if (el && el.style) el.style.display = 'none';
                });
                document.body.style.overflow = 'auto';
                return 'done';
            }
        """)
        
        await asyncio.sleep(1)
        print("✓ 弹窗已关闭")

async def main():
    check = CheckAfterClick()
    await check.run()

if __name__ == "__main__":
    asyncio.run(main())
