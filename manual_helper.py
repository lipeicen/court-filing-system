import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class ManualHelper:
    """手动操作辅助脚本"""
    
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("手动操作辅助")
            print("=" * 60)
            
            # 1. 加载会话
            if not await self.load_session():
                print("请先运行 reliable_login.py 登录")
                return False
            
            # 2. 导航到案件类型页面
            print("\n[2] 导航到案件类型页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
            await asyncio.sleep(5)
            
            # 3. 关闭弹窗
            await self.browser.page.evaluate("""
                () => {
                    document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                        if (el && el.style) el.style.display = 'none';
                    });
                    document.body.style.overflow = 'auto';
                }
            """)
            
            print("\n" + "=" * 60)
            print("请手动操作:")
            print("1. 在浏览器中点击'在线保全'")
            print("2. 观察页面跳转后的URL")
            print("3. 按 Ctrl+C 结束脚本")
            print("=" * 60)
            
            # 保持浏览器打开
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n用户中断")
            
            # 获取当前URL
            url = self.browser.page.url
            print(f"\n当前URL: {url}")
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"页面内容: {page_text[:500]}")
            
            return True
        except Exception as e:
            print(f"错误: {e}")
            return False
        finally:
            await self.browser.close()
    
    async def load_session(self):
        print("\n[1] 加载会话...")
        
        try:
            with open(r"C:\court-auto-filing\court_session.json", 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            token = None
            for origin in session.get('origins', []):
                for item in origin.get('localStorage', []):
                    if item.get('name') == 'loginData':
                        login_data = json.loads(item.get('value', '{}'))
                        if 'data' in login_data and 'token' in login_data['data']:
                            token = login_data['data']['token']
                            break
            
            if not token:
                print("✗ 未找到token")
                return False
            
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(2)
            
            await self.browser.page.evaluate(f"""
                () => {{
                    localStorage.setItem('zxfwtoken', '{token}');
                    const loginData = {{
                        type: 'object',
                        data: {{
                            userId: 'af56109a637f4f8099e349b4321467f7',
                            username: '胡远洋',
                            role: '2',
                            roleText: '律师',
                            token: '{token}'
                        }}
                    }};
                    localStorage.setItem('loginData', JSON.stringify(loginData));
                }}
            """)
            
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(3)
            
            if "login" in self.browser.page.url:
                print("✗ 登录失败")
                return False
            
            print("✓ 登录成功")
            return True
            
        except Exception as e:
            print(f"✗ 加载会话失败: {e}")
            return False

async def main():
    helper = ManualHelper()
    success = await helper.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
