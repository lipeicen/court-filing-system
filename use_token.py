import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class UseToken:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("使用Token保持会话")
            print("=" * 60)
            
            # 1. 先登录获取token
            if not await self.login():
                return False
            
            # 2. 获取token
            token = await self.get_token()
            print(f"\nToken: {token[:50]}..." if token else "未获取到token")
            
            # 3. 使用token访问保全页面
            if not await self.access_baoquan_with_token(token):
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
    
    async def login(self):
        print("\n[1] 登录...")
        
        # 访问登录页面
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 检查是否已经登录
        if "login" not in self.browser.page.url:
            print("✓ 已经登录")
            return True
        
        print("需要手动登录，请在浏览器中完成登录...")
        print("登录完成后按Enter继续（30秒超时）...")
        
        # 等待用户登录
        for i in range(30):
            await asyncio.sleep(1)
            if "login" not in self.browser.page.url:
                print("✓ 检测到登录成功")
                return True
        
        print("✗ 登录超时")
        return False
    
    async def get_token(self):
        print("\n[2] 获取Token...")
        
        token = await self.browser.page.evaluate("() => localStorage.getItem('zxfwtoken')")
        return token
    
    async def access_baoquan_with_token(self, token):
        print("\n[3] 使用Token访问保全页面...")
        
        # 设置token到localStorage
        if token:
            await self.browser.page.evaluate(f"""
                () => {{
                    localStorage.setItem('zxfwtoken', '{token}');
                    return 'token set';
                }}
            """)
        
        # 导航到保全页面
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
        await asyncio.sleep(5)
        
        print(f"当前URL: {self.browser.page.url}")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容长度: {len(page_text)}")
        print("\n内容:")
        print(page_text[:500])
        
        # 检查是否有表单
        inputs = await self.browser.page.query_selector_all('input')
        print(f"\n输入框: {len(inputs)}")
        
        return True

async def main():
    ut = UseToken()
    success = await ut.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
