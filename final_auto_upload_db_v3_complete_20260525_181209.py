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
    
    # 选择财产所有人 - 关键修复
    owner = CASE_DATA.get('property_owner', '') or CASE_DATA.get('respondent_name', '')
    print(f"选择财产所有人: {owner}...")
    
    try:
        # 方法1：点击下拉框，等待选项出现，然后选择
        dropdown = page1.locator(".el-form-item").filter(has_text="财产所有人").locator(".el-input__inner")
        dropdown.click()
        time.sleep(2)  # 等待下拉选项加载
        
        # 在下拉选项中查找并点击
        options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item, .uni-scroll-view li").all()
        selected = False
        for option in options:
            try:
                text = option.text_content()
                if text and owner in text:
                    option.click()
                    selected = True
                    print(f"  选择成功: {text}")
                    break
            except:
                continue
        
        if not selected:
            # 尝试直接点击包含owner文本的元素
            page1.get_by_text(owner, exact=False).first.click()
            print("  选择成功(模糊匹配)")
    except Exception as e:
        print(f"  选择失败: {e}")
        # 备用：使用JavaScript
        try:
            page1.evaluate("() => { const items = document.querySelectorAll('.el-form-item'); for(let item of items) { if(item.textContent.includes('财产所有人')) { const input = item.querySelector('.el-input__inner'); if(input) { input.click(); return; } } } }")
            time.sleep(2)
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('li, div, span'); for(let item of items) {{ if(item.textContent.includes('{owner}')) {{ item.click(); return; }} }} }}")
            print("  JS选择成功")
        except:
            print("  JS选择也失败")
    
    time.sleep(1)
    
    if property_type == '房产':
        print("输入房产信息...")
        
        # 选择省份
        province = CASE_DATA.get('property_province', '')
        if province:
            print(f"选择省份: {province}...")
            try:
                # 步骤0：先关闭所有打开的下拉框
                page1.evaluate("""() => {
                    // 点击body关闭所有下拉框
                    document.body.click();
                }""")
                time.sleep(1)
                
                # 步骤1：点击房产坐落位置的下拉框
                page1.evaluate("""() => {
                    const formItems = document.querySelectorAll('.el-form-item');
                    for(let item of formItems) {
                        const label = item.querySelector('.el-form-item__label');
                        if(label && label.textContent.includes('房产坐落位置')) {
                            const select = item.querySelector('.el-select');
                            if(select) {
                                const input = select.querySelector('.el-input__inner');
                                if(input) {
                                    input.click();
                                    return true;
                                }
                            }
                        }
                    }
                    return false;
                }""")
                time.sleep(2)
                
                # 步骤2：使用JavaScript点击选项
                result = page1.evaluate(f"""() => {{
                    // 找到所有打开的下拉框
                    const dropdowns = document.querySelectorAll('.el-select-dropdown.el-popper');
                    if(dropdowns.length === 0) return 'no dropdown';
                    
                    // 输出所有下拉框的选项数，用于调试
                    let debug = [];
                    for(let i = 0; i < dropdowns.length; i++) {{
                        const items = dropdowns[i].querySelectorAll('li.el-select-dropdown__item');
                        debug.push('dropdown' + i + ': ' + items.length + ' items');
                    }}
                    
                    // 使用最后一个打开的下拉框
                    const dropdown = dropdowns[dropdowns.length - 1];
                    const items = dropdown.querySelectorAll('li.el-select-dropdown__item');
                    
                    for(let item of items) {{
                        const span = item.querySelector('span');
                        const text = span ? span.textContent.trim() : item.textContent.trim();
                        // 匹配时去掉"省"字（如"广东省"匹配"广东"）
                        const provinceShort = '{province}'.replace('省', '').replace('市', '').replace('自治区', '');
                        if(text === '{province}' || text === provinceShort) {{
                            // 触发完整的事件序列
                            item.dispatchEvent(new MouseEvent('mouseenter', {{bubbles: true}}));
                            item.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true}}));
                            item.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                            item.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true}}));
                            return 'clicked: ' + text + '. ' + debug.join(', ');
                        }}
                    }}
                    
                    // 输出所有选项用于调试
                    const allTexts = Array.from(items).map(i => i.textContent.trim());
                    return 'not found in ' + items.length + ' items. All: ' + allTexts.join(', ') + '. ' + debug.join(', ');
                }}""")
                print(f"  JS结果: {result}")
                
                # 步骤3：点击空白处关闭下拉框
                time.sleep(1)
                page1.evaluate("""() => {
                    document.body.click();
                }""")
                time.sleep(1)
            except Exception as e:
                print(f"  省份选择失败: {e}")
            time.sleep(1)
        
        # 输入具体地址
        detail = CASE_DATA.get('property_detail_location', '') or CASE_DATA.get('property_location', '')
        if detail:
            print(f"输入具体地址: {detail}...")
            try:
                # 方法1：使用placeholder查找
                address_input = page1.get_by_placeholder("请输入具体位置")
                address_input.click()
                address_input.fill(detail)
                print("  地址输入成功")
            except:
                try:
                    # 方法2：找到房产坐落位置的文本输入框（不是下拉框）
                    address_input = page1.locator(".el-form-item").filter(has_text="房产坐落位置").locator("input[type='text']").last
                    address_input.click()
                    address_input.fill(detail)
                    print("  地址输入成功(方法2)")
                except Exception as e:
                    print(f"  地址输入失败: {e}")
                    # 备用JS方法
                    page1.evaluate(f"""() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('房产坐落位置')) {{ const inputs = item.querySelectorAll('input[type=\"text\"]'); for(let input of inputs) {{ if(!input.readOnly) {{ input.focus(); input.value = '{detail}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); return; }} }} }} }} }}""")
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
    
    # 输入财产价值
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
    page1.evaluate(f"""() => {{
        const formItems = document.querySelectorAll('.el-form-item');
        for(let item of formItems) {{
            const label = item.querySelector('.el-form-item__label');
            if(label && label.textContent.includes('担保人') && !label.textContent.includes('担保物')) {{
                const input = item.querySelector('input');
                if(input) {{
                    input.value = '{guarantor}';
                    input.dispatchEvent(new Event('input', {{bubbles:true}}));
                    input.dispatchEvent(new Event('change', {{bubbles:true}}));
                    return true;
                }}
            }}
        }}
        return false;
    }}""")
    time.sleep(0.5)
    
    # 输入担保物名称
    guarantee_object = CASE_DATA.get('guarantee_property_name', '') or CASE_DATA.get('guarantee_object', '')
    if guarantee_object:
        print(f"输入担保物名称: {guarantee_object}...")
        page1.evaluate(f"""() => {{
            const formItems = document.querySelectorAll('.el-form-item');
            for(let item of formItems) {{
                const label = item.querySelector('.el-form-item__label');
                if(label && label.textContent.includes('担保物名称')) {{
                    const input = item.querySelector('input');
                    if(input) {{
                        input.value = '{guarantee_object}';
                        input.dispatchEvent(new Event('input', {{bubbles:true}}));
                        input.dispatchEvent(new Event('change', {{bubbles:true}}));
                        return true;
                    }}
                }}
            }}
            return false;
        }}""")
        time.sleep(0.5)
    
    # 输入担保价值
    value = str(CASE_DATA.get('guarantee_value', CASE_DATA.get('preserve_amount', 0)))
    print(f"输入担保价值: {value}...")
    page1.evaluate(f"""() => {{
        const formItems = document.querySelectorAll('.el-form-item');
        for(let item of formItems) {{
            const label = item.querySelector('.el-form-item__label');
            if(label && label.textContent.includes('担保价值')) {{
                const input = item.querySelector('input');
                if(input) {{
                    input.value = '{value}';
                    input.dispatchEvent(new Event('input', {{bubbles:true}}));
                    input.dispatchEvent(new Event('change', {{bubbles:true}}));
                    return true;
                }}
            }}
        }}
        return false;
    }}""")
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
    """上传材料文件 - 从数据库读取文件路径"""
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
    
    # 从数据库读取文件列表
    import pymysql
    import os
    
    case_no = CASE_DATA.get('case_no', '')
    
    # 连接数据库获取文件列表
    try:
        conn = pymysql.connect(host='localhost', user='root', password='lijiayu123', database='court_filing', charset='utf8mb4')
        with conn.cursor() as cursor:
            # 获取case_id
            cursor.execute("SELECT id FROM cases WHERE case_no = %s", (case_no,))
            case = cursor.fetchone()
            if not case:
                print(f"  未找到案件: {case_no}")
                return
            
            case_id = case[0]
            
            # 获取文件列表
            cursor.execute("""
                SELECT file_category, file_name, file_path
                FROM case_files
                WHERE case_id = %s
                ORDER BY file_category
            """, (case_id,))
            files = cursor.fetchall()
            
            print(f"  从数据库读取到 {len(files)} 个文件")
            
            # 按类别分组
            file_map = {}
            for file_category, file_name, file_path in files:
                if file_category not in file_map:
                    file_map[file_category] = []
                file_map[file_category].append({
                    'name': file_name,
                    'path': file_path
                })
        conn.close()
    except Exception as e:
        print(f"  数据库读取失败: {e}")
        return
    
    # 查找所有可点击的上传区域
    print("查找上传区域...")
    
    # 使用JavaScript查找所有上传按钮
    try:
        upload_areas = page1.evaluate("""() => {
            const areas = [];
            // 查找所有包含"上传"文本的元素
            const allElements = document.querySelectorAll('*');
            for(let el of allElements) {
                if(el.children.length === 0 && el.textContent && el.textContent.includes('上传')) {
                    // 找到可点击的父元素
                    let clickable = el;
                    while(clickable && clickable.tagName !== 'BODY') {
                        if(clickable.tagName === 'BUTTON' || 
                           clickable.classList.contains('el-button') ||
                           clickable.onclick ||
                           clickable.style.cursor === 'pointer') {
                            break;
                        }
                        clickable = clickable.parentElement;
                    }
                    
                    // 获取区域标签
                    let label = '';
                    let parent = el;
                    for(let i=0; i<5; i++) {
                        if(!parent) break;
                        const labelEl = parent.querySelector('label, .el-form-item__label, .material-title');
                        if(labelEl) {
                            label = labelEl.textContent.trim();
                            break;
                        }
                        parent = parent.parentElement;
                    }
                    
                    areas.push({
                        text: el.textContent.trim(),
                        label: label,
                        clickable: clickable ? clickable.outerHTML.substring(0, 200) : null
                    });
                }
            }
            return areas;
        }""")
        print(f"  JS找到 {len(upload_areas)} 个上传区域")
        for area in upload_areas:
            print(f"    - {area.get('label', 'unknown')}: {area.get('text', '')}")
    except Exception as e:
        print(f"  JS查找失败: {e}")
    
    # 使用Playwright查找所有包含"上传"的元素
    try:
        all_elements = page1.locator("text=上传").all()
        print(f"  Playwright找到 {len(all_elements)} 个包含'上传'的元素")
        
        for i, el in enumerate(all_elements):
            try:
                text = el.text_content()
                print(f"  元素 {i+1}: {text.strip()}")
            except:
                pass
    except Exception as e:
        print(f"  Playwright查找失败: {e}")
    
    # 方法3：查找所有按钮并筛选
    try:
        all_buttons = page1.locator("button, .el-button, [class*='button'], [class*='btn'], div[role='button']").all()
        upload_buttons = []
        for btn in all_buttons:
            try:
                text = btn.text_content()
                if text and ('上传' in text or '↑' in text):
                    upload_buttons.append(btn)
            except:
                pass
        
        print(f"  找到 {len(upload_buttons)} 个上传按钮")
        
        for i, btn in enumerate(upload_buttons):
            try:
                btn_text = btn.text_content()
                print(f"  按钮 {i+1}: {btn_text.strip()}")
                
                # 确定材料类型和文件
                files_to_upload = []
                
                if '保全申请书' in btn_text:
                    if '保全申请书' in file_map:
                        files_to_upload = [f['path'] for f in file_map['保全申请书']]
                elif '起诉状' in btn_text:
                    if '起诉状' in file_map:
                        files_to_upload = [f['path'] for f in file_map['起诉状']]
                elif '立案受理通知书' in btn_text:
                    if '立案受理通知书' in file_map:
                        files_to_upload = [f['path'] for f in file_map['立案受理通知书']]
                elif '申请人' in btn_text and ('身份' in btn_text or '证照' in btn_text or '法人' in btn_text or '自然人' in btn_text):
                    # 申请人身份证明材料
                    if '身份证明材料' in file_map:
                        for f in file_map['身份证明材料']:
                            if '申请人' in f['name'] and '被申请人' not in f['name']:
                                files_to_upload.append(f['path'])
                elif '被申请人' in btn_text:
                    # 被申请人身份证明材料
                    if '身份证明材料' in file_map:
                        for f in file_map['身份证明材料']:
                            if '被申请人' in f['name']:
                                files_to_upload.append(f['path'])
                elif '担保' in btn_text or '保证金' in btn_text or '保证人' in btn_text:
                    if '担保材料' in file_map:
                        files_to_upload = [f['path'] for f in file_map['担保材料']]
                elif '证据' in btn_text:
                    if '证据材料' in file_map:
                        files_to_upload = [f['path'] for f in file_map['证据材料']]
                elif '其他' in btn_text:
                    if '其他材料' in file_map:
                        files_to_upload = [f['path'] for f in file_map['其他材料']]
                
                # 过滤存在的文件
                files_to_upload = [f for f in files_to_upload if os.path.exists(f)]
                
                if files_to_upload:
                    print(f"    准备上传 {len(files_to_upload)} 个文件: {', '.join([os.path.basename(f) for f in files_to_upload])}")
                    
                    # 点击上传按钮
                    btn.click()
                    time.sleep(2)
                    
                    # 查找文件input
                    file_input = page1.locator("input[type='file']").last
                    if file_input:
                        file_input.set_input_files(files_to_upload)
                        print(f"    上传成功")
                        time.sleep(3)
                    else:
                        print(f"    未找到文件input")
                else:
                    print(f"    未找到对应文件")
            except Exception as e:
                print(f"    上传失败: {e}")
    except Exception as e:
        print(f"  查找上传按钮失败: {e}")
    
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
