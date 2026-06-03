import asyncio
import os
import sys

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

class Vue3Find:
    def __init__(self):
        self.browser = CourtBrowser()
    
    async def run(self):
        try:
            await self.browser.launch()
            
            print("=" * 60)
            print("查找Vue 3实例")
            print("=" * 60)
            
            if not await self.check_session():
                return False
            
            # 访问案件类型页面
            print("\n[1] 访问案件类型页面...")
            await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesWsla/pc/zxla/pick-case-type/index")
            await asyncio.sleep(5)
            
            # 查找Vue实例的各种方式
            print("\n[2] 查找Vue实例...")
            
            vue_info = await self.browser.page.evaluate("""
                () => {
                    const results = {};
                    
                    // 方法1: 检查window.__VUE__
                    results.hasWindowVue = !!window.__VUE__;
                    
                    // 方法2: 检查window.Vue
                    results.hasWindowVue2 = !!window.Vue;
                    
                    // 方法3: 遍历所有元素查找__vueParentComponent（Vue 3）
                    let vue3Found = false;
                    const allElements = document.querySelectorAll('*');
                    for (const el of allElements) {
                        if (el.__vueParentComponent) {
                            vue3Found = true;
                            results.vue3Element = el.tagName;
                            break;
                        }
                    }
                    results.hasVue3 = vue3Found;
                    
                    // 方法4: 检查是否有__VUE_OPTIONS__
                    results.hasVueOptions = !!window.__VUE_OPTIONS__;
                    
                    // 方法5: 检查app元素
                    const app = document.querySelector('#app');
                    results.appExists = !!app;
                    results.appChildren = app ? app.children.length : 0;
                    
                    // 方法6: 检查是否有data-v属性（Vue组件标记）
                    const vueElements = document.querySelectorAll('[data-v-]');
                    results.vueElementsCount = vueElements.length;
                    
                    // 方法7: 检查script标签中的Vue相关代码
                    const scripts = document.querySelectorAll('script');
                    let hasVueScript = false;
                    for (const script of scripts) {
                        if (script.src && (script.src.includes('vue') || script.src.includes('chunk'))) {
                            hasVueScript = true;
                            break;
                        }
                    }
                    results.hasVueScript = hasVueScript;
                    
                    return results;
                }
            """)
            
            print(f"\nVue查找结果:")
            for key, value in vue_info.items():
                print(f"  {key}: {value}")
            
            # 如果找到Vue 3，尝试获取router
            if vue_info.get('hasVue3'):
                print("\n[3] 尝试通过Vue 3获取router...")
                
                router_info = await self.browser.page.evaluate("""
                    () => {
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            if (el.__vueParentComponent) {
                                const component = el.__vueParentComponent;
                                
                                // 查找app上下文中的router
                                if (component.appContext && component.appContext.config) {
                                    return {
                                        hasAppContext: true,
                                        configKeys: Object.keys(component.appContext.config)
                                    };
                                }
                                
                                // 查找provides中的router
                                if (component.provides) {
                                    const keys = Object.keys(component.provides);
                                    return {
                                        hasProvides: true,
                                        provideKeys: keys
                                    };
                                }
                                
                                break;
                            }
                        }
                        return { notFound: true };
                    }
                """)
                
                print(f"Router信息: {router_info}")
            
            # 尝试直接通过window.history导航
            print("\n[4] 尝试通过history导航...")
            await self.browser.page.evaluate("""
                () => {
                    window.history.pushState({}, '', '#/pagesWsla/pc/zxla/apply-baoquan/index');
                    // 触发popstate事件
                    window.dispatchEvent(new PopStateEvent('popstate'));
                    return 'navigated via history';
                }
            """)
            
            await asyncio.sleep(5)
            print(f"当前URL: {self.browser.page.url}")
            
            # 获取页面内容
            page_text = await self.browser.page.evaluate("() => document.body.innerText")
            print(f"\n页面内容长度: {len(page_text)}")
            print("\n内容:")
            print(page_text[:500])
            
            return True
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.browser.close()
    
    async def check_session(self):
        print("检查会话...")
        await self.browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        if "login" in self.browser.page.url:
            print("✗ 会话过期")
            return False
        
        print("✓ 会话有效")
        return True

async def main():
    find = Vue3Find()
    success = await find.run()
    print("\n✓ 完成" if success else "\n✗ 失败")

if __name__ == "__main__":
    asyncio.run(main())
