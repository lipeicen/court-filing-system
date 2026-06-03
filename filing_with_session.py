import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class FixedFiling:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统")
            print("=" * 60)
            
            # 1. 检查会话
            if not await self.check_session():
                return False
            
            # 2. 点击"在线立案"
            if not await self.click_online_filing():
                return False
            
            # 3. 点击"在线保全"
            if not await self.click_online_baoquan():
                return False
            
            print("\n✓ 流程完成")
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
    
    async def click_online_filing(self):
        print("\n[2] 点击'在线立案'...")
        
        # 使用 Playwright 的点击方法
        clicked = await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线立案') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        if clicked:
            print("✓ 已点击'在线立案'")
            await asyncio.sleep(3)
            return True
        return False
    
    async def click_online_baoquan(self):
        print("\n[3] 点击'在线保全'...")
        
        # 方法1: 通过文本查找
        clicked = await self.browser.page.evaluate("""
            () => {
                // 查找包含"在线保全"的元素
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        // 确保元素可见且可点击
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            // 尝试点击父元素（可能是卡片）
                            const parent = el.closest('[class*="card"], [class*="item"], div');
                            if (parent) {
                                parent.click();
                                return 'parent';
                            }
                            el.click();
                            return 'self';
                        }
                    }
                }
                return false;
            }
        """)
        
        print(f"点击结果: {clicked}")
        
        if clicked:
            print("✓ 已点击'在线保全'")
            await asyncio.sleep(5)  # 等待页面加载
            
            # 截图
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_form.png"))
            print("✓ 已保存保全申请页面")
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print("\n保全页面内容:")
            print(page_text[:1000])
            
            # 检查URL是否变化
            print(f"\n当前URL: {self.browser.page.url}")
            
            return True
        else:
            print("✗ 未找到'在线保全'按钮")
            return False

async def main():
    filing = FixedFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
