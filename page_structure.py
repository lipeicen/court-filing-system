import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class PageStructure:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("检查页面结构")
            print("=" * 60)
            
            # 访问案件类型页面
            print("\n[1] 访问案件类型页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
            await asyncio.sleep(5)
            
            # 检查页面结构
            print("\n[2] 检查页面结构...")
            
            structure = await self.browser.page.evaluate("""
                () => {
                    const results = {};
                    
                    // 检查iframe
                    const iframes = document.querySelectorAll('iframe');
                    results.iframeCount = iframes.length;
                    results.iframeSrcs = Array.from(iframes).map(f => f.src);
                    
                    // 检查Shadow DOM
                    results.hasShadowDom = !!document.querySelector('*').shadowRoot;
                    
                    // 检查body内容
                    results.bodyHTML = document.body.innerHTML.substring(0, 500);
                    
                    // 检查是否有#app
                    const app = document.querySelector('#app');
                    results.appHTML = app ? app.innerHTML.substring(0, 500) : 'no #app';
                    
                    // 检查script标签
                    const scripts = document.querySelectorAll('script');
                    results.scriptCount = scripts.length;
                    results.scriptSrcs = Array.from(scripts)
                        .filter(s => s.src)
                        .map(s => s.src)
                        .filter(src => src.includes('vue') || src.includes('chunk') || src.includes('app'));
                    
                    return results;
                }
            """)
            
            print(f"\n页面结构:")
            print(f"  iframe数量: {structure.get('iframeCount', 0)}")
            print(f"  iframe来源: {structure.get('iframeSrcs', [])}")
            print(f"  有Shadow DOM: {structure.get('hasShadowDom', False)}")
            print(f"\n  Body HTML前500字符:")
            print(structure.get('bodyHTML', '')[:300])
            print(f"\n  #app HTML前500字符:")
            print(structure.get('appHTML', '')[:300])
            print(f"\n  Script数量: {structure.get('scriptCount', 0)}")
            print(f"  相关Script来源:")
            for src in structure.get('scriptSrcs', [])[:5]:
                print(f"    - {src}")
            
            # 检查frames
            print("\n[3] 检查frames...")
            frames = self.browser.page.frames
            print(f"  总frame数: {len(frames)}")
            
            for i, frame in enumerate(frames):
                try:
                    url = frame.url
                    print(f"\n  Frame {i}: {url}")
                    
                    # 检查frame中的Vue
                    frame_vue = await frame.evaluate("""
                        () => {
                            const root = document.querySelector('#app');
                            return {
                                hasVue: !!(root && root.__vue__),
                                hasVue3: !!(document.querySelector('*').__vueParentComponent)
                            };
                        }
                    """)
                    print(f"  Frame {i} Vue状态: {frame_vue}")
                except Exception as e:
                    print(f"  Frame {i} 无法访问: {e}")
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()

async def main():
    ps = PageStructure()
    success = await ps.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
