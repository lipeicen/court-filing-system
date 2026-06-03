
import time
import subprocess
import sys

# 启动Flask服务
print("启动Flask服务...")
flask_process = subprocess.Popen(
    [sys.executable, r'C:\court-auto-filing\admin_app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=r'C:\court-auto-filing'
)

# 等待服务启动
time.sleep(3)

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    # 访问管理后台
    page.goto("http://localhost:5000/")
    time.sleep(2)
    page.screenshot(path=r'C:\court-auto-filing\test_admin_home.png')
    print("已截图首页: test_admin_home.png")
    
    # 点击添加案件（如果有这个按钮）
    try:
        page.get_by_text("添加案件").click()
        time.sleep(2)
        page.screenshot(path=r'C:\court-auto-filing\test_admin_add_case.png')
        print("已截图添加案件页: test_admin_add_case.png")
        
        # 填写测试数据 - 法人对非法人组织
        page.fill('input[name="case_no"]', '保全测试2026A')
        page.fill('input[name="case_name"]', '测试案件-法人对非法人组织')
        page.fill('input[name="preserve_amount"]', '100000')
        page.fill('input[name="court_name"]', '深圳市福田区人民法院')
        
        # 申请人 - 法人
        page.select_option('select[name="applicant_type"]', '法人')
        time.sleep(1)
        page.fill('input[name="applicant_name"]', '深圳测试科技有限公司')
        page.fill('input[name="applicant_uscc"]', '91440300MA5G123456')
        page.fill('input[name="applicant_legal_person"]', '张法人')
        page.fill('input[name="applicant_legal_title"]', '执行董事')
        page.fill('input[name="applicant_phone"]', '13800138001')
        page.fill('input[name="applicant_address"]', '深圳市福田区测试路1号')
        page.fill('input[name="applicant_reg_address"]', '深圳市福田区')
        
        # 被申请人 - 非法人组织
        page.select_option('select[name="respondent_type"]', '非法人组织')
        time.sleep(1)
        page.fill('input[name="respondent_name"]', '北京测试合伙企业')
        page.fill('input[name="respondent_uscc"]', '91110105MA5G901234')
        page.fill('input[name="respondent_legal_person"]', '李合伙人')
        page.fill('input[name="respondent_legal_title"]', '执行事务合伙人')
        page.fill('input[name="respondent_phone"]', '13900139001')
        page.fill('input[name="respondent_address"]', '北京市朝阳区测试路2号')
        page.fill('input[name="respondent_reg_address"]', '北京市朝阳区')
        
        page.screenshot(path=r'C:\court-auto-filing\test_admin_filled.png')
        print("已截图填写完成: test_admin_filled.png")
        
        # 提交
        page.get_by_role("button", name="保存").click()
        time.sleep(3)
        page.screenshot(path=r'C:\court-auto-filing\test_admin_result.png')
        print("已截图结果: test_admin_result.png")
        
    except Exception as e:
        print(f"操作失败: {e}")
        page.screenshot(path=r'C:\court-auto-filing\test_admin_error.png')
    
    browser.close()

# 关闭Flask服务
flask_process.terminate()
print("测试完成")
