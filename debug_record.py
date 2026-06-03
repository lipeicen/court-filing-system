from playwright.sync_api import sync_playwright
import time
import os

# 创建录像目录
video_dir = r"C:\court-auto-filing\videos"
os.makedirs(video_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        record_video_dir=video_dir,
        record_video_size={"width": 1280, "height": 720}
    )
    page = context.new_page()
    
    print("登录...")
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
    
    print("点击在线立案...")
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
        
        # 勾选阅读须知
        try:
            checkbox = page1.locator("input[type='checkbox']").first
            checkbox.click()
            time.sleep(0.5)
        except:
            pass
        
        # 点击创建保全申请
        page1.get_by_text("创建保全申请").click()
        time.sleep(3)
        
        # 选择法院
        page1.get_by_placeholder("请选择法院").click()
        time.sleep(1)
        page1.get_by_text("深圳市福田区人民法院").click()
        time.sleep(0.5)
        
        # 输入金额
        amount_input = page1.get_by_placeholder("请输入您要申请的保全金额")
        amount_input.click()
        amount_input.fill("500000")
        time.sleep(0.5)
        
        # 选择申请人类型
        page1.get_by_role("radio", name="法人").click()
        time.sleep(0.5)
        
        # 点击创建
        page1.get_by_role("button", name="创建保全").click()
        time.sleep(3)
        
        # 点击添加申请人
        page1.get_by_text("添加").first.click()
        time.sleep(3)
        
        # === 抓取元素信息 ===
        print("\n=== 申请人弹窗所有元素 ===")
        
        # 获取所有input
        inputs_info = page1.evaluate("""() => {
            const result = [];
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => {
                if (input.placeholder || input.name || input.id) {
                    result.push({
                        tag: 'INPUT',
                        type: input.type,
                        placeholder: input.placeholder,
                        name: input.name,
                        id: input.id,
                        value: input.value,
                        className: input.className
                    });
                }
            });
            return result;
        }""")
        
        for info in inputs_info:
            print(f"INPUT: type={info['type']}, placeholder='{info['placeholder']}', name='{info['name']}', id='{info['id']}'")
        
        # 获取所有可见文本
        all_texts = page1.evaluate("""() => {
            const result = [];
            const elements = document.querySelectorAll('*');
            elements.forEach(el => {
                if (el.children.length === 0 && el.textContent.trim()) {
                    result.push(el.textContent.trim());
                }
            });
            return result;
        }""")
        
        print("\n=== 所有文本标签 ===")
        for text in all_texts[:50]:
            print(f"  '{text}'")
        
        # 截图
        page1.screenshot(path=r"C:\court-auto-filing\debug_applicant.png")
        print("\n截图已保存: debug_applicant.png")
        
        # 保存HTML
        html = page1.content()
        with open(r"C:\court-auto-filing\debug_applicant.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML已保存: debug_applicant.html")
    
    print("\n等待30秒后关闭...")
    time.sleep(30)
    
    context.close()
    browser.close()
    
    # 列出录像文件
    videos = os.listdir(video_dir)
    print(f"\n录像文件: {videos}")
