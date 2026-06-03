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
    
    print("请手动输入验证码...")
    time.sleep(15)
    
    page.get_by_text("登录", exact=True).click()
    time.sleep(5)
    
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
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
        
        # 勾选并创建
        try:
            page1.locator("input[type='checkbox']").first.click()
            time.sleep(0.5)
        except:
            pass
        
        page1.get_by_text("创建保全申请").click()
        time.sleep(3)
        
        page1.get_by_placeholder("请选择法院").click()
        time.sleep(1)
        page1.get_by_text("深圳市福田区人民法院").click()
        time.sleep(0.5)
        
        page1.get_by_placeholder("请输入您要申请的保全金额").fill("500000")
        time.sleep(0.5)
        
        page1.get_by_role("radio", name="法人").click()
        time.sleep(0.5)
        
        page1.get_by_role("button", name="创建保全").click()
        time.sleep(3)
        
        # 点击添加申请人
        page1.get_by_text("添加").first.click()
        time.sleep(3)
        
        # 获取弹窗HTML
        html = page1.content()
        
        # 提取申请人弹窗部分
        start = html.find('addSQR')
        if start > 0:
            end = html.find('/uni-popup', start)
            if end > 0:
                popup_html = html[start-50:end+50]
                with open(r"C:\court-auto-filing\popup_html.txt", "w", encoding="utf-8") as f:
                    f.write(popup_html)
                print("弹窗HTML已保存到 popup_html.txt")
        
        # 获取所有input的完整信息
        inputs_detail = page1.evaluate("""() => {
            const result = [];
            const inputs = document.querySelectorAll('input');
            inputs.forEach((input, idx) => {
                const rect = input.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    // 找到最近的标签
                    let label = null;
                    let parent = input.parentElement;
                    for (let i = 0; i < 5; i++) {
                        if (!parent) break;
                        const labels = parent.querySelectorAll('.label, label, .uni-label, .form-item-label');
                        if (labels.length > 0) {
                            label = labels[0].textContent.trim();
                            break;
                        }
                        parent = parent.parentElement;
                    }
                    
                    result.push({
                        index: idx,
                        type: input.type,
                        placeholder: input.placeholder,
                        name: input.name,
                        id: input.id,
                        className: input.className,
                        label: label,
                        value: input.value,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    });
                }
            });
            return result;
        }""")
        
        print("\n=== 可见Input元素 ===")
        for info in inputs_detail:
            print(f"[{info['index']}] type={info['type']}, label='{info['label']}', placeholder='{info['placeholder']}', id='{info['id']}', class='{info['className']}', pos=({info['x']:.0f},{info['y']:.0f})")
        
        # 截图
        page1.screenshot(path=r"C:\court-auto-filing\debug_popup.png")
        print("\n截图: debug_popup.png")
    
    time.sleep(10)
    browser.close()
