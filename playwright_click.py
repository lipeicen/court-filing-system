import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class PlaywrightClick:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            if not await self.navigate_to_filing():
                return False
            
            # 关闭弹窗
            await self.close_popup()
            
            # 点击"在线保全"
            if not await self.click_baoquan():
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
        
        # 使用JavaScript移除弹窗
        await self.browser.page.evaluate("""
            () => {
                const selectors = [
                    '.el-dialog', '.el-overlay', '.modal', '.popup',
                    '[class*="dialog"]', '[class*="Dialog"]', '[class*="overlay"]',
                    '[class*="mask"]', '[class*="modal"]'
                ];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el && el.style) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                        }
                    });
                });
                
                document.body.style.overflow = 'auto';
                return 'done';
            }
        """)
        
        await asyncio.sleep(1)
        print("✓ 弹窗已关闭")
    
    async def click_baoquan(self):
        print("\n[4] 点击'在线保全'...")
        
        try:
            # 方式1: 使用 Playwright 的 page.click() 和 text 选择器
            print("方式1: Playwright text选择器...")
            await self.browser.page.click("text=在线保全", timeout=5000)
            print("✓ 点击成功（方式1）")
            await asyncio.sleep(5)
            
            if "pick-case-type" not in self.browser.page.url:
                print("✓ 页面已跳转！")
                return True
        except Exception as e:
            print(f"方式1失败: {e}")
        
        try:
            # 方式2: 使用 role 选择器
            print("方式2: role选择器...")
            await self.browser.page.get_by_role("button", name="在线保全").click(timeout=5000)
            print("✓ 点击成功（方式2）")
            await asyncio.sleep(5)
            
            if "pick-case-type" not in self.browser.page.url:
                print("✓ 页面已跳转！")
                return True
        except Exception as e:
            print(f"方式2失败: {e}")
        
        try:
            # 方式3: 使用 locator
            print("方式3: locator...")
            await self.browser.page.locator("text=在线保全").click(timeout=5000)
            print("✓ 点击成功（方式3）")
            await asyncio.sleep(5)
            
            if "pick-case-type" not in self.browser.page.url:
                print("✓ 页面已跳转！")
                return True
        except Exception as e:
            print(f"方式3失败: {e}")
        
        print("✗ 所有方式都失败")
        return False

async def main():
    filing = PlaywrightClick()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
