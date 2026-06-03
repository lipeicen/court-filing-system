"""
法院自动立案系统 - 最终版本
基于 Playwright Codegen 录制结果优化
"""

from playwright.sync_api import sync_playwright, expect
import time
import re
import pymysql
import sys



CASE_DATA = {}

def get_db_connection():
    return pymysql.connect(
        host='localhost', user='root', password='lijiayu123',
        database='court_filing', charset='utf8mb4'
    )

def get_case_data(case_no):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM cases WHERE case_no = %s", (case_no,))
    case = cursor.fetchone()
    if not case:
        conn.close()
        return None
    cursor.execute("SELECT * FROM property_clues WHERE case_id = %s", (case['id'],))
    properties = cursor.fetchall()
    cursor.execute("SELECT * FROM case_files WHERE case_id = %s", (case['id'],))
    files = cursor.fetchall()
    cursor.execute("SELECT * FROM agents WHERE case_id = %s", (case['id'],))
    agents = cursor.fetchall()
    conn.close()
    case['properties'] = properties
    case['files'] = files
    case['agents'] = agents
    return case

def load_case_data(case_no):
    global CASE_DATA
    case = get_case_data(case_no)
    if not case:
        print(f"未找到案件: {case_no}")
        return False
    CASE_DATA = case
    print(f"案件数据加载成功: {case_no}")
    return True

def solve_captcha(page):
    """解决验证码"""
    import ddddocr
    
    # 找到验证码图片 - 尝试多种选择器
    captcha_img = None
    
    # 尝试不同的选择器
    selectors = [
        "img[mode='aspectFit']",
        "img.captcha",
        "img[src*='captcha']",
        "img[src*='verify']",
        "uni-image img",
        "img"
    ]
    
    for selector in selectors:
        try:
            img = page.locator(selector).first
            if img.is_visible():
                captcha_img = img
                print(f"找到验证码图片: {selector}")
                break
        except:
            continue
    
    if not captcha_img:
        print("未找到验证码图片，尝试截图查找...")
        # 截图查看页面
        page.screenshot(path="login_page.png")
        return None
    
    # 截图
    img_path = "captcha_codegen.png"
    captcha_img.screenshot(path=img_path)
    
    # OCR识别
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    
    result = ocr.classification(img_bytes)
    print(f"验证码识别结果: {result}")
    return result


def auto_login(page, max_retries=3):
    """自动登录 - 带重试机制"""
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    for attempt in range(max_retries):
        print(f"\n第 {attempt + 1} 次尝试...")
        
        # 进入登录页
        page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        time.sleep(2)
        
        # 选择律师用户
        print("选择律师用户...")
        page.get_by_text("律师用户").click()
        time.sleep(0.5)
        
        # 输入手机号
        print("输入手机号...")
        phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
        phone_input.click()
        phone_input.fill(CASE_DATA.get("agent_phone", "13723715831"))
        time.sleep(0.5)
        
        # 输入密码
        print("输入密码...")
        pwd_input = page.locator("input[type=\"password\"]")
        pwd_input.click()
        pwd_input.fill(CASE_DATA.get("agent_password", "HU1234pp"))
        time.sleep(0.5)
        
        # 识别并输入验证码
        print("识别验证码...")
        captcha_text = solve_captcha(page)
        if captcha_text:
            captcha_input = page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox")
            captcha_input.click()
            captcha_input.fill(captcha_text)
        time.sleep(0.5)
        
        # 点击登录
        print("点击登录...")
        page.get_by_text("登录", exact=True).click()
        
        # 等待登录成功
        try:
            page.wait_for_selector("text=在线立案", timeout=10000)
            print("登录成功!")
            return True
        except:
            print("登录失败，准备重试...")
            time.sleep(2)
            continue
    
    print(f"\n登录失败，已达到最大重试次数 ({max_retries})")
    return False
