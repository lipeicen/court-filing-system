import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class SimpleBaoquan:
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
        
        # 使用JavaScript移除所有弹窗和遮罩
        await self.browser.page.evaluate("""
            () => {
                // 移除所有可能的弹窗和遮罩
                const selectors = [
                    '.el-dialog', '.el-overlay', '.modal', '.popup', '.dialog',
                    '[class*="dialog"]', '[class*="Dialog"]', '[class*="overlay"]',
                    '[class*="mask"]', '[class*="modal"]', '[class*="Modal"]'
                ];
                
                selectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el && el.style) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                        }
                    });
                });
                
                // 移除body上的overflow:hidden（防止滚动锁定）
                document.body.style.overflow = 'auto';
                
                return 'done';
            }
        """)
        
        await asyncio.sleep(1)
        print("✓ 弹窗已关闭")
    
    async def click_baoquan(self):
        print("\n[4] 点击'在线保全'...")
        
        # 使用JavaScript查找并点击
        clicked = await self.browser.page.evaluate("""
            () => {
                // 方法1: 通过文本查找
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        // 向上查找5层父元素，找到可点击的元素
                        let target = el;
                        for (let i = 0; i < 5; i++) {
                            if (!target) break;
                            
                            const style = window.getComputedStyle(target);
                            if (style.cursor === 'pointer' || target.onclick || target.tagName === 'A' || target.tagName === 'BUTTON') {
                                target.click();
                                return 'clicked parent level ' + i;
                            }
                            
                            target = target.parentElement;
                        }
                        
                        // 如果没找到，点击元素自身
                        el.click();
                        return 'clicked self';
                    }
                }
                
                return 'not found';
            }
        """)
        
        print(f"点击结果: {clicked}")
        await asyncio.sleep(5)
        
        # 检查URL
        current_url = self.browser.page.url
        print(f"当前URL: {current_url}")
        
        if "pick-case-type" not in current_url:
            print("✓ 页面已跳转！")
            return True
        else:
            print("! 页面未跳转")
            return False

async def main():
    filing = SimpleBaoquan()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
