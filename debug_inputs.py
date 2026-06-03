from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(3)
    
    page.get_by_text("律师用户").click()
    time.sleep(1)
    
    inputs = page.locator("input").all()
    inputs[0].fill("13723715831")
    inputs[1].fill("HU1234pp")
    time.sleep(1)
    
    # 手动输入验证码后登录
    print("请手动输入验证码并登录...")
    time.sleep(15)
    
    # 进入保全页面
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    # 查找并点击保全
    elements = page.locator("uni-view").all()
    for elem in elements:
        try:
            text = elem.text_content()
            if text and "保全" in text:
                elem.click()
                break
        except:
            pass
    
    time.sleep(5)
    
    pages = context.pages
    if len(pages) > 1:
        page1 = pages[-1]
        
        # 创建保全申请（简化版）
        page1.goto("https://zxfw.court.gov.cn/yzwbqww/index.html#/createBqqw")
        time.sleep(5)
        
        # 点击添加申请人
        page1.get_by_text("添加").first.click()
        time.sleep(3)
        
        # 获取所有input信息
        inputs_info = page1.evaluate("""() => {
            const inputs = document.querySelectorAll('input');
            return Array.from(inputs).map(input => ({
                type: input.type,
                placeholder: input.placeholder,
                name: input.name,
                id: input.id,
                className: input.className
            }));
        }""")
        
        print("\n=== 所有input元素 ===")
        for info in inputs_info:
            if info['placeholder'] or info['name'] or info['id']:
                print(f"type={info['type']}, placeholder={info['placeholder']}, name={info['name']}, id={info['id']}")
        
        # 截图
        page1.screenshot(path="debug_inputs.png")
        print("\n截图已保存: debug_inputs.png")
    
    time.sleep(10)
    browser.close()
