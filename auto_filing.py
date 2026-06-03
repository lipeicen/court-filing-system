import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings
from PIL import Image
import ddddocr

class AutoFiling:
    """完整的自动立案流程"""
    
    def __init__(self):
        self.browser = CourtBrowser()
        self.ocr = ddddocr.DdddOcr()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("自动立案系统")
            print("=" * 60)
            
            # 1. 自动登录
            if not await self.auto_login():
                return False
            
            # 2. 导航到在线立案
            if not await self.navigate_to_filing():
                return False
            
            # 3. 处理弹窗
            await self.handle_popups()
            
            # 4. 点击在线保全
            if not await self.click_baoquan():
                return False
            
            # 5. 等待页面加载并检查
            await self.check_baoquan_page()
            
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
    
    async def auto_login(self):
        """自动登录"""
        print("\n[1] 自动登录...")
        
        # 访问登录页面
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 检查是否已经登录
        if "login" not in self.browser.page.url:
            print("✓ 已经登录")
            return True
        
        # 点击律师用户
        print("  点击律师用户...")
        await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '律师用户') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(1)
        
        # 点击密码登录
        print("  点击密码登录...")
        await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '密码登录') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(1)
        
        # 获取输入框
        inputs = await self.browser.page.query_selector_all(".uni-input-input")
        print(f"  找到 {len(inputs)} 个输入框")
        
        if len(inputs) < 3:
            print("✗ 输入框数量不对")
            return False
        
        # 填写账号密码
        print("  填写账号密码...")
        await inputs[0].fill(settings.COURT_USERNAME)
        await inputs[1].fill(settings.COURT_PASSWORD)
        
        # 识别验证码
        print("  识别验证码...")
        
        # 截图验证码区域
        captcha_input = inputs[2]
        box = await captcha_input.bounding_box()
        
        if box:
            # 截图验证码
            captcha_path = r"C:\court-auto-filing\captcha_login.png"
            await self.browser.page.screenshot(path=captcha_path, clip={
                'x': box['x'] - 100,
                'y': box['y'] - 50,
                'width': 200,
                'height': 100
            })
            
            # OCR识别
            img = Image.open(captcha_path)
            captcha_code = self.ocr.classification(img)
            print(f"  验证码: {captcha_code}")
            
            # 填写验证码
            await inputs[2].fill(captcha_code)
        
        # 点击登录按钮
        print("  点击登录...")
        await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '登录') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        # 等待登录结果
        await asyncio.sleep(5)
        
        if "login" in self.browser.page.url:
            print("✗ 登录失败")
            return False
        
        print("✓ 登录成功")
        
        # 保存会话
        await self.browser.save_session()
        print("✓ 会话已保存")
        
        return True
    
    async def navigate_to_filing(self):
        """导航到在线立案"""
        print("\n[2] 导航到在线立案...")
        
        await self.browser.page.click("text=在线立案", timeout=5000)
        await asyncio.sleep(3)
        
        print(f"当前URL: {self.browser.page.url}")
        return True
    
    async def handle_popups(self):
        """处理弹窗"""
        print("\n[3] 处理弹窗...")
        
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
        print("\n[4] 点击在线保全...")
        
        # 使用JavaScript点击
        result = await self.browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '在线保全') {
                        // 向上查找可点击的父元素
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
    
    async def check_baoquan_page(self):
        """检查保全页面"""
        print("\n[5] 检查保全页面...")
        
        url = self.browser.page.url
        print(f"当前URL: {url}")
        
        # 获取页面内容
        page_text = await self.browser.page.evaluate("() => document.body.innerText")
        print(f"页面内容长度: {len(page_text)}")
        print(f"页面内容: {page_text[:500]}")
        
        # 查找表单
        inputs = await self.browser.page.query_selector_all('input')
        print(f"输入框: {len(inputs)}")
        
        buttons = await self.browser.page.query_selector_all('button')
        print(f"按钮: {len(buttons)}")

async def main():
    filing = AutoFiling()
    success = await filing.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
