from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录
    page.goto("https://zxfw.court.gov.cn/login")
    time.sleep(3)
    
    # 选择律师用户
    page.get_by_text("律师", exact=True).click()
    time.sleep(0.5)
    
    # 输入手机号
    page.get_by_placeholder("请输入手机号").fill("13723715831")
    time.sleep(0.5)
    
    # 输入密码
    page.get_by_placeholder("请输入密码").fill("HU1234pp")
    time.sleep(0.5)
    
    # 登录
    page.get_by_text("登录", exact=True).click()
    time.sleep(5)
    
    # 进入保全申请流程（简化版，直接到财产线索弹窗）
    # ... 这里需要完整的流程到财产线索弹窗
    
    print("请手动操作到财产线索弹窗，然后按Enter继续...")
    input()
    
    # 获取页面HTML
    html = page.content()
    with open(r'C:\court-auto-filing\debug_dropdown.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 获取所有下拉选项
    options = page.evaluate("""() => {
        const result = [];
        const dropdowns = document.querySelectorAll('.el-select-dropdown, .el-dropdown-menu, .uni-popup');
        for(let dropdown of dropdowns) {
            const items = dropdown.querySelectorAll('li, .el-select-dropdown__item, .el-dropdown-menu__item');
            for(let item of items) {
                if(item.textContent.trim()) {
                    result.push({
                        text: item.textContent.trim(),
                        className: item.className,
                        tagName: item.tagName
                    });
                }
            }
        }
        return result;
    }""")
    
    print(f"找到 {len(options)} 个下拉选项:")
    for opt in options[:20]:
        print(f"  {opt['text']} ({opt['tagName']}.{opt['className']})")
    
    browser.close()
