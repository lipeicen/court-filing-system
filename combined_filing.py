import asyncio
import os
import sys
import json
import subprocess

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class CombinedFiling:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("组合立案流程")
            print("=" * 60)
            
            # 1. 使用reliable_login.py登录
            if not await self.login_with_reliable():
                return False
            
            # 2. 加载保存的会话
            if not await self.load_session():
                return False
            
            # 3. 导航到在线立案
            if not await self.navigate_to_filing():
                return False
            
            # 4. 处理弹窗
            await self.handle_popups()
            
            # 5. 点击在线保全
            if not await self.click_baoquan():
                return False
            
            # 6. 检查页面
            await self.check_page()
            
            print("\n" + "=" * 60)
            print("✓ 流程完成")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def login_with_reliable(self):
        """使用reliable_login.py登录"""
        print("\n[1] 使用reliable_login.py登录...")
        
        # 先关闭当前浏览器
        await self.browser.close()
        
        # 运行reliable_login.py
        result = subprocess.run(
            [sys.executable, "reliable_login.py"],
            cwd=r"C:\court-auto-filing",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("reliable_login输出:")
        print(result.stdout[-500:])
        
        if result.returncode != 0:
            print("✗ reliable_login失败")
            return False
        
        print("✓ reliable_login完成")
        
        # 重新启动浏览器
        self.browser = CourtBrowser()
        await self.browser.launch()
        
        return True
    
    async def load_session(self):
        """加载保存的会话"""
        print("\n[2] 加载会话...")
        
        try:
            # 从session.json加载
            with open(r"C:\court-auto-filing\court_session.json", 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            # 提取token
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
            
            # 访问首页并设置token
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
            
            print("✓ 会话加载成功")
            return True
            
        except Exception as e:
            print(f"✗ 加载会话失败: {e}")
            return False
    
    async def navigate_to_filing(self):
        """导航到在线立案"""
        print("\n[3] 导航到在线立案...")
        
        await self.browser.page.click("text=在线立案", timeout=5000)
        await asyncio.sleep(3)
        
        print(f"当前URL: {self.browser.page.url}")
        return True
    
    async def handle_popups(self):
        """处理弹窗"""
        print("\n[4] 处理弹窗...")
        
        await self.browser.page.evaluate("""
            () => {
                document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                    if (el && el.style) el.style.display = 'none';
                });
                document.body.style.overflow = 'auto';
            }
        """)
        
        print("✓ 弹窗已关闭")
    
    async def click_baoquan(self):
        """点击在线保全"""
        print("\n[5] 点击在线保全...")
        
        # 使用JavaScript点击
        result = await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        let target = el;
                        for (let i = 0; i < 10; i++) {
                            if (!target) break;
                            
                            const style = window.getComputedStyle(target);
                            if (style.cursor === 'pointer' || target.tagName === 'A' || 
                                target.tagName === 'BUTTON') {
                                target.click();
                                return { clicked: true, level: i, tagName: target.tagName };
                            }
                            
                            target = target.parentElement;
                        }
                        
                        return { clicked: false, reason: 'no clickable parent' };
                    }
                }
                return { clicked: false, reason: 'not found' };
            }
        """)
        
        print(f"点击结果: {result}")
        await asyncio.sleep(5)
        
        return True
    
    async def check_page(self):
        """检查页面"""
        print("\n[6] 检查页面...")
        
        url = self.browser.page.url
        print(f"当前URL: {url}")
        
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"页面内容: {page_text[:500]}")
        
        inputs = await self.browser.page.query_selector_all('input')
        print(f"输入框: {len(inputs)}")

async def main():
    filing = CombinedFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
