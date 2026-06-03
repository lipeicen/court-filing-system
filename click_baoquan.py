import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class ClickBaoquan:
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
            if not await self.close_popup():
                print("! 弹窗关闭可能失败，继续尝试")
            
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
        print("\n[3] 关闭综治中心弹窗...")
        
        # 截图查看
        await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "popup_before.png"))
        
        # 方式1: 点击弹窗内的"关闭"按钮
        # 根据分析，关闭按钮在弹窗底部，坐标大约在 (1050, 750)
        print("方式1: 点击关闭按钮坐标...")
        await self.browser.page.mouse.click(1050, 750)
        await asyncio.sleep(2)
        
        # 方式2: 点击右上角X
        print("方式2: 点击右上角X...")
        await self.browser.page.mouse.click(1250, 320)
        await asyncio.sleep(2)
        
        # 方式3: 使用JavaScript查找关闭按钮
        print("方式3: JavaScript关闭...")
        result = await self.browser.page.evaluate("""
            () => {
                // 查找关闭按钮
                const closeBtns = document.querySelectorAll('button, .close, [class*="close"], [class*="Close"]');
                for (const btn of closeBtns) {
                    if (btn.textContent && (btn.textContent.includes('关闭') || btn.textContent.includes('×') || btn.textContent.includes('X'))) {
                        btn.click();
                        return 'found close button';
                    }
                }
                
                // 查找弹窗并移除
                const dialogs = document.querySelectorAll('.el-dialog, .modal, [class*="dialog"], [class*="Dialog"]');
                for (const dialog of dialogs) {
                    dialog.style.display = 'none';
                    if (dialog.parentElement) dialog.parentElement.style.display = 'none';
                }
                
                // 查找遮罩层并移除
                const overlays = document.querySelectorAll('.el-overlay, .overlay, [class*="overlay"], [class*="mask"]');
                for (const overlay of overlays) {
                    overlay.style.display = 'none';
                }
                
                return 'removed overlays';
            }
        """)
        print(f"结果: {result}")
        await asyncio.sleep(2)
        
        # 截图确认
        await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "popup_after.png"))
        print("✓ 已保存关闭后截图")
        
        return True
    
    async def click_baoquan(self):
        print("\n[4] 点击'在线保全'...")
        
        # 先截图查看当前状态
        await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "before_click.png"))
        
        # 使用JavaScript点击
        clicked = await self.browser.page.evaluate("""
            () => {
                // 查找所有元素
                const allElements = document.querySelectorAll('*');
                
                for (const el of allElements) {
                    // 查找文本完全匹配"在线保全"的元素
                    if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) {
                        if (el.textContent.trim() === '在线保全') {
                            console.log('Found element:', el.tagName, el.className);
                            
                            // 向上查找可点击的父元素
                            let target = el.parentElement;
                            while (target && target.tagName !== 'BODY') {
                                console.log('Checking parent:', target.tagName, target.className);
                                
                                // 检查是否有点击事件或cursor样式
                                const style = window.getComputedStyle(target);
                                if (style.cursor === 'pointer' || target.onclick || target.tagName === 'A' || target.tagName === 'BUTTON') {
                                    console.log('Clicking parent:', target.tagName);
                                    target.click();
                                    return 'clicked parent: ' + target.tagName;
                                }
                                
                                target = target.parentElement;
                            }
                            
                            // 如果没找到，点击自身
                            el.click();
                            return 'clicked self';
                        }
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
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_success.png"))
            return True
        else:
            print("! 页面未跳转")
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "click_failed.png"))
            return False

async def main():
    filing = ClickBaoquan()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
