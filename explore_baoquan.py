import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class ExploreBaoquan:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("探索保全申请页面")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            if not await self.navigate_to_baoquan():
                return False
            
            # 探索页面内容
            await self.explore_page()
            
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
    
    async def navigate_to_baoquan(self):
        print("\n[2] 导航到保全申请页面...")
        
        # 直接访问保全申请URL
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
        await asyncio.sleep(5)
        
        if "login" in self.browser.page.url:
            print("✗ 需要登录")
            return False
        
        print(f"✓ 当前URL: {self.browser.page.url}")
        return True
    
    async def explore_page(self):
        print("\n[3] 探索页面内容...")
        
        # 获取页面完整文本
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        
        print(f"\n页面内容长度: {len(page_text)}")
        print("\n完整页面内容:")
        print("=" * 60)
        print(page_text)
        print("=" * 60)
        
        # 查找表单元素
        print("\n[4] 查找表单元素...")
        
        inputs = await self.browser.page.query_selector_all('input')
        print(f"\n输入框数量: {len(inputs)}")
        
        for i, input_el in enumerate(inputs[:10]):  # 只显示前10个
            try:
                input_type = await input_el.get_attribute('type') or 'text'
                input_name = await input_el.get_attribute('name') or ''
                input_placeholder = await input_el.get_attribute('placeholder') or ''
                print(f"  输入框 {i+1}: type={input_type}, name={input_name}, placeholder={input_placeholder}")
            except:
                pass
        
        # 查找按钮
        buttons = await self.browser.page.query_selector_all('button')
        print(f"\n按钮数量: {len(buttons)}")
        
        for i, btn in enumerate(buttons[:10]):
            try:
                btn_text = await btn.text_content()
                if btn_text:
                    print(f"  按钮 {i+1}: {btn_text.strip()}")
            except:
                pass
        
        # 查找所有链接
        links = await self.browser.page.query_selector_all('a')
        print(f"\n链接数量: {len(links)}")
        
        # 查找选择器
        selects = await self.browser.page.query_selector_all('select')
        print(f"\n选择器数量: {len(selects)}")
        
        # 截图
        print("\n[5] 保存截图...")
        await self.browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baoquan_explore.png"))
        print("✓ 已保存截图")

async def main():
    explore = ExploreBaoquan()
    success = await explore.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
