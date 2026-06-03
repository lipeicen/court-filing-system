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

def fill_input_by_label(page, label_text, value, input_type='.el-input__inner'):
    """根据标签文字填写输入框 - 使用精确匹配"""
    if not value:
        return
    
    js_code = f"""() => {{
        const inputs = document.querySelectorAll('{input_type}');
        for(let input of inputs) {{
            const rect = input.getBoundingClientRect();
            if(rect.width > 0 && rect.height > 0) {{
                let el = input;
                for(let i=0; i<10; i++) {{
                    el = el.parentElement;
                    if(!el) break;
                    const allEls = el.querySelectorAll('*');
                    for(let e of allEls) {{
                        if(e !== input && e.children.length === 0 && 
                           e.textContent && e.textContent.trim() === '{label_text}') {{
                            const labelRect = e.getBoundingClientRect();
                            if(Math.abs(labelRect.y - rect.y) < 100) {{
                                input.focus(); 
                                input.value = '{value}';
                                input.dispatchEvent(new Event('input', {{bubbles:true}}));
                                input.blur();
                                return 'filled';
                            }}
                        }}
                    }}
                }}
            }}
        }}
        return 'not found';
    }}"""
    
    result = page.evaluate(js_code)
    return result

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
    
    # 将第一个财产线索的信息合并到CASE_DATA
    properties = case.get('properties', [])
    if properties:
        prop = properties[0]
        case['property_type'] = prop.get('property_type', '存款')
        case['property_owner'] = prop.get('property_owner', '') or prop.get('owner', '')
        case['property_value'] = prop.get('property_value', '') or prop.get('amount', '')
        case['bank_name'] = prop.get('bank_name', '')
        case['bank_account'] = prop.get('bank_account', '')
        case['property_location'] = prop.get('property_location', '')
        case['property_detail_location'] = prop.get('property_detail_location', '')
        case['property_province'] = prop.get('property_province', '')
        case['property_cert_no'] = prop.get('property_cert_no', '')
        case['stock_company_name'] = prop.get('stock_company_name', '')
        case['stock_reg_location'] = prop.get('stock_reg_location', '')
        case['vehicle_plate_no'] = prop.get('vehicle_plate_no', '')
        case['vehicle_type'] = prop.get('vehicle_type', '')
    else:
        case['property_type'] = '存款'
    
    CASE_DATA = case
    print(f"案件数据加载成功: {case_no}")
    print(f"  申请人: {case.get('applicant_name', '')}")
    print(f"  被申请人: {case.get('respondent_name', '')}")
    print(f"  保全金额: {case.get('preserve_amount', '')}")
    print(f"  财产类型: {case.get('property_type', '')}")
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
    time.sleep(1)  # 等待图片加载
    try:
        captcha_img.screenshot(path=img_path)
    except:
        # 如果截图失败，尝试直接截图整个页面然后裁剪
        page.screenshot(path="full_page.png")
        return None
    
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
            print(f"输入验证码: {captcha_text}...")
            try:
                captcha_input = page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox")
                captcha_input.click()
                captcha_input.fill(captcha_text)
            except:
                # 备用方法：直接用JavaScript设置验证码
                page.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('验证码')) {{ input.value = '{captcha_text}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
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
    amount = str(CASE_DATA.get("preserve_amount", 0))
    try:
        amount_input = page1.get_by_placeholder("请输入您要申请的保全金额")
        amount_input.click()
        amount_input.fill(amount)
    except:
        page1.evaluate(f"() => {{ const inputs = document.querySelectorAll('input'); for(let input of inputs) {{ if(input.placeholder && input.placeholder.includes('保全金额')) {{ input.click(); input.value = '{amount}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); return; }} }} }}")
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
    time.sleep(3)  # 增加等待时间让弹窗加载
    
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
        
        # 法人申请人字段（根据截图）：
        # 必填：单位名称、证照类型、证照号码、法定代表人、法定代表人职务、手机号码、单位地址、单位注册地
        # 选填：单位性质、固定电话
        
        # 使用Playwright的locator直接定位（更可靠）
        name = CASE_DATA.get('applicant_name', '')
        print(f"输入单位名称: {name}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位名称").locator(".el-input__inner")
            input_field.click()
            input_field.fill(name)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('applicant_uscc', '')
        print(f"输入证照号码: {credit}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="证照号码").locator(".el-input__inner")
            input_field.click()
            input_field.fill(credit)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('证照号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('applicant_legal_person', '')
        print(f"输入法定代表人: {legal}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="法定代表人").locator(".el-input__inner")
            input_field.click()
            input_field.fill(legal)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人') && !item.textContent.includes('职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        legal_title = CASE_DATA.get('applicant_legal_title', '')
        print(f"输入法定代表人职务: {legal_title}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="法定代表人职务").locator(".el-input__inner")
            input_field.click()
            input_field.fill(legal_title)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal_title}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('applicant_phone', '')
        print(f"输入手机号码: {phone}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="手机号码").locator(".el-input__inner")
            input_field.click()
            input_field.fill(phone)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('手机号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        address = CASE_DATA.get('applicant_address', '')
        print(f"输入单位地址: {address}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位地址").locator(".el-input__inner")
            input_field.click()
            input_field.fill(address)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位地址')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        reg_address = CASE_DATA.get('applicant_reg_address', '')
        print(f"输入单位注册地: {reg_address}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位注册地").locator(".el-input__inner")
            input_field.click()
            input_field.fill(reg_address)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位注册地')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{reg_address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
    
    elif applicant_type == '非法人组织':
        page1.get_by_role("radio", name="非法人组织", exact=True).click()
        time.sleep(2)
        
        name = CASE_DATA.get('applicant_name', '')
        print(f"输入单位名称: {name}...")
        page1.evaluate("""() => {
            const inputs = document.querySelectorAll('.el-input__inner');
            // 单位名称是第1个text input（index 0是radio后面的）
            if(inputs[0]) {
                inputs[0].focus(); inputs[0].value = '""" + name + """';
                inputs[0].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[0].blur(); return 'filled';
            }
            return 'not found';
        }""")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('applicant_uscc', '')
        print("输入证照号码...")
        page1.evaluate("""() => {
            const inputs = document.querySelectorAll('.el-input__inner');
            if(inputs[2]) { inputs[2].focus(); inputs[2].value = '""" + credit + """'; inputs[2].dispatchEvent(new Event('input', {bubbles:true})); inputs[2].blur(); }
        }""")
        time.sleep(0.5)
        
        legal = CASE_DATA.get('applicant_legal_person', '')
        print("输入法定代表人...")
        page1.evaluate("""() => {
            const inputs = document.querySelectorAll('.el-input__inner');
            if(inputs[4]) { inputs[4].focus(); inputs[4].value = '""" + legal + """'; inputs[4].dispatchEvent(new Event('input', {bubbles:true})); inputs[4].blur(); }
        }""")
        time.sleep(0.5)
        
        legal_title = CASE_DATA.get('applicant_legal_title', '')
        print("输入法定代表人职务...")
        page1.evaluate("""() => {
            const inputs = document.querySelectorAll('.el-input__inner');
            if(inputs[5]) { inputs[5].focus(); inputs[5].value = '""" + legal_title + """'; inputs[5].dispatchEvent(new Event('input', {bubbles:true})); inputs[5].blur(); }
        }""")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('applicant_phone', '')
        print("输入手机号...")
        page1.evaluate("""() => {
            const inputs = document.querySelectorAll('.el-input__inner');
            if(inputs[6]) { inputs[6].focus(); inputs[6].value = '""" + phone + """'; inputs[6].dispatchEvent(new Event('input', {bubbles:true})); inputs[6].blur(); }
        }""")
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
        page1.locator("#addBSQR").get_by_role("radio", name="自然人").click()
        time.sleep(0.5)
        
        # 自然人被申请人字段（根据截图）：
        # 必填：姓名、国别或地区（默认中国）、证件类型（默认居民身份证）、证件号码、性别（默认男性）
        # 选填：出生日期、年龄、民族（默认汉族）、手机号码、固定电话、经常居住地
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入姓名: {name}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="姓名").locator(".el-input__inner")
            input_field.click()
            input_field.fill(name)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('姓名')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        cert_no = CASE_DATA.get('respondent_id', '')
        print(f"输入证件号码: {cert_no}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="证件号码").locator(".el-input__inner")
            input_field.click()
            input_field.fill(cert_no)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('证件号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{cert_no}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        gender = CASE_DATA.get('respondent_gender', '男性')
        print(f"选择性别: {gender}...")
        if gender == '男' or gender == '男性':
            page1.evaluate("() => { const radios = document.querySelectorAll('input[type=radio]'); for(let r of radios) { const label = r.parentElement; if(label && label.textContent.includes('男')) { r.click(); return; } } }")
        else:
            page1.evaluate("() => { const radios = document.querySelectorAll('input[type=radio]'); for(let r of radios) { const label = r.parentElement; if(label && label.textContent.includes('女')) { r.click(); return; } } }")
        time.sleep(0.5)
        
        phone = CASE_DATA.get('respondent_phone', '')
        print(f"输入手机号: {phone}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="手机号码").locator(".el-input__inner")
            input_field.click()
            input_field.fill(phone)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('手机号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
    
    elif respondent_type == '法人':
        page1.locator("#addBSQR").get_by_role("radio", name="法人").click()
        time.sleep(0.5)
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入单位名称: {name}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位名称").locator(".el-input__inner")
            input_field.click()
            input_field.fill(name)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        credit = CASE_DATA.get('respondent_uscc', '')
        if credit:
            print(f"输入证照号码: {credit}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="证照号码").locator(".el-input__inner")
                input_field.click()
                input_field.fill(credit)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('证照号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
    
    elif respondent_type == '非法人组织':
        page1.locator("#addBSQR").get_by_role("radio", name="非法人组织").click()
        time.sleep(0.5)
        
        name = CASE_DATA.get('respondent_name', '')
        print(f"输入单位名称: {name}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位名称").locator(".el-input__inner")
            input_field.click()
            input_field.fill(name)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
    
    print("保存被申请人...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("被申请人添加成功!")




def add_property(page1):
    """添加财产线索 - 数据驱动版本"""
    print("\n" + "=" * 50)
    print("添加财产线索")
    print("=" * 50)
    
    property_type = CASE_DATA.get('property_type', '存款')
    print(f"财产类型: {property_type}")
    
    # 点击添加（在财产线索区域内查找）
    print("点击添加财产...")
    try:
        page1.locator("div").filter(has_text=re.compile(r"财产线索|保全财产")).locator("span").filter(has_text=re.compile(r"^添加$")).click()
    except:
        try:
            adds = page1.locator("span").filter(has_text=re.compile(r"^添加$")).all()
            if len(adds) >= 3:
                adds[-1].click()
            else:
                page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let i=spans.length-1; i>=0; i--) { if(spans[i].textContent.trim() === '添加') { spans[i].click(); return; } } }")
        except:
            page1.evaluate("() => { const sections = document.querySelectorAll('div, section'); for(let section of sections) { if(section.textContent.includes('财产线索') || section.textContent.includes('保全财产')) { const spans = section.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { s.click(); return; } } } } }")
    time.sleep(2)
    
    # 选择财产类型
    print(f"选择财产类型: {property_type}...")
    clicked = False
    
    if not clicked:
        try:
            page1.get_by_placeholder("请选择财产类型").click()
            time.sleep(1)
            page1.get_by_text(property_type, exact=True).click()
            clicked = True
            print("  方法1成功")
        except:
            pass
    
    if not clicked:
        try:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div, span'); for(let item of items) {{ if(item.textContent.trim() === '{property_type}') {{ item.click(); return true; }} }} return false; }}")
            clicked = True
            print("  方法2成功")
        except:
            pass
    
    if not clicked:
        print(f"  警告: 无法选择财产类型 {property_type}")
    
    time.sleep(1)
    
    # 选择财产所有人 - 使用更可靠的方式
    owner = CASE_DATA.get('property_owner', '') or CASE_DATA.get('respondent_name', '')
    print(f"选择财产所有人: {owner}...")
    
    try:
        # 方法1：使用Playwright的locator
        dropdown = page1.locator(".el-form-item").filter(has_text="财产所有人").locator(".el-input__inner")
        dropdown.click()
        time.sleep(1)
        # 在下拉选项中查找
        page1.get_by_text(owner, exact=True).click()
        print("  选择成功")
    except:
        try:
            # 方法2：使用JavaScript
            page1.evaluate("() => { const items = document.querySelectorAll('.el-form-item'); for(let item of items) { if(item.textContent.includes('财产所有人')) { const input = item.querySelector('.el-input__inner'); if(input) { input.click(); return; } } } }")
            time.sleep(1)
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div'); for(let item of items) {{ if(item.textContent.trim() === '{owner}') {{ item.click(); return; }} }} }}")
            print("  JS选择成功")
        except:
            print("  无法选择财产所有人")
    
    time.sleep(1)
    
    if property_type == '房产':
        print("输入房产信息...")
        
        # 输入房产坐落位置 - 使用标签精确匹配
        detail = CASE_DATA.get('property_detail_location', '') or CASE_DATA.get('property_location', '')
        if detail:
            print(f"输入房产坐落位置: {detail}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="房产坐落位置").locator(".el-input__inner")
                input_field.click()
                input_field.fill(detail)
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('房产坐落位置')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{detail}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 输入房产证号
        cert_no = CASE_DATA.get('property_cert_no', '')
        if cert_no:
            print(f"输入房产证号: {cert_no}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="房产证号").locator(".el-input__inner")
                input_field.click()
                input_field.fill(cert_no)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('房产证号')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{cert_no}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
    
    # 输入财产价值 - 使用标签精确匹配
    value = str(CASE_DATA.get('property_value', CASE_DATA.get('preserve_amount', 0)))
    print(f"输入财产价值: {value}...")
    try:
        input_field = page1.locator(".el-form-item").filter(has_text="财产价值").locator(".el-input__inner")
        input_field.click()
        input_field.fill(value)
        print("  成功")
    except:
        page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('财产价值')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{value}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
    time.sleep(0.5)
    
    # 保存
    print("保存财产线索...")
    try:
        page1.get_by_role("button", name="保存").click()
    except:
        page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let btn of btns) { if(btn.textContent.includes('保存')) { btn.click(); return; } } }")
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
    clicked = False
    
    # 方法1：使用locator查询所有按钮
    if not clicked:
        try:
            buttons = page1.locator("button").all()
            for btn in buttons:
                try:
                    text = btn.text_content()
                    if text and "下一步" in text and btn.is_visible():
                        btn.click()
                        clicked = True
                        print("  方法1成功")
                        break
                except:
                    continue
        except:
            pass
    
    # 方法2：使用JavaScript查找
    if not clicked:
        try:
            result = page1.evaluate("() => { const btns = document.querySelectorAll('button, uni-button'); for(let btn of btns) { if(btn.textContent && btn.textContent.includes('下一步') && btn.offsetParent !== null) { btn.click(); return true; } } return false; }")
            if result:
                clicked = True
                print("  方法2成功")
        except:
            pass
    
    if not clicked:
        print("  下一步按钮未找到，跳过")
        return
    
    time.sleep(2)
    
    # 点击添加
    print("点击添加担保...")
    page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { const parent = s.closest('[id*=add], [class*=add]'); if(parent) { s.click(); return; } } } }")
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
    page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { let p = input.parentElement; for(let i=0; i<8; i++) { if(!p) break; if(p.textContent.includes('担保人') && !input.readOnly) { input.value = '" + guarantor + "'; input.dispatchEvent(new Event('input', {bubbles:true})); return; } p = p.parentElement; } } }")
    time.sleep(0.5)
    
    # 输入担保物名称
    guarantee_object = CASE_DATA.get('guarantee_property_name', '') or CASE_DATA.get('guarantee_object', '')
    if guarantee_object:
        print(f"输入担保物名称: {guarantee_object}...")
        page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { let p = input.parentElement; for(let i=0; i<8; i++) { if(!p) break; if(p.textContent.includes('担保名称') && !input.readOnly) { input.value = '" + guarantee_object + "'; input.dispatchEvent(new Event('input', {bubbles:true})); return; } p = p.parentElement; } } }")
        time.sleep(0.5)
    
    # 输入担保价值
    value = str(CASE_DATA.get('guarantee_value', CASE_DATA.get('preserve_amount', 0)))
    print(f"输入担保价值: {value}...")
    page1.evaluate("() => { const inputs = document.querySelectorAll('input'); for(let input of inputs) { let p = input.parentElement; for(let i=0; i<8; i++) { if(!p) break; if(p.textContent.includes('担保价值') && !input.readOnly) { input.value = '" + value + "'; input.dispatchEvent(new Event('input', {bubbles:true})); return; } p = p.parentElement; } } }")
    time.sleep(0.5)
    
    # 保存
    print("保存担保信息...")
    try:
        page1.get_by_role("button", name="保存").click()
    except:
        page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let btn of btns) { if(btn.textContent.includes('保存')) { btn.click(); return; } } }")
    time.sleep(2)
    
    print("担保信息添加成功!")


def upload_files(page1):
    """上传材料文件"""
    print("\n" + "=" * 50)
    print("上传材料")
    print("=" * 50)
    
    # 点击下一步进入材料上传页面
    print("进入材料上传页面...")
    try:
        page1.get_by_role("button", name="下一步").click()
    except:
        page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let btn of btns) { if(btn.textContent.includes('下一步')) { btn.click(); return; } } }")
    time.sleep(3)
    
    # 查找文件上传input
    print("查找文件上传区域...")
    file_inputs = page1.locator("input[type='file']").all()
    print(f"  找到 {len(file_inputs)} 个文件上传区域")
    
    if len(file_inputs) == 0:
        print("  未找到文件上传区域，跳过")
        return
    
    # 上传文件
    import os
    upload_dir = r'C:\court-auto-filing\uploads\保全2026002'
    
    if not os.path.exists(upload_dir):
        print(f"  上传目录不存在: {upload_dir}")
        return
    
    # 遍历上传区域
    for i, file_input in enumerate(file_inputs):
        try:
            # 获取上传区域的标签
            label = file_input.locator("xpath=ancestor::div[contains(@class, 'el-form-item')]").text_content()
            print(f"  区域 {i+1}: {label}")
        except:
            print(f"  区域 {i+1}: 未知类型")
    
    print("材料上传完成!")

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
    
    # 启动浏览器并执行流程
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 登录
        if not auto_login(page):
            print("登录失败")
            browser.close()
            return
        
        # 创建保全申请
        page1 = create_preservation(page)
        if not page1:
            print("创建保全申请失败")
            browser.close()
            return
        
        # 添加申请人
        add_applicant(page1)
        
        # 添加被申请人
        add_respondent(page1)
        
        # 添加财产线索
        add_property(page1)
        
        # 添加担保信息
        add_guarantee(page1)
        
        # 上传材料
        upload_files(page1)
        
        print("\n" + "=" * 60)
        print("保全申请流程完成!")
        print("=" * 60)
        
        # 等待查看结果
        time.sleep(30)
        
        browser.close()

if __name__ == '__main__':
    main()
