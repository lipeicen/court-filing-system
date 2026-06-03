import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class HashNavigate:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("使用Hash导航")
            print("=" * 60)
            
            # 1. 检查会话
            if not await self.check_session():
                return False
            
            # 2. 导航到案件类型选择页面
            if not await self.navigate_to_filing():
                return False
            
            # 3. 关闭弹窗
            await self.close_popup()
            
            # 4. 通过修改hash导航
            if not await self.navigate_by_hash():
                return False
            
            # 5. 检查页面
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
        print("\n[2] 导航到案件类型选择...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
        await asyncio.sleep(5)
        
        if "login" in self.browser.page.url:
            print("✗ 需要登录")
            return False
        
        print("✓ 已加载")
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
    
    async def navigate_by_hash(self):
        print("\n[4] 通过修改hash导航...")
        
        # 修改hash并触发路由
        result = await self.browser.page.evaluate("""
            () => {
                // 保存当前hash
                const oldHash = window.location.hash;
                
                // 设置新hash
                window.location.hash = '#/pagesWsla/pc/zxla/apply-baoquan/index';
                
                // 触发hashchange事件
                window.dispatchEvent(new HashChangeEvent('hashchange', {
                    oldURL: window.location.origin + '/' + oldHash,
                    newURL: window.location.href
                }));
                
                return {
                    oldHash: oldHash,
                    newHash: window.location.hash,
                    url: window.location.href
                };
            }
        """)
        
        print(f"结果: {result}")
        
        # 等待页面加载
        print("\n等待页面加载...")
        await asyncio.sleep(5)
        
        # 检查URL
        current_url = self.browser.page.url
        print(f"当前URL: {current_url}")
        
        return True
    
    async def check_page(self):
        print("\n[5] 检查页面...")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容长度: {len(page_text)}")
        print("\n内容:")
        print(page_text[:500])
        
        # 查找表单
        inputs = await self.browser.page.query_selector_all('input')
        print(f"\n输入框: {len(inputs)}")
        
        buttons = await self.browser.page.query_selector_all('button')
        print(f"按钮: {len(buttons)}")

async def main():
    nav = HashNavigate()
    success = await nav.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