def create_preservation(page):
    """创建保全申请 - 数据库版本"""
    print("\n" + "=" * 50)
    print("开始创建保全申请")
    print(f"保全类别: {CASE_DATA.get('preserve_category', '诉前保全')}")
    print("=" * 50)
    
    # 点击在线立案
    print("点击在线立案...")
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    # 点击在线保全 - 关键：使用 expect_popup 等待新窗口
    print("点击在线保全...")
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    
    # 获取新页面
    page1 = page1_info.value
    print(f"新窗口已打开: {page1.url}")
    time.sleep(3)
    
    # 勾选阅读须知
    print("勾选阅读须知...")
    page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    time.sleep(0.5)
    
    # 点击创建保全申请
    print("点击创建保全申请...")
    page1.get_by_role("button", name="创建保全申请").click()
    time.sleep(2)
    
    # 选择申请法院
    court = CASE_DATA.get("court_name", "")
    print(f"选择申请法院: {court}...")
    try:
        court_input = page1.get_by_placeholder("选择申请法院")
        court_input.click()
        court_input.fill(court[:2])
    except:
        page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { if(input.placeholder && input.placeholder.includes('法院')) { input.click(); return; } } }")
    time.sleep(1)
    try:
        page1.get_by_text(court, exact=True).click()
    except:
        page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div'); for(let item of items) {{ if(item.textContent.includes('{court}')) {{ item.click(); return; }} }} }}")
    time.sleep(0.5)
    
    # 输入保全金额
    print("输入保全金额...")
    amount_input = page1.get_by_placeholder("请输入您要申请的保全金额")
    amount_input.click()
    amount_input.fill(str(CASE_DATA.get("preserve_amount", 0)))
    time.sleep(0.5)
    
    # 选择申请人类型
    print("选择申请人类型...")
    page1.get_by_role("radio", name="律师").click()
    time.sleep(0.5)
    
    # 点击创建保全
    print("点击创建保全...")
    page1.get_by_role("button", name="创建保全").click()
    time.sleep(3)
    
    print("保全申请创建成功!")
    return page1


