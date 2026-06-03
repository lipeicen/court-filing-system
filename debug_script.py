import asyncio
import os
import sys
import json

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class DebugScript:
    def __init__(self):
        self.browser = CourtBrowser()
    
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
            
            # 4. 查找"在线保全"元素并分析
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
                                attributes: {},
                                parentTagName: el.parentElement ? el.parentElement.tagName : null,
                                parentClassName: el.parentElement ? el.parentElement.className : null,
                                grandparentTagName: el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.tagName : null,
                                grandparentClassName: el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.className : null,
                                onclick: el.onclick ? 'has onclick' : 'no onclick',
                                hasClickEvent: el.onclick !== null,
                                style: el.style.cssText,
                                rect: el.getBoundingClientRect ? {
                                    top: el.getBoundingClientRect().top,
                                    left: el.getBoundingClientRect().left,
                                    width: el.getBoundingClientRect().width,
                                    height: el.getBoundingClientRect().height
                                } : null
                            };
                            
                            // 获取所有属性
                            for (const attr of el.attributes) {
                                info.attributes[attr.name] = attr.value;
                            }
                            
                            return info;
                        }
                    }
                    return null;
                }
            """)
            
            print(f"\n元素信息:")
            print(json.dumps(element_info, ensure_ascii=False, indent=2))
            
            # 5. 尝试多种点击方式
            print("\n[5] 尝试多种点击方式...")
            
            # 方式1: 直接点击元素
            print("\n方式1: 直接点击...")
            await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            el.click();
                            return 'clicked';
                        }
                    }
                    return 'not found';
                }
            """)
            await asyncio.sleep(3)
            print(f"URL: {self.browser.page.url}")
            
            # 方式2: 点击父元素
            print("\n方式2: 点击父元素...")
            await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            const parent = el.parentElement;
                            if (parent) {
                                parent.click();
                                return 'clicked parent: ' + parent.tagName;
                            }
                        }
                    }
                    return 'not found';
                }
            """)
            await asyncio.sleep(3)
            print(f"URL: {self.browser.page.url}")
            
            # 方式3: 点击祖父元素
            print("\n方式3: 点击祖父元素...")
            await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            const grandparent = el.parentElement && el.parentElement.parentElement;
                            if (grandparent) {
                                grandparent.click();
                                return 'clicked grandparent: ' + grandparent.tagName;
                            }
                        }
                    }
                    return 'not found';
                }
            """)
            await asyncio.sleep(3)
            print(f"URL: {self.browser.page.url}")
            
            # 方式4: 触发mousedown/mouseup/click序列
            print("\n方式4: 触发完整鼠标事件...")
            await self.browser.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        if (el.textContent && el.textContent.trim() === '在线保全') {
                            const events = ['mousedown', 'mouseup', 'click'];
                            events.forEach(type => {
                                const event = new MouseEvent(type, {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                el.dispatchEvent(event);
                            });
                            return 'triggered events';
                        }
                    }
                    return 'not found';
                }
            """)
            await asyncio.sleep(3)
            print(f"URL: {self.browser.page.url}")
            
            # 方式5: 使用uni-app导航
            print("\n方式5: 使用uni-app导航...")
            await self.browser.page.evaluate("""
                () => {
                    if (window.uni) {
                        uni.navigateTo({
                            url: '/pagesWsla/pc/zxla/apply-baoquan/index'
                        });
                        return 'uni.navigateTo called';
                    }
                    return 'uni not found';
                }
            """)
            await asyncio.sleep(3)
            print(f"URL: {self.browser.page.url}")
            
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
        
        # 尝试使用保存的token
        try:
            with open(os.path.join(settings.DATA_DIR, 'session.json'), 'r') as f:
                session = json.load(f)
                token = session.get('token')
                
            if token:
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
                    print("✓ 使用token登录成功")
                    return True
        except:
            pass
        
        print("需要手动登录")
        return False

async def main():
    debug = DebugScript()
    success = await debug.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
