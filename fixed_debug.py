import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser

class FixedDebug:
    def __init__(self):
        self.browser = CourtBrowser()
        self.data_dir = r"C:\court-auto-filing\data"
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("调试脚本")
            print("=" * 60)
            
            # 1. 登录
            if not await self.login():
                return False
            
            # 2. 导航到案件类型页面
            print("\n[2] 导航到案件类型页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
            await asyncio.sleep(5)
            
            # 3. 关闭弹窗
            print("[3] 关闭弹窗...")
            await self.browser.page.evaluate("""
                () => {
                    document.querySelectorAll('.el-dialog, .el-overlay').forEach(el => {
                        if (el && el.style) el.style.display = 'none';
                    });
                    document.body.style.overflow = 'auto';
                }
            """)
            
            # 4. 分析"在线保全"元素
            print("\n[4] 分析'在线保全'元素...")
            
            element_info = await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            const info = {
                                tagName: el.tagName,
                                className: el.className,
                                id: el.id,
                                parentTagName: el.parentElement ? el.parentElement.tagName : null,
                                parentClassName: el.parentElement ? el.parentElement.className : null,
                                grandparentTagName: el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.tagName : null,
                                grandparentClassName: el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.className : null,
                                onclick: el.onclick ? 'has onclick' : 'no onclick',
                                style: el.style.cssText,
                                rect: el.getBoundingClientRect ? {
                                    top: el.getBoundingClientRect().top,
                                    left: el.getBoundingClientRect().left,
                                    width: el.getBoundingClientRect().width,
                                    height: el.getBoundingClientRect().height
                                } : null
                            };
                            return info;
                        }
                    }
                    return null;
                }
            """)
            
            print(f"元素信息:")
            for key, value in element_info.items():
                print(f"  {key}: {value}")
            
            # 5. 尝试点击父元素（卡片）
            print("\n[5] 尝试点击父元素...")
            
            result = await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            // 向上查找可点击的卡片
                            let target = el;
                            for (let i = 0; i < 10; i++) {
                                if (!target) break;
                                
                                const style = window.getComputedStyle(target);
                                if (style.cursor === 'pointer' || target.tagName === 'A' || target.tagName === 'BUTTON') {
                                    target.click();
                                    return {
                                        clicked: true,
                                        level: i,
                                        tagName: target.tagName,
                                        className: target.className
                                    };
                                }
                                
                                target = target.parentElement;
                            }
                            
                            return { clicked: false, reason: 'no clickable parent found' };
                        }
                    }
                    return { clicked: false, reason: 'element not found' };
                }
            """)
            
            print(f"点击结果: {result}")
            
            await asyncio.sleep(5)
            print(f"\n当前URL: {self.browser.page.url}")
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"页面内容: {page_text[:300]}")
            
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
        
        # 读取token
        try:
            with open(os.path.join(self.data_dir, 'session.json'), 'r') as f:
                session = json.load(f)
                token = session.get('token')
                
            if not token:
                print("✗ 没有token")
                return False
                
            print(f"使用token: {token[:30]}...")
            
            # 访问首页并设置token
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
            await asyncio.sleep(2)
            
            await self.browser.page.evaluate(f"""
                () => {{
                    localStorage.setItem('zxfwtoken', '{token}');
                }}
            """)
            
            # 刷新页面
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
    debug = FixedDebug()
    success = await debug.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