def add_applicant(page1):
    """添加申请人 - 数据驱动版本"""
    print("\n" + "=" * 50)
    print("添加申请人")
    print("=" * 50)
    
    applicant_type = CASE_DATA.get('applicant_type', '自然人')
    print(f"申请人类型: {applicant_type}")
    
    # 点击添加
    print("点击添加申请人...")
    page1.get_by_text("添加").first.click()
    time.sleep(2)
    
    if applicant_type == '自然人':
        page1.get_by_role("radio", name="自然人", exact=True).click()
        time.sleep(0.5)
        
        name = CASE_DATA.get('applicant_name', '')
        print(f"输入姓名: {name}...")
        name_input = page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox")
        name_input.click()
        name_input.fill(name)
        time.sleep(0.5)
        
        cert_no = CASE_DATA.get('applicant_cert_no', '')
        print("输入身份证号...")
        id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
        id_input.click()
        id_input.fill(cert_no)
        time.sleep(0.5)
        
        gender = CASE_DATA.get('applicant_gender', '男性')
        print(f"选择性别: {gender}...")
        page1.get_by_role("radio", name=gender, exact=True).click()
        time.sleep(0.5)
        
        phone = CASE_DATA.get('applicant_phone', '')
        print("输入手机号...")
        phone_input = page1.locator("#addSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
        phone_input.click()
        phone_input.fill(phone)
        time.sleep(0.5)
        
        address = CASE_DATA.get('applicant_address', '')
        print("输入地址...")
        addr_input = page1.locator("div").filter(has_text=re.compile(r"^经常居住地$")).get_by_role("textbox")
        addr_input.click()
        addr_input.fill(address)
        time.sleep(0.5)
    
    elif applicant_type == '法人':
        page1.get_by_role("radio", name="法人", exact=True).click()
        time.sleep(2)
        
        name = CASE_DATA.get('applicant_name', '')
        print(f"输入单位名称: {name}...")
        try:
            page1.get_by_placeholder("请输入单位名称").fill(name)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('单位名称')) {{ input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('applicant_legal_person', '')
        print("输入法定代表人...")
        try:
            page1.get_by_placeholder("请输入法定代表人").fill(legal)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('法定代表人')) {{ input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('applicant_uscc', '')
        print("输入统一社会信用代码...")
        try:
            page1.get_by_placeholder("请输入统一社会信用代码").fill(credit)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('信用代码')) {{ input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('applicant_phone', '')
        print("输入手机号...")
        try:
            page1.get_by_placeholder("请输入手机号码").fill(phone)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('手机号码')) {{ input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
    
    elif applicant_type == '非法人组织':
        page1.get_by_role("radio", name="非法人组织", exact=True).click()
        time.sleep(2)
        
        name = CASE_DATA.get('applicant_name', '')
        print(f"输入单位名称: {name}...")
        try:
            page1.get_by_placeholder("请输入单位名称").fill(name)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('单位名称')) {{ input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('applicant_legal_person', '')
        print("输入法定代表人...")
        try:
            page1.get_by_placeholder("请输入法定代表人").fill(legal)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('法定代表人')) {{ input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('applicant_uscc', '')
        print("输入统一社会信用代码...")
        try:
            page1.get_by_placeholder("请输入统一社会信用代码").fill(credit)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('信用代码')) {{ input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('applicant_phone', '')
        print("输入手机号...")
        try:
            page1.get_by_placeholder("请输入手机号码").fill(phone)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('手机号码')) {{ input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
    
    print("保存申请人...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("申请人添加成功!")


def add_respondent(page1):
    """添加被申请人 - 数据驱动版本"""
    print("\n" + "=" * 50)
    print("添加被申请人")
    print("=" * 50)
    
    respondent_type = CASE_DATA.get('respondent_type', '自然人')
    print(f"被申请人类型: {respondent_type}")
    
    # 点击添加（第二个添加按钮）
    print("点击添加被申请人...")
    try:
        page1.get_by_text("添加").nth(1).click()
    except:
        page1.evaluate("() => { const spans = document.querySelectorAll('span'); let count = 0; for(let s of spans) { if(s.textContent.trim() === '添加') { count++; if(count === 2) { s.click(); return; } } } }")
    time.sleep(2)
    
    if respondent_type == '自然人':
        try:
            page1.locator("#addBSQR").get_by_role("radio", name="自然人", exact=True).click()
        except:
            page1.evaluate("() => { const radios = document.querySelectorAll('#addBSQR [role=radio], #addBSQR input[type=radio]'); for(let r of radios) { if(r.textContent.includes('自然人') || r.nextElementSibling?.textContent.includes('自然人')) { r.click(); return; } } }")
        time.sleep(0.5)
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入姓名: {name}...")
        name_input = page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox")
        name_input.click()
        name_input.fill(name)
        time.sleep(0.5)
        
        cert_no = CASE_DATA.get('respondent_id', '')
        print("输入身份证号...")
        id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
        id_input.click()
        id_input.fill(cert_no)
        time.sleep(0.5)
        
        gender = CASE_DATA.get('respondent_gender', '男性')
        print(f"选择性别: {gender}...")
        try:
            page1.locator("#addBSQR").get_by_role("radio", name=gender, exact=True).click()
        except:
            page1.evaluate(f"() => {{ const radios = document.querySelectorAll('#addBSQR [role=radio], #addBSQR input[type=radio]'); for(let r of radios) {{ const text = r.textContent || r.nextElementSibling?.textContent || ''; if(text.includes('{gender}')) {{ r.click(); return; }} }} }}")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('respondent_phone', '')
        print("输入手机号...")
        phone_input = page1.locator("#addBSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
        phone_input.click()
        phone_input.fill(phone)
        time.sleep(0.5)
    
    elif respondent_type == '法人':
        try:
            page1.locator("#addBSQR").get_by_role("radio", name="法人", exact=True).click()
        except:
            page1.evaluate("() => { const radios = document.querySelectorAll('#addBSQR [role=radio], #addBSQR input[type=radio]'); for(let r of radios) { const text = r.textContent || r.nextElementSibling?.textContent || ''; if(text.includes('法人') && !text.includes('非法人')) { r.click(); return; } } }")
        time.sleep(2)
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入单位名称: {name}...")
        try:
            page1.get_by_placeholder("请输入单位名称").fill(name)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('单位名称')) {{ input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('respondent_legal_person', '')
        print("输入法定代表人...")
        try:
            page1.get_by_placeholder("请输入法定代表人").fill(legal)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('法定代表人')) {{ input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('respondent_uscc', '')
        print("输入统一社会信用代码...")
        try:
            page1.get_by_placeholder("请输入统一社会信用代码").fill(credit)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('信用代码')) {{ input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
    
    elif respondent_type == '非法人组织':
        try:
            page1.locator("#addBSQR").get_by_role("radio", name="非法人组织", exact=True).click()
        except:
            page1.evaluate("() => { const radios = document.querySelectorAll('#addBSQR [role=radio], #addBSQR input[type=radio]'); for(let r of radios) { const text = r.textContent || r.nextElementSibling?.textContent || ''; if(text.includes('非法人组织')) { r.click(); return; } } }")
        time.sleep(2)
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入单位名称: {name}...")
        try:
            page1.get_by_placeholder("请输入单位名称").fill(name)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('单位名称')) {{ input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('respondent_legal_person', '')
        print("输入法定代表人...")
        try:
            page1.get_by_placeholder("请输入法定代表人").fill(legal)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('法定代表人')) {{ input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('respondent_uscc', '')
        print("输入统一社会信用代码...")
        try:
            page1.get_by_placeholder("请输入统一社会信用代码").fill(credit)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('信用代码')) {{ input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
        time.sleep(0.5)
    
    print("保存被申请人...")
    try:
        page1.locator("#addBSQR").get_by_role("button", name="保存").click()
    except:
        page1.evaluate("() => { const btns = document.querySelectorAll('#addBSQR button'); for(let b of btns) { if(b.textContent.includes('保存')) { b.click(); return; } } }")
    time.sleep(2)
    
    print("被申请人添加成功!")


def add_property(page1):
    """添加财产线索 - 数据驱动版本"""
    print("\n" + "=" * 50)
    print("添加财产线索")
    print("=" * 50)
    
    property_type = CASE_DATA.get('property_type', '存款')
    print(f"财产类型: {property_type}")
    
    # 点击添加
    print("点击添加财产...")
    try:
        page1.locator("span").filter(has_text=re.compile(r"^添加$")).click()
    except:
        page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { s.click(); return; } } }")
    time.sleep(2)
    
    # 选择财产类型
    print(f"选择财产类型: {property_type}...")
    try:
        page1.get_by_placeholder("请选择财产类型").click()
        time.sleep(1)
        page1.get_by_text(property_type, exact=True).click()
    except:
        try:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div'); for(let item of items) {{ if(item.textContent.trim() === '{property_type}') {{ item.click(); return; }} }} }}")
        except:
            pass
    time.sleep(0.5)
    
    # 选择财产所有人
    owner = CASE_DATA.get('property_owner', '') or CASE_DATA.get('respondent_name', '')
    print(f"选择财产所有人: {owner}...")
    try:
        page1.get_by_placeholder("请选择财产所有人").click()
        time.sleep(1)
        page1.get_by_text(owner).first.click()
    except:
        page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div'); for(let item of items) {{ if(item.textContent.includes('{owner}')) {{ item.click(); return; }} }} }}")
    time.sleep(0.5)
    
    if property_type == '房产':
        print("输入房产信息...")
        province = CASE_DATA.get('property_province', '')
        if province:
            try:
                page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { let p = input.parentElement; for(let i=0; i<8; i++) { if(!p) break; if(p.textContent.includes('房产坐落') && input.readOnly) { input.click(); return; } p = p.parentElement; } } }")
                time.sleep(1)
                page1.get_by_text(province, exact=True).click()
                time.sleep(0.5)
            except Exception as e:
                print(f"  省份选择失败: {e}")
        
        detail = CASE_DATA.get('property_detail_location', '') or CASE_DATA.get('property_location', '')
        if detail:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('房产坐落') && !input.readOnly) {{ input.value = '{detail}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  详细地址输入失败: {e}")
        
        cert_no = CASE_DATA.get('property_cert_no', '')
        if cert_no:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('房产证号') && !input.readOnly) {{ input.value = '{cert_no}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  房产证号输入失败: {e}")
    
    elif property_type == '股权':
        print("输入股权信息...")
        reg_location = CASE_DATA.get('stock_reg_location', '')
        if reg_location:
            try:
                page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { let p = input.parentElement; for(let i=0; i<8; i++) { if(!p) break; if(p.textContent.includes('注册地') && input.readOnly) { input.click(); return; } p = p.parentElement; } } }")
                time.sleep(1)
                page1.get_by_text(reg_location, exact=True).click()
                time.sleep(0.5)
            except Exception as e:
                print(f"  注册地选择失败: {e}")
        
        company = CASE_DATA.get('stock_company_name', '') or CASE_DATA.get('invested_company', '')
        if company:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('持股公司') && !input.readOnly) {{ input.value = '{company}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  持股公司输入失败: {e}")
        
        ratio = CASE_DATA.get('stock_ratio', '')
        if ratio:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('出资比例') && !input.readOnly) {{ input.value = '{ratio}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  出资比例输入失败: {e}")
    
    elif property_type == '车辆':
        print("输入车辆信息...")
        brand = CASE_DATA.get('vehicle_brand_model', '')
        if brand:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('车辆品牌') && !input.readOnly) {{ input.value = '{brand}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  车辆品牌输入失败: {e}")
        
        plate = CASE_DATA.get('vehicle_plate_no', '')
        if plate:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('车牌号') && !input.readOnly) {{ input.value = '{plate}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  车牌号输入失败: {e}")
    
    elif property_type == '股票':
        print("输入股票信息...")
        account = CASE_DATA.get('stock_account', '')
        if account:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('证券账户') && !input.readOnly) {{ input.value = '{account}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  证券账户输入失败: {e}")
        
        code = CASE_DATA.get('stock_code', '')
        if code:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('股票代码') && !input.readOnly) {{ input.value = '{code}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  股票代码输入失败: {e}")
        
        quantity = CASE_DATA.get('stock_quantity', '')
        if quantity:
            try:
                page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('持股数量') && !input.readOnly) {{ input.value = '{quantity}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  持股数量输入失败: {e}")
    
    else:
        # 银行存款（默认）
        print("输入银行存款信息...")
        location = CASE_DATA.get('property_location', '')
        if location:
            try:
                location_input = page1.locator("div").filter(has_text=re.compile(r"^开户行所在地")).get_by_role("textbox")
                location_input.click()
                time.sleep(1)
                page1.get_by_text(location[:2], exact=True).click()
                time.sleep(0.5)
            except Exception as e:
                print(f"  开户行所在地选择失败: {e}")
        
        bank = CASE_DATA.get('property_bank_name', '')
        if bank:
            try:
                bank_input = page1.locator("div").filter(has_text=re.compile(r"^开户银行名称$")).get_by_role("textbox")
                bank_input.click()
                bank_input.fill(bank)
                time.sleep(0.5)
            except Exception as e:
                print(f"  开户银行输入失败: {e}")
        
        account = CASE_DATA.get('property_bank_account', '')
        if account:
            try:
                account_input = page1.locator("div").filter(has_text=re.compile(r"^开户账号$")).get_by_role("textbox")
                account_input.click()
                account_input.fill(account)
                time.sleep(0.5)
            except Exception as e:
                print(f"  开户账号输入失败: {e}")
    
    # 输入数额（通用）
    amount = str(CASE_DATA.get('preserve_amount', 0))
    print(f"输入数额: {amount}...")
    try:
        amount_input = page1.locator("div").filter(has_text=re.compile(r"^数额$")).get_by_role("textbox")
        amount_input.click()
        amount_input.fill(amount)
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('数额') && !input.readOnly && input.type === 'text') {{ input.value = '{amount}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
    time.sleep(0.5)
    
    # 选择币种（通用）
    print("选择币种...")
    try:
        page1.get_by_placeholder("请选择单位").click()
        time.sleep(1)
        page1.locator("li").filter(has_text="人民币").click()
    except:
        print("  币种选择失败，跳过")
    time.sleep(0.5)
    
    # 输入财产价值（通用）
    value = str(CASE_DATA.get('property_value', CASE_DATA.get('preserve_amount', 0)))
    print(f"输入财产价值: {value}...")
    try:
        value_input = page1.locator("form div").filter(has_text="财产价值￥ 元").get_by_role("textbox")
        value_input.click()
        value_input.fill(value)
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('财产价值') && !input.readOnly) {{ input.value = '{value}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
    time.sleep(0.5)
    
    # 保存
    print("保存财产线索...")
    page1.get_by_role("button", name="保存", exact=True).click()
    time.sleep(2)
    
    print("财产线索添加成功!")


def add_guarantee(page1):
    """添加担保信息 - 数据驱动版本"""
    print("\n" + "=" * 50)
    print("添加担保信息")
    print("=" * 50)
    
    guarantee_type = CASE_DATA.get('guarantee_type', '提供保证人')
    print(f"担保方式: {guarantee_type}")
    
    # 点击下一步
    print("点击下一步...")
    try:
        page1.get_by_role("button", name="下一步").click()
    except:
        try:
            page1.evaluate("() => { const btns = document.querySelectorAll('button, uni-button'); for(let btn of btns) { if(btn.textContent && btn.textContent.includes('下一步')) { btn.click(); return true; } } return false; }")
        except:
            print("  下一步按钮未找到，跳过")
            return
    time.sleep(2)
    
    # 点击添加
    print("点击添加担保...")
    try:
        page1.locator("span").filter(has_text="添加").locator("i").click()
    except:
        page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { s.click(); return; } } }")
    time.sleep(2)
    
    # 选择担保方式
    print(f"选择担保方式: {guarantee_type}...")
    try:
        page1.get_by_placeholder("请选择").click()
        time.sleep(1)
        page1.get_by_text(guarantee_type).first.click()
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder === '请选择') {{ input.click(); return; }} }} }}")
        time.sleep(1)
        page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div'); for(let item of items) {{ if(item.textContent.includes('{guarantee_type}')) {{ item.click(); return; }} }} }}")
    time.sleep(0.5)
    
    # 输入担保人
    guarantor = CASE_DATA.get('guarantor_name', '') or CASE_DATA.get('applicant_name', '')
    print(f"输入担保人: {guarantor}...")
    try:
        guarantor_input = page1.get_by_placeholder("请输入担保人")
        guarantor_input.click()
        guarantor_input.fill(guarantor)
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('担保人') && !input.readOnly) {{ input.value = '{guarantor}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
    time.sleep(0.5)
    
    # 输入担保物名称
    guarantee_object = CASE_DATA.get('guarantee_property_name', '') or CASE_DATA.get('guarantee_object', '')
    if guarantee_object:
        print(f"输入担保物名称: {guarantee_object}...")
        try:
            name_input = page1.get_by_placeholder("请输入担保名称")
            name_input.click()
            name_input.fill(guarantee_object)
        except:
            page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('担保名称') && !input.readOnly) {{ input.value = '{guarantee_object}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
        time.sleep(0.5)
    
    # 输入担保价值
    value = str(CASE_DATA.get('guarantee_value', CASE_DATA.get('preserve_amount', 0)))
    print(f"输入担保价值: {value}...")
    try:
        value_input = page1.locator("#addDBXX div").filter(has_text="担保价值 元").get_by_role("textbox")
        value_input.click()
        value_input.fill(value)
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ let p = input.parentElement; for(let i=0; i<8; i++) {{ if(!p) break; if(p.textContent.includes('担保价值') && !input.readOnly) {{ input.value = '{value}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} p = p.parentElement; }} }} }}")
    time.sleep(0.5)
    
    # 保存
    print("保存担保信息...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("担保信息添加成功!")


def main():
    """主函数"""
    import sys
    
    # 获取命令行参数
    case_no = None
    if len(sys.argv) > 1:
        case_no = sys.argv[1]
    
    # 加载案件数据
    if case_no:
        if not load_case_data(case_no):
            print(f"无法加载案件: {case_no}")
            return
    else:
        # 使用默认案件
        print("未指定案件编号，使用默认案件...")
        if not load_case_data('保全2026001'):
            print("默认案件加载失败")
            return
    
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 数据库版本")
    print("=" * 60)
    print(f"案件: {CASE_DATA['case_name']} ({CASE_DATA['case_no']})")
    print(f"申请人: {CASE_DATA['applicant_name']}")
    print(f"被申请人: {CASE_DATA['respondent_name']}")
    print(f"保全金额: {CASE_DATA['preserve_amount']}")
    print("=" * 60 + "\n")
    
    with sync_playwright() as p:
        # 启动浏览器
        print("启动浏览器...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录
            if not auto_login(page):
                print("登录失败，退出")
                return
            
            # 2. 创建保全申请
            page1 = create_preservation(page)
            
            # 3. 添加申请人
            add_applicant(page1)
            
            # 4. 添加被申请人
            add_respondent(page1)
            
            # 5. 添加财产线索
            add_property(page1)
            
            # 6. 添加担保信息
            add_guarantee(page1)
            
            # 7. 点击下一步进入材料上传页面
            print("\n" + "=" * 60)
            print("进入材料上传页面")
            print("=" * 60)
            page1.get_by_role("button", name="下一步").click()
            time.sleep(5)
            
            # 8. 按文件夹名匹配上传文件
            import os
            # 支持从命令行参数指定案件目录，默认使用保全2026001
            import sys
            if len(sys.argv) > 1:
                case_name = sys.argv[1]
                upload_dir = os.path.join(r"C:\court-auto-filing\uploads", case_name)
            else:
                upload_dir = r"C:\court-auto-filing\uploads\保全2026001"
            
            print(f"使用案件目录: {upload_dir}")
            
            print("\n" + "=" * 60)
            print("开始按文件夹名匹配上传")
            print("=" * 60)
            
            # 获取本地文件夹映射
            folder_mapping = {}
            for folder_name in os.listdir(upload_dir):
                folder_path = os.path.join(upload_dir, folder_name)
                if os.path.isdir(folder_path):
                    files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
                    folder_mapping[folder_name] = {
                        'path': folder_path,
                        'files': files
                    }
            
            print(f"本地文件夹: {list(folder_mapping.keys())}")
            
            # 获取页面文本
            page_text = page1.evaluate("() => document.body.innerText")
            
            # 获取所有文件input
            all_inputs = page1.locator("input[type='file']").all()
            print(f"页面共有 {len(all_inputs)} 个文件input")
            
            # 遍历每个文件夹
            for folder_name, info in folder_mapping.items():
                print(f"\n{'='*50}")
                print(f"【{folder_name}】")
                print(f"{'='*50}")
                
                if folder_name not in page_text:
                    print(f"页面上未找到: {folder_name}")
                    continue
                
                print(f"找到 {len(info['files'])} 个文件")
                
                for file_name in info['files']:
                    file_path = os.path.join(info['path'], file_name)
                    print(f"\n  上传: {file_name}")
                    
                    uploaded = False
                    
                    # 策略1: 通过content属性匹配
                    try:
                        upload_demo = page1.locator(f'[content="{folder_name}"]').first
                        if upload_demo.count() > 0:
                            inp = upload_demo.locator("input[type='file']").first
                            if inp.count() > 0:
                                inp.set_input_files(file_path)
                                print(f"    ✓ content匹配上传成功")
                                uploaded = True
                                time.sleep(2)
                                continue
                    except:
                        pass
                    
                    # 策略1.5: 证据材料特殊处理 - 通过文本内容查找上传区域
                    if not uploaded and "证据" in folder_name:
                        try:
                            # 方法1: 使用JavaScript查找包含"证据材料"的upload-demo区域
                            input_idx = page1.evaluate("""() => {
                                // 查找所有包含"证据材料"文本的元素
                                const allElements = document.querySelectorAll('*');
                                for (let el of allElements) {
                                    if (el.textContent && el.textContent.includes('证据材料') && el.children.length < 5) {
                                        // 向上查找包含file input的父元素
                                        let parent = el;
                                        for (let i = 0; i < 10; i++) {
                                            if (!parent) break;
                                            const input = parent.querySelector('input[type="file"]');
                                            if (input) {
                                                return Array.from(document.querySelectorAll('input[type="file"]')).indexOf(input);
                                            }
                                            parent = parent.parentElement;
                                        }
                                    }
                                }
                                return -1;
                            }""")
                            
                            if input_idx >= 0 and input_idx < len(all_inputs):
                                all_inputs[input_idx].set_input_files(file_path)
                                print(f"    ✓ 证据材料JS匹配上传成功")
                                uploaded = True
                                time.sleep(2)
                                continue
                            
                            # 方法2: 使用Playwright的locator
                            evidence_section = page1.locator("text=证据材料").first
                            if evidence_section.count() > 0:
                                # 获取元素的句柄，然后查找父元素
                                handle = evidence_section.element_handle()
                                if handle:
                                    parent = handle.evaluate_handle("""el => {
                                        let parent = el;
                                        for (let i = 0; i < 10; i++) {
                                            if (!parent) return null;
                                            const input = parent.querySelector('input[type="file"]');
                                            if (input) return parent;
                                            parent = parent.parentElement;
                                        }
                                        return null;
                                    }""")
                                    if parent:
                                        inp = parent.query_selector("input[type='file']")
                                        if inp:
                                            inp.set_input_files(file_path)
                                            print(f"    ✓ 证据材料区域匹配上传成功")
                                            uploaded = True
                                            time.sleep(2)
                                            continue
                        except Exception as e:
                            print(f"    证据材料区域匹配失败: {e}")
                    
                    # 策略2: 带子项区域
                    if not uploaded:
                        try:
                            target_subitem = None
                            if "申请人" in file_name and "被申请人" not in file_name:
                                target_subitem = "申请人"
                            elif "被申请人" in file_name:
                                target_subitem = "被申请人"
                            elif "代理人" in file_name:
                                target_subitem = "申请人"
                            elif "担保" in file_name or "保证人" in file_name:
                                target_subitem = "保证人"
                            elif "证据" in file_name:
                                target_subitem = "证据材料"
                            
                            if target_subitem:
                                print(f"    目标子项: {target_subitem}")
                                
                                subitem_buttons = page1.locator(".fd-upload-item-name").all()
                                for btn in subitem_buttons:
                                    try:
                                        btn_text = btn.inner_text()
                                        if target_subitem in btn_text:
                                            print(f"    找到子项: {btn_text}")
                                            
                                            input_idx = page1.evaluate(f"""() => {{
                                                const buttons = document.querySelectorAll('.fd-upload-item-name');
                                                for (let i = 0; i < buttons.length; i++) {{
                                                    if (buttons[i].textContent.includes('{target_subitem}')) {{
                                                        const parent = buttons[i].closest('.upload-demo, .el-upload');
                                                        if (parent) {{
                                                            const input = parent.querySelector('input[type="file"]');
                                                            if (input) {{
                                                                return Array.from(document.querySelectorAll('input[type="file"]')).indexOf(input);
                                                            }}
                                                        }}
                                                    }}
                                                }}
                                                return -1;
                                            }}""")
                                            
                                            if input_idx >= 0 and input_idx < len(all_inputs):
                                                all_inputs[input_idx].set_input_files(file_path)
                                                print(f"    ✓ 子项上传成功")
                                                uploaded = True
                                                time.sleep(2)
                                            break
                                    except:
                                        continue
                        except Exception as e:
                            print(f"    子项匹配失败: {e}")
                    
                    # 策略3: 遍历所有input
                    if not uploaded:
                        for i, inp in enumerate(all_inputs):
                            try:
                                inp.set_input_files(file_path)
                                print(f"    ✓ input[{i}]上传成功")
                                uploaded = True
                                time.sleep(2)
                                break
                            except:
                                continue
                    
                    if not uploaded:
                        print(f"    ✗ 上传失败")
            
            # 9. 完成
            print("\n" + "=" * 60)
            print("保全申请流程完成（含文件上传）!")
            print("=" * 60)
            
            # 等待用户查看
            print("\n等待30秒供查看结果...")
            time.sleep(30)
            
        except Exception as e:
            print(f"\n发生错误: {e}")
            import traceback
            traceback.print_exc()
            
            # 出错时保持浏览器打开
            print("\n发生错误，保持浏览器打开供检查...")
            time.sleep(60)
            
        finally:
            # 关闭浏览器
            print("\n关闭浏览器...")
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
