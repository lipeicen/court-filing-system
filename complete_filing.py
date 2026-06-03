import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class CompleteFiling:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("完整立案流程")
            print("=" * 60)
            
            # 1. 登录
            if not await self.login():
                return False
            
            # 2. 导航到案件类型选择
            if not await self.navigate_to_filing():
                return False
            
            # 3. 关闭弹窗
            await self.close_popup()
            
            # 4. 点击"在线保全"
            if not await self.click_baoquan():
                return False
            
            # 5. 填写保全申请
            if not await self.fill_baoquan_form():
                return False
            
            print("\n✓ 立案流程完成")
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
        
        print("需要登录，请手动登录后按Enter继续...")
        # 这里可以添加自动登录逻辑，或者等待用户手动登录
        # 暂时等待30秒让用户手动登录
        await asyncio.sleep(30)
        
        # 检查是否登录成功
        if "login" in self.browser.page.url:
            print("✗ 登录失败或未完成")
            return False
        
        print("✓ 登录成功")
        return True
    
    async def navigate_to_filing(self):
        print("\n[2] 导航到案件类型选择...")
        
        # 点击"在线立案"
        await self.browser.page.click("text=在线立案", timeout=5000)
        await asyncio.sleep(3)
        
        # 等待页面加载
        await self.browser.page.wait_for_selector("text=选择案件类型", timeout=10000)
        print("✓ 已加载案件类型选择页面")
        return True
    
    async def close_popup(self):
        print("\n[3] 关闭弹窗...")
        
        try:
            # 点击关闭按钮
            await self.browser.page.click("text=关闭", timeout=3000)
            print("✓ 已关闭弹窗")
        except:
            print("! 没有弹窗或关闭失败")
        
        await asyncio.sleep(1)
    
    async def click_baoquan(self):
        print("\n[4] 点击'在线保全'...")
        
        # 点击"在线保全"按钮
        await self.browser.page.click("text=在线保全", timeout=5000)
        await asyncio.sleep(5)
        
        print("✓ 已点击'在线保全'")
        return True
    
    async def fill_baoquan_form(self):
        print("\n[5] 填写保全申请表单...")
        
        # 等待表单加载
        await asyncio.sleep(3)
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"\n当前页面内容:")
        print(page_text[:500])
        
        # 这里可以根据实际表单字段填写
        # 示例：
        # await self.browser.page.fill("#applicantName", "申请人姓名")
        # await self.browser.page.fill("#applicantId", "身份证号")
        # await self.browser.page.fill("#claimAmount", "100000")
        
        print("\n✓ 表单填写完成（请根据实际页面手动填写）")
        return True

async def main():
    filing = CompleteFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
