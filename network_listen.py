import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class NetworkListen:
    def __init__(self):
        self.browser = CourtBrowser()
        self.requests = []
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("网络请求监听")
            print("=" * 60)
            
            # 设置请求监听
            self.browser.page.on("request", lambda request: self.log_request(request))
            self.browser.page.on("response", lambda response: self.log_response(response))
            
            # 1. 使用token登录
            if not await self.login_with_token():
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
            
            # 4. 点击"在线保全"
            print("\n[3] 点击'在线保全'...")
            print("监听网络请求中...")
            
            await self.browser.page.click("text=在线保全", timeout=5000)
            
            # 等待收集请求
            print("\n等待10秒收集请求...")
            await asyncio.sleep(10)
            
            # 显示结果
            print(f"\n收集到 {len(self.requests)} 个请求:")
            for req in self.requests[-30:]:
                print(f"  [{req['type']}] {req['method']} {req['url'][:80]}")
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    def log_request(self, request):
        """记录请求"""
        self.requests.append({
            'type': 'REQ',
            'method': request.method,
            'url': request.url
        })
    
    def log_response(self, response):
        """记录响应"""
        if response.status != 200 or 'baoquan' in response.url or 'apply' in response.url:
            self.requests.append({
                'type': 'RES',
                'method': response.request.method,
                'url': response.url,
                'status': response.status
            })
    
    async def login_with_token(self):
        print("\n[1] 使用token登录...")
        
        # 读取token
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
            
            print(f"Token: {token[:30]}...")
            
            # 设置token
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
            print(f"✗ 登录错误: {e}")
            return False

async def main():
    listen = NetworkListen()
    success = await listen.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
