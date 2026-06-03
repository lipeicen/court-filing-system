import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class SmartFiling:
    """智能立案脚本"""
    
    def __init__(self):
        self.browser = CourtBrowser()
        self.token = None
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("智能立案系统")
            print("=" * 60)
            
            # 1. 确保登录
            if not await self.ensure_login():
                return False
            
            # 2. 获取用户信息
            await self.get_user_info()
            
            # 3. 导航到保全申请
            if not await self.navigate_to_baoquan():
                return False
            
            # 4. 填写保全申请
            await self.fill_application()
            
            print("\n" + "=" * 60)
            print("✓ 立案流程完成")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def ensure_login(self):
        """确保已登录"""
        print("\n[1] 检查登录状态...")
        
        # 访问首页
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        # 检查是否已登录
        if "login" not in self.browser.page.url:
            print("✓ 已登录")
            return True
        
        print("需要登录...")
        
        # 尝试使用保存的token
        try:
            with open(os.path.join(settings.DATA_DIR, 'session.json'), 'r') as f:
                session = json.load(f)
                self.token = session.get('token')
        except:
            pass
        
        if self.token:
            print("尝试使用保存的token...")
            await self.browser.page.evaluate(f"""
                () => {{
                    localStorage.setItem('zxfwtoken', '{self.token}');
                }}
            """)
            
            # 刷新页面
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(3)
            
            if "login" not in self.browser.page.url:
                print("✓ 使用token登录成功")
                return True
        
        print("✗ 需要手动登录")
        print("请运行 reliable_login.py 登录")
        return False
    
    async def get_user_info(self):
        """获取用户信息"""
        print("\n[2] 获取用户信息...")
        
        # 从localStorage获取用户信息
        user_info = await self.browser.page.evaluate("""
            () => {
                return {
                    username: localStorage.getItem('username'),
                    role: localStorage.getItem('role'),
                    roleText: localStorage.getItem('roleText'),
                    userId: localStorage.getItem('userId'),
                    provinceId: localStorage.getItem('provinceId')
                };
            }
        """)
        
        print(f"用户信息: {json.dumps(user_info, ensure_ascii=False)}")
        return user_info
    
    async def navigate_to_baoquan(self):
        """导航到保全申请"""
        print("\n[3] 导航到保全申请...")
        
        # 点击"在线立案"
        try:
            await self.browser.page.click("text=在线立案", timeout=5000)
            print("✓ 已点击'在线立案'")
        except Exception as e:
            print(f"! 点击失败: {e}")
            return False
        
        await asyncio.sleep(3)
        
        # 关闭弹窗
        await self.browser.page.evaluate("""
            () => {
                document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                    if (el && el.style) el.style.display = 'none';
                });
                document.body.style.overflow = 'auto';
            }
        """)
        
        # 点击"在线保全"
        try:
            await self.browser.page.click("text=在线保全", timeout=5000)
            print("✓ 已点击'在线保全'")
        except Exception as e:
            print(f"! 点击失败: {e}")
            return False
        
        await asyncio.sleep(5)
        
        # 检查URL
        print(f"当前URL: {self.browser.page.url}")
        
        return True
    
    async def fill_application(self):
        """填写保全申请"""
        print("\n[4] 填写保全申请...")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容: {page_text[:500]}")
        
        # 查找表单元素
        inputs = await self.browser.page.query_selector_all('input')
        print(f"\n找到 {len(inputs)} 个输入框")
        
        # 这里可以根据实际表单填写
        # 示例：
        # for i, input_el in enumerate(inputs):
        #     try:
        #         placeholder = await input_el.get_attribute('placeholder')
        #         if placeholder:
        #             print(f"输入框 {i}: {placeholder}")
        #     except:
        #         pass
        
        print("\n✓ 请根据实际页面手动填写表单")

async def main():
    filing = SmartFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
