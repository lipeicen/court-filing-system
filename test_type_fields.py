
import time
import sys
sys.path.insert(0, r'C:\court-auto-filing')

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # 登录
    page.goto("https://zxfw.court.gov.cn")
    time.sleep(3)
    
    print("请手动登录...")
    print("登录完成后按Enter继续...")
    input()
    
    # 进入保全申请
    page.goto("https://zxfw.court.gov.cn/#/caseCenter/insurance")
    time.sleep(3)
    
    # 点击我要保全
    page.get_by_text("我要保全").click()
    time.sleep(2)
    
    # 点击申请保全
    page.get_by_text("申请保全").click()
    time.sleep(3)
    
    # 点击添加申请人
    page.get_by_text("添加").first.click()
    time.sleep(3)
    
    # 截图: 默认状态(自然人)
    page.screenshot(path=r'C:\court-auto-filing\test_applicant_自然人.png')
    print("已截图: test_applicant_自然人.png")
    
    # 选择法人
    page.get_by_role("radio", name="法人", exact=True).click()
    time.sleep(2)
    page.screenshot(path=r'C:\court-auto-filing\test_applicant_法人.png')
    print("已截图: test_applicant_法人.png")
    
    # 选择非法人组织
    page.get_by_role("radio", name="非法人组织", exact=True).click()
    time.sleep(2)
    page.screenshot(path=r'C:\court-auto-filing\test_applicant_非法人组织.png')
    print("已截图: test_applicant_非法人组织.png")
    
    # 关闭弹窗
    page.get_by_role("button", name="取 消").click()
    time.sleep(1)
    
    # 测试被申请人
    page.get_by_text("添加").nth(1).click()
    time.sleep(3)
    
    page.screenshot(path=r'C:\court-auto-filing\test_respondent_自然人.png')
    print("已截图: test_respondent_自然人.png")
    
    page.get_by_role("radio", name="法人", exact=True).click()
    time.sleep(2)
    page.screenshot(path=r'C:\court-auto-filing\test_respondent_法人.png')
    print("已截图: test_respondent_法人.png")
    
    page.get_by_role("radio", name="非法人组织", exact=True).click()
    time.sleep(2)
    page.screenshot(path=r'C:\court-auto-filing\test_respondent_非法人组织.png')
    print("已截图: test_respondent_非法人组织.png")
    
    print("\n全部截图完成，请对比字段差异")
    browser.close()
