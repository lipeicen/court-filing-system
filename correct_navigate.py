import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class CorrectNavigate:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("正确的导航方式")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            # 1. 先访问案件类型选择页面（确保Vue应用正确加载）
            if not await self.navigate_to_filing():
                return False
            
            # 2. 关闭弹窗
            await self.close_popup()
            
            # 3. 通过Vue Router导航到保全页面
            if not await self.navigate_to_baoquan():
                return False
            
            # 4. 等待并检查页面
            await self.check_page()
            
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
        print("\n[2] 导航到案件类型选择页面...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
        await asyncio.sleep(5)
        
        if "login" in self.browser.page.url:
            print("✗ 需要登录")
            return False
        
        # 检查Vue是否加载
        vue_status = await self.browser.page.evaluate("""
            () => {
                const root = document.querySelector('#app');
                return {
                    hasVue: !!(root && root.__vue__),
                    url: window.location.href
                };
            }
        """)
        print(f"Vue状态: {vue_status}")
        
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
    
    async def navigate_to_baoquan(self):
        print("\n[4] 通过Vue Router导航到保全页面...")
        
        # 使用Vue Router导航
        result = await self.browser.page.evaluate("""
            () => {
                // 查找Vue根实例
                const root = document.querySelector('#app');
                if (!root || !root.__vue__) {
                    return 'no vue instance';
                }
                
                const vue = root.__vue__;
                
                if (!vue.$router) {
                    return 'no router';
                }
                
                // 导航到保全申请页面
                vue.$router.push({
                    path: '/pagesWsla/pc/zxla/apply-baoquan/index'
                });
                
                return 'navigated';
            }
        """)
        
        print(f"结果: {result}")
        
        if result != 'navigated':
            print(f"✗ 导航失败: {result}")
            return False
        
        # 等待页面加载
        print("\n等待页面加载...")
        await asyncio.sleep(5)
        
        # 等待网络空闲
        try:
            await self.browser.page.wait_for_load_state('networkidle', timeout=10000)
            print("✓ 网络空闲")
        except:
            print("! 网络未完全空闲")
        
        print(f"\n当前URL: {self.browser.page.url}")
        return True
    
    async def check_page(self):
        print("\n[5] 检查页面内容...")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容长度: {len(page_text)}")
        print("\n页面内容:")
        print(page_text[:800])
        
        # 检查Vue状态
        vue_status = await self.browser.page.evaluate("""
            () => {
                const root = document.querySelector('#app');
                if (root && root.__vue__) {
                    return {
                        hasVue: true,
                        route: root.__vue__.$route ? root.__vue__.$route.path : 'no route'
                    };
                }
                return { hasVue: false };
            }
        """)
        print(f"\nVue状态: {vue_status}")
        
        # 查找表单元素
        print("\n[6] 查找表单元素...")
        
        inputs = await self.browser.page.query_selector_all('input, textarea')
        print(f"输入框数量: {len(inputs)}")
        
        buttons = await self.browser.page.query_selector_all('button')
        print(f"按钮数量: {len(buttons)}")
        
        # 截图
        await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_final.png"))
        print("\n✓ 已保存截图")

async def main():
    nav = CorrectNavigate()
    success = await nav.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
