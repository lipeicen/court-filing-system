import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, r"C:\court-auto-filing")

from core.browser_controller import CourtBrowser
from config import settings

async def filing_with_session():
    """使用已有会话进行立案"""
    browser = CourtBrowser()
    
    try:
        await browser.launch()
        
        print("=" * 60)
        print("法院自动立案系统 - 使用已有会话")
        print("=" * 60)
        
        # 尝试恢复会话
        print("\n[1/3] 恢复会话...")
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pages/pc/home/index")
        await asyncio.sleep(3)
        
        # 检查是否已登录
        if "login" in browser.page.url:
            print("会话已过期，需要重新登录")
            print("请运行: python reliable_login.py")
            return False
        
        print("✓ 会话有效")
        
        # 2. 导航到保全申请页面
        print("\n[2/3] 导航到保全申请页面...")
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
        await asyncio.sleep(3)
        
        if "login" in browser.page.url:
            print("会话过期")
            return False
        
        # 截图查看页面
        await browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "baqx_page.png"))
        print("✓ 已加载保全申请页面")
        
        # 获取页面内容
        page_text = await browser.page.evaluate("() => document.body.innerText")
        print(f"\n页面内容预览:")
        print(page_text[:500])
        
        # 查找申请按钮
        print("\n[3/3] 查找申请入口...")
        
        # 查找所有按钮和链接
        buttons = await browser.page.query_selector_all("button, a, [class*='btn'], [class*='button']")
        print(f"找到 {len(buttons)} 个可点击元素")
        
        # 查找包含"申请"的元素
        apply_elements = await browser.page.evaluate("""
            () => {
                const results = [];
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && (
                        el.textContent.includes('申请') ||
                        el.textContent.includes('立案') ||
                        el.textContent.includes('保全')
                    )) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            results.push({
                                text: el.textContent.trim(),
                                tag: el.tagName,
                                class: el.className,
                                id: el.id
                            });
                        }
                    }
                }
                return results.slice(0, 20);  // 只返回前20个
            }
        """)
        
        print("\n找到的相关元素:")
        for i, el in enumerate(apply_elements):
            print(f"  {i+1}. {el['text'][:50]} (tag: {el['tag']}, class: {el['class'][:30]})")
        
        # 尝试点击"申请保全"按钮
        clicked = await browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim() === '申请保全') {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        
        if clicked:
            print("\n✓ 已点击'申请保全'按钮")
            await asyncio.sleep(3)
            
            # 截图查看申请页面
            await browser.page.screenshot(path=os.path.join(settings.SCREENSHOT_DIR, "apply_page.png"))
            print("✓ 已保存申请页面截图")
        else:
            print("\n未找到'申请保全'按钮")
        
        print("\n" + "=" * 60)
        print("当前状态已保存，请查看截图")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(filing_with_session())
