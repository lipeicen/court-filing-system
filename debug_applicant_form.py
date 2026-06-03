from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = p.chromium.launch().new_page()
    
    # 登录
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login")
    time.sleep(3)
    page.click("text=律师用户")
    page.fill("input[type='text']", "13723715831")
    page.fill("input[type='password']", "HU1234pp")
    
    # 手动输入验证码
    captcha = input("请输入验证码: ")
    page.fill("input[placeholder='请输入验证码']", captcha)
    page.click("text=登录")
    time.sleep(3)
    
    # 进入保全页面
    page.click("text=在线立案")
    time.sleep(1)
    page.click("text=在线保全")
    time.sleep(3)
    
    # 获取新页面
    pages = browser.pages
    page1 = pages[-1] if len(pages) > 1 else page
    
    # 勾选阅读须知
    page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    time.sleep(1)
    
    # 点击创建保全申请
    page1.get_by_role("button", name="创建保全申请").click()
    time.sleep(2)
    
    # 选择法院
    court_input = page1.get_by_placeholder("选择申请法院")
    court_input.click()
    court_input.fill("广东")
    time.sleep(1)
    page1.get_by_text("广州市天河区人民法院").click()
    time.sleep(1)
    
    # 输入金额
    amount_input = page1.get_by_placeholder("请输入您要申请的保全金额")
    amount_input.click()
    amount_input.fill("300000")
    time.sleep(1)
    
    # 选择律师
    page1.get_by_role("radio", name="律师").click()
    time.sleep(1)
    
    # 点击创建保全
    page1.get_by_role("button", name="创建保全").click()
    time.sleep(3)
    
    # 点击添加申请人
    page1.get_by_text("添加").first.click()
    time.sleep(2)
    
    # 截图查看申请人表单
    page1.screenshot(path=r"C:\court-auto-filing\applicant_form.png")
    print("✓ 截图已保存")
    
    # 获取表单HTML
    html = page1.content()
    with open(r"C:\court-auto-filing\applicant_form.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ HTML已保存")
    
    browser.close()
