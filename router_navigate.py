import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class RouterNavigate:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("法院自动立案系统 - 直接路由导航")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            if not await self.navigate_to_filing():
                return False
            
            await self.close_popup()
            
            # 尝试通过Vue Router导航
            if not await self.navigate_via_router():
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
    
    async def navigate_via_router(self):
        print("\n[4] 通过Vue Router导航...")
        
        # 尝试找到Vue Router实例并导航
        result = await self.browser.page.evaluate("""
            () => {
                // 方法1: 查找Vue根实例
                const root = document.querySelector('#app');
                if (root && root.__vue__) {
                    const vue = root.__vue__;
                    
                    // 查找router
                    if (vue.$router) {
                        console.log('Found router');
                        
                        // 尝试导航到保全页面
                        vue.$router.push('/pagesWsla/pc/zxla/apply-baoquan/index');
                        return 'navigated via router.push';
                    }
                }
                
                // 方法2: 查找所有Vue实例
                const allElements = document.querySelectorAll('*');
                for (const el of allElements) {
                    if (el.__vue__ && el.__vue__.$router) {
                        el.__vue__.$router.push('/pagesWsla/pc/zxla/apply-baoquan/index');
                        return 'navigated via element router';
                    }
                }
                
                // 方法3: 直接修改hash
                window.location.hash = '#/pagesWsla/pc/zxla/apply-baoquan/index';
                return 'navigated via hash';
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
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print("\n新页面内容:")
            print(page_text[:500])
            
            return True
        else:
            print("! 页面未跳转")
            return False

async def main():
    filing = RouterNavigate()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
