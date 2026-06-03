
import pymysql
from playwright.sync_api import sync_playwright
import time
import re

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lijiayu123',
    'database': 'court_filing',
    'charset': 'utf8mb4'
}

def get_case_data(case_no):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM cases WHERE case_no = %s", (case_no,))
    case = cursor.fetchone()
    conn.close()
    return case

# 测试非法人组织案件
case = get_case_data('保全2026006')
print(f"案件: {case['case_no']}")
print(f"被申请人: {case['respondent_name']}")
print(f"被申请人类型: {case['respondent_type']}")
print(f"被申请人性质: {case['respondent_nature']}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 打开法院网站
    page.goto("https://zxfw.court.gov.cn/")
    print("已打开法院网站")
    
    # 等待页面加载
    time.sleep(3)
    
    # 尝试自动登录（如果有保存的登录状态）
    # 或者等待手动登录
    print("请手动登录，然后按Enter继续...")
    print("等待60秒用于登录...")
    time.sleep(60)
    
    # 尝试导航到保全申请
    print("尝试导航到保全申请页面...")
    # 这里需要根据实际情况点击菜单
    
    # 测试被申请人添加
    respondent_type = case['respondent_type']
    print(f"\n测试被申请人类型: {respondent_type}")
    
    # 点击添加被申请人
    try:
        page.get_by_text("添加").nth(1).click(force=True)
        print("点击添加被申请人")
    except Exception as e:
        print(f"点击失败: {e}")
    
    time.sleep(2)
    
    # 选择被申请人类型
    if respondent_type == '法人':
        page.get_by_role("radio", name="法人", exact=True).click()
        print("已选择: 法人")
    elif respondent_type == '非法人组织':
        page.get_by_role("radio", name="非法人组织", exact=True).click()
        print("已选择: 非法人组织")
    else:
        page.get_by_role("radio", name="自然人", exact=True).click()
        print("已选择: 自然人")
    
    time.sleep(2)
    print("\n请检查页面显示...")
    print("等待30秒后关闭...")
    time.sleep(30)
    
    context.close()
    browser.close()
