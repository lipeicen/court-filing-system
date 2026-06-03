import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class FinalFiling:
    """最终版立案脚本 - 使用已有会话"""
    
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统")
            print("=" * 60)
            
            # 1. 检查并使用已有会话
            if not await self.use_existing_session():
                print("\n请先运行 reliable_login.py 登录")
                return False
            
            # 2. 导航到在线立案
            if not await self.navigate_to_online_filing():
                return False
            
            # 3. 处理弹窗
            await self.handle_popups()
            
            # 4. 点击"在线保全"
            if not await self.click_online_baoquan():
                return False
            
            # 5. 等待并探索保全页面
            await self.explore_baoquan_page()
            
            print("\n" + "=" * 60)
            print("✓ 流程完成")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def use_existing_session(self):
        """使用已有会话"""
        print("\n[1] 检查已有会话...")
        
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        if "login" in self.browser.page.url:
            print("✗ 会话已过期")
            return False
        
        # 检查页面内容确认登录状态
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        if "登录" in page_text and "个人用户" in page_text:
            print("✗ 未登录")
            return False
        
        print("✓ 会话有效")
        return True
    
    async def navigate_to_online_filing(self):
        """导航到在线立案"""
        print("\n[2] 导航到在线立案...")
        
        # 点击左侧"在线立案"
        try:
            await self.browser.page.click("text=在线立案", timeout=5000)
            print("✓ 已点击'在线立案'")
        except Exception as e:
            print(f"! 点击失败: {e}")
            # 直接导航
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
        
        await asyncio.sleep(3)
        
        # 等待页面加载
        try:
            await self.browser.page.wait_for_selector("text=选择案件类型", timeout=10000)
            print("✓ 已加载案件类型选择页面")
        except:
            print("! 等待超时，继续执行")
        
        return True
    
    async def handle_popups(self):
        """处理弹窗"""
        print("\n[3] 处理弹窗...")
        
        # 使用JavaScript关闭弹窗
        await self.browser.page.evaluate("""
            () => {
                // 关闭所有可能的弹窗
                const selectors = [
                    '.el-dialog', '.el-overlay', '.modal', '.popup',
                    '.dialog', '[class*="dialog"]', '[class*="Dialog"]',
                    '[class*="overlay"]', '[class*="mask"]'
                ];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el && el.style) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                        }
                    });
                });
                
                // 恢复滚动
                document.body.style.overflow = 'auto';
                
                return 'done';
            }
        """)
        
        await asyncio.sleep(1)
        print("✓ 弹窗已处理")
    
    async def click_online_baoquan(self):
        """点击在线保全"""
        print("\n[4] 点击'在线保全'...")
        
        try:
            # 使用Playwright点击
            await self.browser.page.click("text=在线保全", timeout=5000)
            print("✓ 已点击'在线保全'")
        except Exception as e:
            print(f"! Playwright点击失败: {e}")
            
            # 使用JavaScript点击
            result = await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            el.click();
                            return 'clicked';
                        }
                    }
                    return 'not found';
                }
            """)
            print(f"JavaScript点击结果: {result}")
        
        await asyncio.sleep(5)
        
        # 检查URL
        current_url = self.browser.page.url
        print(f"当前URL: {current_url}")
        
        if "baoquan" in current_url or "apply" in current_url:
            print("✓ 页面已跳转")
            return True
        else:
            print("! 页面可能未跳转，继续执行")
            return True
    
    async def explore_baoquan_page(self):
        """探索保全页面"""
        print("\n[5] 探索保全页面...")
        
        # 等待页面加载
        await asyncio.sleep(3)
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容长度: {len(page_text)}")
        print("\n页面内容:")
        print(page_text[:800])
        
        # 查找表单元素
        print("\n[6] 查找表单元素...")
        
        inputs = await self.browser.page.query_selector_all('input')
        print(f"输入框数量: {len(inputs)}")
        
        buttons = await self.browser.page.query_selector_all('button')
        print(f"按钮数量: {len(buttons)}")
        
        selects = await self.browser.page.query_selector_all('select')
        print(f"选择器数量: {len(selects)}")
        
        # 截图
        try:
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_final.png"))
            print("\n✓ 已保存截图")
        except Exception as e:
            print(f"! 截图失败: {e}")

async def main():
    filing = FinalFiling()
    success = await filing.run()
    
    if success:
        print("\n✓ 操作完成")
    else:
        print("\n✗ 操作失败")

if __name__ == "__main__":
    asyncio.run(main())
