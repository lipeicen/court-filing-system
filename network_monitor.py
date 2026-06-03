import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class NetworkMonitor:
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
            self.browser.page.on("request", self.handle_request)
            self.browser.page.on("response", self.handle_response)
            
            # 1. 登录
            if not await self.login():
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
            
            # 4. 点击"在线保全"并监听请求
            print("\n[3] 点击'在线保全'...")
            print("监听网络请求...")
            
            await self.browser.page.click("text=在线保全", timeout=5000)
            
            # 等待一段时间收集请求
            print("\n等待10秒收集请求...")
            await asyncio.sleep(10)
            
            # 显示收集到的请求
            print(f"\n收集到 {len(self.requests)} 个请求:")
            for req in self.requests[-20:]:  # 显示最后20个
                print(f"  {req['method']} {req['url'][:100]}")
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    def handle_request(self, request):
        """处理请求"""
        self.requests.append({
            'method': request.method,
            'url': request.url,
            'type': request.resource_type
        })
    
    def handle_response(self, response):
        """处理响应"""
        if response.status >= 300 or 'baoquan' in response.url or 'apply' in response.url:
            print(f"  [响应] {response.status} {response.url[:80]}")
    
    async def login(self):
        print("\n[1] 登录...")
        
        # 读取token
        try:
            with open(r"C:\court-auto-filing\court_session.json", 'r') as f:
                session = json.load(f)
                
            # 提取token
            token = None
            for cookie in session.get('cookies', []):
                if cookie.get('name') == 'zxfwtoken':
                    token = cookie.get('value')
                    break
            
            if not token:
                print("✗ 没有token")
                return False
            
            print(f"使用token: {token[:30]}...")
            
            # 设置token
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(2)
            
            await self.browser.page.evaluate(f"""
                () => {{
                    localStorage.setItem('zxfwtoken', '{token}');
                }}
            """)
            
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(3)
            
            if "login" not in self.browser.page.url:
                print("✓ 登录成功")
                return True
            else:
                print("✗ 登录失败")
                return False
                
        except Exception as e:
            print(f"✗ 登录错误: {e}")
            return False

async def main():
    monitor = NetworkMonitor()
    success = await monitor.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
