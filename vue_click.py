import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class VueClick:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统 - Vue事件触发")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            if not await self.navigate_to_filing():
                return False
            
            await self.close_popup()
            
            # 使用多种方式触发点击
            if not await self.click_baoquan_vue():
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
        
        await self.browser.page.evaluate("""
            () => {
                document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                    if (el && el.style) el.style.display = 'none';
                });
                document.body.style.overflow = 'auto';
                return 'done';
            }
        """)
        
        await asyncio.sleep(1)
        print("✓ 弹窗已关闭")
    
    async def click_baoquan_vue(self):
        print("\n[4] 触发Vue点击事件...")
        
        # 使用JavaScript触发Vue组件的点击
        result = await self.browser.page.evaluate("""
            () => {
                // 查找包含"在线保全"的元素
                const elements = document.querySelectorAll('*');
                let targetElement = null;
                
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        targetElement = el;
                        break;
                    }
                }
                
                if (!targetElement) {
                    return 'element not found';
                }
                
                console.log('Found element:', targetElement.tagName, targetElement.className);
                
                // 方法1: 触发Vue的$emit事件
                let vueInstance = targetElement.__vue__ || targetElement.__VUE__;
                if (!vueInstance) {
                    // 向上查找Vue实例
                    let parent = targetElement.parentElement;
                    while (parent && !vueInstance) {
                        vueInstance = parent.__vue__ || parent.__VUE__;
                        parent = parent.parentElement;
                    }
                }
                
                if (vueInstance) {
                    console.log('Found Vue instance');
                    
                    // 触发点击事件
                    if (vueInstance.$emit) {
                        vueInstance.$emit('click');
                        return 'emitted click event';
                    }
                    
                    // 触发原生点击
                    if (vueInstance.$el) {
                        vueInstance.$el.click();
                        return 'clicked vue $el';
                    }
                }
                
                // 方法2: 查找router-link或类似元素
                let routerLink = targetElement.closest('a, [class*="router-link"], [class*="nav"]');
                if (routerLink) {
                    console.log('Found router link:', routerLink.tagName);
                    routerLink.click();
                    return 'clicked router link';
                }
                
                // 方法3: 触发完整的事件序列
                const events = ['mousedown', 'mouseup', 'click'];
                events.forEach(eventType => {
                    const event = new MouseEvent(eventType, {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    targetElement.dispatchEvent(event);
                });
                
                // 方法4: 尝试找到父组件并触发其点击处理
                let clickableParent = targetElement.parentElement;
                while (clickableParent && clickableParent.tagName !== 'BODY') {
                    const style = window.getComputedStyle(clickableParent);
                    if (style.cursor === 'pointer') {
                        console.log('Clicking parent with pointer cursor');
                        clickableParent.click();
                        return 'clicked pointer parent';
                    }
                    clickableParent = clickableParent.parentElement;
                }
                
                // 最后尝试: 直接点击
                targetElement.click();
                return 'clicked directly';
            }
        """)
        
        print(f"结果: {result}")
        
        # 等待页面跳转
        print("\n等待5秒...")
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
    filing = VueClick()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
