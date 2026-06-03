import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class ApiAuth:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("API认证测试")
            print("=" * 60)
            
            # 1. 使用token登录
            if not await self.login_with_token():
                return False
            
            # 2. 获取认证头
            print("\n[2] 获取认证头...")
            
            auth_info = await self.browser.page.evaluate("""
                () => {
                    // 获取localStorage中的token
                    const token = localStorage.getItem('zxfwtoken');
                    const loginData = localStorage.getItem('loginData');
                    
                    // 获取cookie
                    const cookies = document.cookie;
                    
                    return {
                        token: token,
                        loginData: loginData,
                        cookies: cookies
                    };
                }
            """)
            
            print(f"Token: {auth_info.get('token', '')[:50]}...")
            print(f"Cookies: {auth_info.get('cookies', '')[:100]}")
            
            # 3. 使用fetch访问API（带认证头）
            print("\n[3] 使用认证头访问API...")
            
            result = await self.browser.page.evaluate("""
                async () => {
                    const token = localStorage.getItem('zxfwtoken');
                    
                    try {
                        const response = await fetch('/yzw/yzw-zxfw-lafw/api/v3/pz/fy/ajlx/330000', {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json, text/plain, */*',
                                'Authorization': 'Bearer ' + token,
                                'X-Access-Token': token,
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });
                        
                        const data = await response.json();
                        return { 
                            success: response.ok, 
                            status: response.status,
                            data: data 
                        };
                    } catch (e) {
                        return { success: false, error: e.message };
                    }
                }
            """)
            
            print(f"API结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
            
            # 4. 尝试访问保全申请API
            print("\n[4] 访问保全申请API...")
            
            baoquan_result = await self.browser.page.evaluate("""
                async () => {
                    const token = localStorage.getItem('zxfwtoken');
                    
                    const endpoints = [
                        '/yzw/yzw-zxfw-lafw/api/v3/layy/baqx/sqbd',
                        '/yzw/yzw-zxfw-lafw/api/v3/layy/baqx/sqcl',
                        '/yzw/yzw-zxfw-lafw/api/v3/layy/baqx/sqxx',
                    ];
                    
                    const results = {};
                    
                    for (const endpoint of endpoints) {
                        try {
                            const response = await fetch(endpoint, {
                                method: 'GET',
                                headers: {
                                    'Accept': 'application/json',
                                    'Authorization': 'Bearer ' + token,
                                    'X-Access-Token': token
                                }
                            });
                            
                            const data = await response.json();
                            results[endpoint] = { 
                                status: response.status, 
                                data: data 
                            };
                        } catch (e) {
                            results[endpoint] = { error: e.message };
                        }
                    }
                    
                    return results;
                }
            """)
            
            print(f"\n保全API结果:")
            print(json.dumps(baoquan_result, indent=2, ensure_ascii=False)[:1500])
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def login_with_token(self):
        print("\n[1] 使用token登录...")
        
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
            print(f"✗ 登录错误: {e}")
            return False

async def main():
    auth = ApiAuth()
    success = await auth.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
