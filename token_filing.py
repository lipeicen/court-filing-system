import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class TokenFiling:
    def __init__(self):
        self.browser = CourtBrowser()
        self.token = None
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("使用Token立案")
            print("=" * 60)
            
            # 1. 读取token
            if not await self.load_token():
                return False
            
            # 2. 使用token登录
            if not await self.login_with_token():
                return False
            
            # 3. 导航到案件类型页面
            if not await self.navigate_to_filing():
                return False
            
            # 4. 尝试多种方式进入保全申请
            if not await self.try_enter_baoquan():
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
    
    async def load_token(self):
        print("\n[1] 加载token...")
        try:
            # 从session.json读取
            with open(r"C:\court-auto-filing\court_session.json", 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            # 从localStorage中提取token
            for origin in session.get('origins', []):
                for item in origin.get('localStorage', []):
                    if item.get('name') == 'loginData':
                        login_data = json.loads(item.get('value', '{}'))
                        if 'data' in login_data and 'token' in login_data['data']:
                            self.token = login_data['data']['token']
                            break
            
            if not self.token:
                print("✗ 未找到token")
                return False
            
            print(f"✓ Token已加载: {self.token[:30]}...")
            return True
        except Exception as e:
            print(f"✗ 加载token失败: {e}")
            return False
    
    async def login_with_token(self):
        print("\n[2] 使用token登录...")
        
        # 访问首页
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(2)
        
        # 设置token到localStorage
        await self.browser.page.evaluate(f"""
            () => {{
                localStorage.setItem('zxfwtoken', '{self.token}');
                
                // 同时设置loginData
                const loginData = {{
                    type: 'object',
                    data: {{
                        userId: 'af56109a637f4f8099e349b4321467f7',
                        username: '胡远洋',
                        role: '2',
                        roleText: '律师',
                        token: '{self.token}'
                    }}
                }};
                localStorage.setItem('loginData', JSON.stringify(loginData));
                
                return 'token set';
            }}
        """)
        
        # 刷新页面
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        # 检查登录状态
        if "login" in self.browser.page.url:
            print("✗ 登录失败")
            return False
        
        print("✓ 登录成功")
        return True
    
    async def navigate_to_filing(self):
        print("\n[3] 导航到案件类型选择...")
        
        # 点击"在线立案"
        await self.browser.page.click("text=在线立案", timeout=5000)
        await asyncio.sleep(3)
        
        print(f"当前URL: {self.browser.page.url}")
        return True
    
    async def try_enter_baoquan(self):
        print("\n[4] 尝试进入保全申请...")
        
        # 关闭弹窗
        await self.browser.page.evaluate("""
            () => {
                document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                    if (el && el.style) el.style.display = 'none';
                });
                document.body.style.overflow = 'auto';
            }
        """)
        
        # 方式1: 直接点击"在线保全"
        print("\n方式1: 直接点击...")
        await self.browser.page.click("text=在线保全", timeout=5000)
        await asyncio.sleep(5)
        
        url1 = self.browser.page.url
        print(f"URL: {url1}")
        
        if "baoquan" in url1 or "apply" in url1:
            print("✓ 成功进入保全申请")
            return True
        
        # 方式2: 使用JavaScript查找并点击可点击的父元素
        print("\n方式2: 点击可点击父元素...")
        
        result = await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        // 向上查找10层
                        let target = el;
                        for (let i = 0; i < 10; i++) {
                            if (!target) break;
                            
                            const style = window.getComputedStyle(target);
                            const rect = target.getBoundingClientRect();
                            
                            // 检查是否是可见的可点击元素
                            if (rect.width > 0 && rect.height > 0 && 
                                (style.cursor === 'pointer' || target.tagName === 'A' || 
                                 target.tagName === 'BUTTON' || target.onclick)) {
                                
                                // 模拟真实点击事件序列
                                const mousedown = new MouseEvent('mousedown', { bubbles: true, cancelable: true });
                                const mouseup = new MouseEvent('mouseup', { bubbles: true, cancelable: true });
                                const click = new MouseEvent('click', { bubbles: true, cancelable: true });
                                
                                target.dispatchEvent(mousedown);
                                target.dispatchEvent(mouseup);
                                target.dispatchEvent(click);
                                
                                return { success: true, level: i, tagName: target.tagName };
                            }
                            
                            target = target.parentElement;
                        }
                        
                        return { success: false, reason: 'no clickable parent' };
                    }
                }
                return { success: false, reason: 'element not found' };
            }
        """)
        
        print(f"结果: {result}")
        await asyncio.sleep(5)
        
        url2 = self.browser.page.url
        print(f"URL: {url2}")
        
        if "baoquan" in url2 or "apply" in url2:
            print("✓ 成功进入保全申请")
            return True
        
        # 方式3: 直接修改URL hash
        print("\n方式3: 直接修改URL...")
        
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/apply-baoquan/index")
        await asyncio.sleep(5)
        
        url3 = self.browser.page.url
        print(f"URL: {url3}")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"页面内容: {page_text[:300]}")
        
        if len(page_text) > 200:
            print("✓ 页面有内容")
            return True
        
        print("! 所有方式都未成功进入保全申请")
        return False

async def main():
    filing = TokenFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
