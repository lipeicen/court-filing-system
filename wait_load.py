import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class WaitLoad:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("等待保全页面加载")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            # 导航到保全页面
            print("\n[1] 导航到保全申请页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
            
            # 等待页面加载
            print("\n[2] 等待页面加载...")
            await asyncio.sleep(10)
            
            print(f"当前URL: {self.browser.page.url}")
            
            # 等待网络空闲
            print("\n[3] 等待网络空闲...")
            try:
                await self.browser.page.wait_for_load_state('networkidle', timeout=10000)
                print("✓ 网络空闲")
            except:
                print("! 网络未完全空闲")
            
            # 获取页面内容
            print("\n[4] 获取页面内容...")
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"内容长度: {len(page_text)}")
            print("\n内容:")
            print(page_text[:1000])
            
            # 检查是否有加载动画
            print("\n[5] 检查加载状态...")
            loading = await self.browser.page.evaluate("""
                () => {
                    const loaders = document.querySelectorAll('.loading, .el-loading, [class*="loading"], [class*="Loading"]');
                    return {
                        loaderCount: loaders.length,
                        isVisible: Array.from(loaders).some(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && style.visibility !== 'hidden';
                        })
                    };
                }
            """)
            print(f"加载状态: {loading}")
            
            # 检查Vue是否挂载
            print("\n[6] 检查Vue状态...")
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
            print(f"Vue状态: {vue_status}")
            
            # 截图
            await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_wait.png"))
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

async def main():
    wait = WaitLoad()
    success = await wait.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
