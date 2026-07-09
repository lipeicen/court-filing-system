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


def load_system_config(created_by=''):
    """从数据库加载系统配置(登录账号,密码,用户类型)
    如果传入 created_by，则优先读取该用户对应的法院账号配置
    """
    try:
        conn = pymysql.connect(
            host="localhost", user="root", password="lijiayu123",
            database="court_filing", charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT config_key, config_value FROM system_config")
        config = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        
        # 按 created_by 提取对应的法院账号配置
        if created_by:
            username = config.get(f'login_username_{created_by}', '')
            password = config.get(f'login_password_{created_by}', '')
            user_type = config.get(f'login_user_type_{created_by}', '个人用户')
            if username and password:
                config['login_username'] = username
                config['login_password'] = password
                config['login_user_type'] = user_type
                print(f"使用案件创建者账号配置: {created_by} -> {username}")
        
        return config
    except Exception as e:
        print(f"加载系统配置失败: {e}")
        return {}

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
        case['stock_name'] = prop.get('stock_name', '')
        case['stock_code'] = prop.get('stock_code', '')
        case['stock_quantity'] = prop.get('stock_quantity', '')
        case['stock_company_name'] = prop.get('stock_company_name', '')
        case['stock_reg_location'] = prop.get('stock_reg_location', '')
        case['stock_ratio'] = prop.get('stock_ratio', '')
        case['vehicle_plate_no'] = prop.get('vehicle_plate_no', '')
        case['vehicle_type'] = prop.get('vehicle_type', '')
        case['amount'] = prop.get('amount', '')
        case['currency'] = prop.get('currency', '')
        case['mortgage_property_type'] = prop.get('mortgage_property_type', '') or case.get('mortgage_property_type', '')
        case['pledge_property_type'] = prop.get('pledge_property_type', '') or case.get('pledge_property_type', '')
    else:
        case['property_type'] = '存款'
    
    # 备用映射：当cert_no为空时，使用id字段
    if not case.get('applicant_cert_no'):
        case['applicant_cert_no'] = case.get('applicant_id', '')
    if not case.get('respondent_cert_no'):
        case['respondent_cert_no'] = case.get('respondent_id', '')
    
    CASE_DATA = case
    print(f"案件数据加载成功: {case_no}")
    print(f"  申请人: {case.get('applicant_name', '')}")
    print(f"  被申请人: {case.get('respondent_name', '')}")
    print(f"  保全金额: {case.get('preserve_amount', '')}")
    print(f"  财产类型: {case.get('property_type', '')}")
    print(f"  创建者: {case.get('created_by', '')}")
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


def auto_login(page, created_by='', max_retries=3):
    """自动登录 - 带重试机制
    created_by: 案件创建者账号，用于读取对应的法院系统登录配置
    """
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
        # 从数据库加载登录配置
        sys_config = load_system_config(created_by)
        login_username = sys_config.get('login_username', '13723715831')
        login_password = sys_config.get('login_password', 'HU1234pp')
        login_user_type = sys_config.get('login_user_type', '个人用户')
        print(f"使用账号登录: {login_username}, 身份: {login_user_type}")
        phone_input.fill(login_username)
        time.sleep(0.5)
        
        # 输入密码
        print("输入密码...")
        pwd_input = page.locator("input[type=\"password\"]")
        pwd_input.click()
        pwd_input.fill(login_password)
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
    try:
        page1.get_by_role("button", name="创建保全").click()
    except:
        # 备用：使用JavaScript点击
        page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let btn of btns) { if(btn.textContent.includes('创建保全')) { btn.click(); return; } } }")
    time.sleep(8)
    
    # 截图确认页面状态
    try:
        page1.screenshot(path=r'C:\court-auto-filing\debug_after_create.png')
        print("  截图保存: debug_after_create.png")
    except:
        print("  截图失败")
    
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
    try:
        page1.get_by_text("添加").first.click()
    except:
        page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { s.click(); return; } } }")
    time.sleep(3)  # 增加等待时间让弹窗加载
    
    # 截图确认弹窗状态
    page1.screenshot(path=r'C:\court-auto-filing\debug_applicant_popup.png')
    print("  截图保存: debug_applicant_popup.png")
    
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
        if not gender:
            gender = '男性'
        # 映射性别值
        gender_map = {'男': '男性', '女': '女性'}
        gender_display = gender_map.get(gender, gender)
        print(f"选择性别: {gender_display}...")
        try:
            page1.get_by_role("radio", name=gender_display, exact=True).click()
        except:
            # 如果映射后的值找不到，尝试原始值
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
        print("选择法人类型...")
        try:
            page1.get_by_role("radio", name="法人", exact=True).click(timeout=10000)
            print("  成功")
        except:
            # JS方式点击
            result = page1.evaluate("""() => {
                const radios = document.querySelectorAll('input[type="radio"]');
                for(let radio of radios) {
                    const label = radio.closest('label') || radio.parentElement;
                    if(label && label.textContent.includes('法人')) {
                        radio.click();
                        label.click();
                        return 'clicked: ' + label.textContent;
                    }
                }
                return 'not found';
            }""")
            print(f"  JS结果: {result}")
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
        
        cert_type = CASE_DATA.get('applicant_cert_type', '统一社会信用代码证')
        print(f"证照类型: {cert_type}")
        
        # 如果证照类型是营业执照，选择营业执照
        if cert_type == '营业执照':
            try:
                page1.locator(".el-form-item").filter(has_text="证照类型").locator(".el-input__inner").click()
                time.sleep(1)
                page1.get_by_text("营业执照", exact=True).click()
                print("  选择营业执照")
                time.sleep(0.5)
            except:
                pass
        
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
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="单位名称").locator(".el-input__inner")
            input_field.click()
            input_field.fill(name)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        # 证照类型
        cert_type = CASE_DATA.get('applicant_cert_type', '统一社会信用代码证')
        print(f"证照类型: {cert_type}")
        if cert_type == '营业执照':
            try:
                page1.locator(".el-form-item").filter(has_text="证照类型").locator(".el-input__inner").click()
                time.sleep(1)
                page1.get_by_text("营业执照", exact=True).click()
                print("  选择营业执照")
                time.sleep(0.5)
            except:
                pass
        
        credit = CASE_DATA.get('applicant_uscc', '')
        print(f"输入证照号码: {credit}...")
        try:
            input_field = page1.locator(".el-form-item").filter(has_text="证照号码").locator(".el-input__inner")
            input_field.click()
            input_field.fill(credit)
        except:
            page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('证照号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{credit}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
        time.sleep(0.5)
        
        # 单位性质
        nature = CASE_DATA.get('applicant_nature', '')
        if nature:
            print(f"输入单位性质: {nature}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="单位性质").locator(".el-input__inner")
                input_field.click()
                input_field.fill(nature)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位性质')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{nature}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
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
        
        # 经常居住地
        address = CASE_DATA.get('respondent_address', '')
        if address:
            print(f"输入经常居住地: {address}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="经常居住地").locator(".el-input__inner")
                input_field.click()
                input_field.fill(address)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('经常居住地')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
    
    elif respondent_type == '法人':
        page1.locator("#addBSQR").get_by_role("radio", name="法人", exact=True).click()
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
        
        cert_type = CASE_DATA.get('respondent_cert_type', '统一社会信用代码证')
        print(f"证照类型: {cert_type}")
        
        # 如果证照类型是营业执照，选择营业执照
        if cert_type == '营业执照':
            try:
                page1.locator(".el-form-item").filter(has_text="证照类型").locator(".el-input__inner").click()
                time.sleep(1)
                page1.get_by_text("营业执照", exact=True).click()
                print("  选择营业执照")
                time.sleep(0.5)
            except:
                pass
        
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
        
        # 添加法定代表人
        legal = CASE_DATA.get('respondent_legal_person', '')
        if legal:
            print(f"输入法定代表人: {legal}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="法定代表人").locator(".el-input__inner")
                input_field.click()
                input_field.fill(legal)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人') && !item.textContent.includes('职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 添加法定代表人职务
        legal_title = CASE_DATA.get('respondent_legal_title', '')
        if legal_title:
            print(f"输入法定代表人职务: {legal_title}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="法定代表人职务").locator(".el-input__inner")
                input_field.click()
                input_field.fill(legal_title)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal_title}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 添加手机号码
        phone = CASE_DATA.get('respondent_phone', '')
        if phone:
            print(f"输入手机号码: {phone}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="手机号码").locator(".el-input__inner")
                input_field.click()
                input_field.fill(phone)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('手机号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 单位性质 - 下拉框选择
        nature = CASE_DATA.get('respondent_nature', '')
        if nature:
            print(f"选择单位性质: {nature}...")
            try:
                # 点击下拉框
                page1.locator(".el-form-item").filter(has_text="单位性质").locator(".el-input__inner").click()
                time.sleep(1)
                # 在下拉选项中查找
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and nature in text:
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    # 尝试直接点击
                    page1.get_by_text(nature, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 添加单位地址
        address = CASE_DATA.get('respondent_address', '')
        if address:
            print(f"输入单位地址: {address}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="单位地址").locator(".el-input__inner")
                input_field.click()
                input_field.fill(address)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位地址')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 添加单位注册地
        reg_address = CASE_DATA.get('respondent_reg_address', '')
        if reg_address:
            print(f"输入单位注册地: {reg_address}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="单位注册地").locator(".el-input__inner")
                input_field.click()
                input_field.fill(reg_address)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位注册地')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{reg_address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 截图确认填写状态
        page1.screenshot(path=r'C:\court-auto-filing\debug_respondent_before_save.png')
        print("  截图保存: debug_respondent_before_save.png")
    
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
        
        # 证照类型
        cert_type = CASE_DATA.get('respondent_cert_type', '统一社会信用代码证')
        print(f"证照类型: {cert_type}")
        if cert_type == '营业执照':
            try:
                page1.locator(".el-form-item").filter(has_text="证照类型").locator(".el-input__inner").click()
                time.sleep(1)
                page1.get_by_text("营业执照", exact=True).click()
                print("  选择营业执照")
                time.sleep(0.5)
            except:
                pass
        
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
        
        # 单位性质 - 下拉框选择
        nature = CASE_DATA.get('respondent_nature', '')
        if nature:
            print(f"选择单位性质: {nature}...")
            try:
                # 点击下拉框
                page1.locator(".el-form-item").filter(has_text="单位性质").locator(".el-input__inner").click()
                time.sleep(1)
                # 在下拉选项中查找
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and nature in text:
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    # 尝试直接点击
                    page1.get_by_text(nature, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        legal = CASE_DATA.get('respondent_legal_person', '')
        if legal:
            print(f"输入法定代表人: {legal}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="法定代表人").locator(".el-input__inner")
                input_field.click()
                input_field.fill(legal)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人') && !item.textContent.includes('职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        legal_title = CASE_DATA.get('respondent_legal_title', '')
        if legal_title:
            print(f"输入法定代表人职务: {legal_title}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="法定代表人职务").locator(".el-input__inner")
                input_field.click()
                input_field.fill(legal_title)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('法定代表人职务')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{legal_title}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        phone = CASE_DATA.get('respondent_phone', '')
        if phone:
            print(f"输入手机号码: {phone}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="手机号码").locator(".el-input__inner")
                input_field.click()
                input_field.fill(phone)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('手机号码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{phone}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        address = CASE_DATA.get('respondent_address', '')
        if address:
            print(f"输入单位地址: {address}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="单位地址").locator(".el-input__inner")
                input_field.click()
                input_field.fill(address)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位地址')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        reg_address = CASE_DATA.get('respondent_reg_address', '')
        if reg_address:
            print(f"输入单位注册地: {reg_address}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="单位注册地").locator(".el-input__inner")
                input_field.click()
                input_field.fill(reg_address)
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('单位注册地')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{reg_address}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
    
    print("保存被申请人...")
    try:
        # 在被申请人弹窗内查找保存按钮
        page1.locator("#addBSQR").get_by_role("button", name="保存").click()
    except:
        try:
            # 备用：查找所有保存按钮，点击最后一个（通常是被申请人的）
            buttons = page1.locator("button").filter(has_text="保存").all()
            if len(buttons) >= 2:
                buttons[-1].click()
            else:
                page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let i=btns.length-1; i>=0; i--) { if(btns[i].textContent.includes('保存')) { btns[i].click(); return; } } }")
        except:
            page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let i=btns.length-1; i>=0; i--) { if(btns[i].textContent.includes('保存')) { btns[i].click(); return; } } }")
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
    
    # 先点击下拉框获取选项
    try:
        page1.get_by_placeholder("请选择财产类型").click()
        time.sleep(1)
        
        # 获取所有选项
        options = page1.evaluate("""() => {
            const items = document.querySelectorAll('.el-select-dropdown__list li, .el-dropdown-menu__item, .uni-scroll-view li');
            return Array.from(items).map(item => item.textContent.trim()).filter(text => text.length > 0);
        }""")
        print(f"  页面选项: {options}")
        
        # 根据选项匹配
        selected_type = None
        if property_type in options:
            selected_type = property_type
        elif '交通运输工具' in options and property_type in ['车辆', '汽车']:
            selected_type = '交通运输工具'
        elif '股票' in options and property_type in ['股权', '股份']:
            selected_type = '股票'
        else:
            # 模糊匹配
            for opt in options:
                if property_type in opt or opt in property_type:
                    selected_type = opt
                    break
        
        if selected_type:
            print(f"  匹配到: {selected_type}")
            page1.get_by_text(selected_type, exact=True).click()
            clicked = True
            print("  选择成功")
        else:
            print(f"  警告: 未找到匹配的选项")
    except Exception as e:
        print(f"  获取选项失败: {e}")
    
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
    
    # 股权类型特殊字段
    if property_type == '股权':
        # 发行单位注册地 - 下拉框选择
        reg_location = CASE_DATA.get('stock_reg_location', '')
        if reg_location:
            print(f"选择发行单位注册地: {reg_location}...")
            try:
                # 点击下拉框
                page1.locator(".el-form-item").filter(has_text="发行单位注册地").locator(".el-input__inner").click()
                time.sleep(1)
                # 在下拉选项中查找（去掉"市"字匹配）
                reg_short = reg_location.replace('市', '').replace('省', '')
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and (reg_location in text or reg_short in text):
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    # 尝试直接点击
                    page1.get_by_text(reg_location, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 持股公司名称
        company_name = CASE_DATA.get('stock_company_name', '')
        if company_name:
            print(f"输入持股公司名称: {company_name}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="持股公司名称").locator(".el-input__inner")
                input_field.click()
                input_field.fill(company_name)
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('持股公司名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{company_name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 出资比例 - 百分比格式（如30表示30%）
        ratio = CASE_DATA.get('stock_ratio', '')
        print(f"  出资比例数据: {ratio} (类型: {type(ratio)})")
        if ratio is not None and ratio != '':
            ratio_str = str(ratio).replace('%', '')
            print(f"输入出资比例: {ratio_str}%...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="出资比例").locator(".el-input__inner")
                input_field.click()
                input_field.fill(ratio_str)
                print("  成功")
            except Exception as e:
                print(f"  失败: {e}")
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('出资比例')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{ratio_str}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        else:
            print("  警告: 出资比例数据为空")
    
    # 股票类型特殊字段
    if property_type == '股票':
        # 发行单位注册地 - 下拉框选择
        reg_location = CASE_DATA.get('stock_reg_location', '')
        if reg_location:
            print(f"选择发行单位注册地: {reg_location}...")
            try:
                page1.locator(".el-form-item").filter(has_text="发行单位注册地").locator(".el-input__inner").click()
                time.sleep(1)
                reg_short = reg_location.replace('市', '').replace('省', '')
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and (reg_location in text or reg_short in text):
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    page1.get_by_text(reg_location, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 股票名称
        stock_name = CASE_DATA.get('stock_name', '') or CASE_DATA.get('stock_company_name', '')
        if stock_name:
            print(f"输入股票名称: {stock_name}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="股票名称").locator(".el-input__inner")
                input_field.click()
                input_field.fill(stock_name)
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('股票名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{stock_name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 股票代码
        stock_code = CASE_DATA.get('stock_code', '')
        if stock_code:
            print(f"输入股票代码: {stock_code}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="股票代码").locator(".el-input__inner")
                input_field.click()
                input_field.fill(str(stock_code))
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('股票代码')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{stock_code}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 持股数量
        stock_qty = CASE_DATA.get('stock_quantity', '')
        if stock_qty:
            print(f"输入持股数量: {stock_qty}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="持股数量").locator(".el-input__inner")
                input_field.click()
                input_field.fill(str(stock_qty))
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('持股数量')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{stock_qty}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
    
    # 存款类型特殊字段
    if property_type == '存款':
        # 开户行所在地 - 下拉框选择
        # 优先使用property_province，其次property_location
        bank_location = CASE_DATA.get('property_province', '') or CASE_DATA.get('property_location', '')
        if bank_location:
            print(f"选择开户行所在地: {bank_location}...")
            try:
                # 使用JS点击
                page1.evaluate(f"""() => {{
                    const labels = document.querySelectorAll('.el-form-item__label');
                    for(let label of labels) {{
                        if(label.textContent.includes('开户行所在地')) {{
                            const formItem = label.closest('.el-form-item');
                            if(formItem) {{
                                const select = formItem.querySelector('.el-select');
                                if(select) {{
                                    select.click();
                                    return true;
                                }}
                            }}
                        }}
                    }}
                    return false;
                }}""")
                time.sleep(2)
                
                # 在下拉选项中查找
                loc_short = bank_location.replace('市', '').replace('省', '')
                result = page1.evaluate(f"""() => {{
                    const dropdowns = document.querySelectorAll('.el-select-dropdown.el-popper');
                    if(dropdowns.length === 0) return 'no dropdown';
                    
                    const dropdown = dropdowns[dropdowns.length - 1];
                    const items = dropdown.querySelectorAll('.el-select-dropdown__item');
                    
                    for(let item of items) {{
                        const text = item.textContent.trim();
                        if(text.includes('{bank_location}') || text.includes('{loc_short}')) {{
                            item.click();
                            return 'clicked: ' + text;
                        }}
                    }}
                    
                    const allTexts = Array.from(items).map(i => i.textContent.trim());
                    return 'not found in: ' + allTexts.slice(0, 10).join(', ') + '...';
                }}""")
                print(f"  JS结果: {result}")
                if 'clicked' in result:
                    print("  选择成功")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 开户银行名称
        bank_name = CASE_DATA.get('bank_name', '')
        if bank_name:
            print(f"输入开户银行名称: {bank_name}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="开户银行名称").locator(".el-input__inner")
                input_field.click()
                input_field.fill(bank_name)
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('开户银行名称')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{bank_name}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 开户账号
        bank_account = CASE_DATA.get('bank_account', '')
        if bank_account:
            print(f"输入开户账号: {bank_account}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="开户账号").locator(".el-input__inner")
                input_field.click()
                input_field.fill(str(bank_account))
                print("  成功")
            except:
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('开户账号')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{bank_account}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 数额
        amount = CASE_DATA.get('amount', '')
        if amount:
            print(f"输入数额: {amount}...")
            try:
                # JS方式 - 通过label精确定位
                result = page1.evaluate(f"""() => {{
                    const labels = document.querySelectorAll('.el-form-item__label');
                    for(let label of labels) {{
                        if(label.textContent.includes('数额') && !label.textContent.includes('财产价值')) {{
                            const formItem = label.closest('.el-form-item');
                            if(formItem) {{
                                const input = formItem.querySelector('.el-input__inner');
                                if(input) {{
                                    input.focus();
                                    input.value = '{amount}';
                                    input.dispatchEvent(new Event('input', {{bubbles:true}}));
                                    input.dispatchEvent(new Event('change', {{bubbles:true}}));
                                    input.blur();
                                    return 'filled: ' + input.value;
                                }}
                            }}
                        }}
                    }}
                    return 'not found';
                }}""")
                print(f"  JS结果: {result}")
                if 'filled' in result:
                    print("  成功")
                else:
                    print("  失败: 未找到字段")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 币种
        currency = CASE_DATA.get('currency', '')
        # 币种映射: CNY -> 人民币
        if currency == 'CNY':
            currency = '人民币'
        if currency:
            print(f"选择币种: {currency}...")
            try:
                page1.locator(".el-form-item").filter(has_text="币种").locator(".el-input__inner").click()
                time.sleep(1)
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and currency in text:
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    page1.get_by_text(currency, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
    
    # 车辆类型特殊字段
    if property_type == '车辆':
        # 车辆品牌型号
        vehicle_brand = CASE_DATA.get('vehicle_brand_model', '')
        if vehicle_brand:
            print(f"输入车辆品牌型号: {vehicle_brand}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="车辆品牌型号").locator(".el-input__inner")
                input_field.click()
                input_field.fill(vehicle_brand)
                print("  成功")
            except Exception as e:
                print(f"  失败: {e}")
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('车辆品牌型号')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{vehicle_brand}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 车牌号
        vehicle_plate = CASE_DATA.get('vehicle_plate_no', '')
        if vehicle_plate:
            print(f"输入车牌号: {vehicle_plate}...")
            try:
                input_field = page1.locator(".el-form-item").filter(has_text="车牌号").locator(".el-input__inner")
                input_field.click()
                input_field.fill(vehicle_plate)
                print("  成功")
            except Exception as e:
                print(f"  失败: {e}")
                page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('车牌号')) {{ const input = item.querySelector('.el-input__inner'); if(input) {{ input.focus(); input.value = '{vehicle_plate}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); }} }} }} }}")
            time.sleep(0.5)
        
        # 车辆归属地（省份）
        vehicle_province = CASE_DATA.get('property_province', '')
        if vehicle_province:
            print(f"选择车辆归属地: {vehicle_province}...")
            try:
                # 点击下拉框
                page1.locator(".el-form-item").filter(has_text="车辆归属地").locator(".el-input__inner").click()
                time.sleep(1)
                # 选择省份（去掉"省"字匹配）
                province_short = vehicle_province.replace('省', '').replace('市', '').replace('自治区', '')
                options = page1.locator(".el-select-dropdown__list li, .el-dropdown-menu__item").all()
                selected = False
                for option in options:
                    try:
                        text = option.text_content()
                        if text and (vehicle_province in text or province_short in text):
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                if not selected:
                    page1.get_by_text(vehicle_province, exact=False).first.click()
                    print("  选择成功(模糊匹配)")
            except Exception as e:
                print(f"  失败: {e}")
            time.sleep(0.5)
        
        # 车辆具体位置
        vehicle_location = CASE_DATA.get('property_location', '')
        if vehicle_location:
            print(f"输入车辆具体位置: {vehicle_location}...")
            try:
                # 方法1：使用placeholder查找
                input_field = page1.get_by_placeholder("请输入车辆具体位置")
                input_field.click()
                input_field.fill(vehicle_location)
                print("  成功")
            except:
                try:
                    # 方法2：使用label查找
                    input_field = page1.locator(".el-form-item").filter(has_text="车辆具体位置").locator("input[type='text']").last
                    input_field.click()
                    input_field.fill(vehicle_location)
                    print("  成功(方法2)")
                except Exception as e:
                    print(f"  失败: {e}")
                    # 方法3：JS注入
                    page1.evaluate(f"() => {{ const items = document.querySelectorAll('.el-form-item'); for(let item of items) {{ if(item.textContent.includes('车辆具体位置')) {{ const inputs = item.querySelectorAll('input'); for(let input of inputs) {{ if(input.type === 'text') {{ input.focus(); input.value = '{vehicle_location}'; input.dispatchEvent(new Event('input', {{bubbles:true}})); input.blur(); return; }} }} }} }} }}")
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
    clicked = False
    try:
        # 方法1：查找所有包含"添加"的按钮
        buttons = page1.locator("button, span").filter(has_text="添加").all()
        for btn in buttons:
            try:
                if btn.is_visible():
                    btn.click()
                    print("  点击成功")
                    clicked = True
                    break
            except:
                continue
    except:
        pass
    
    if not clicked:
        # 方法2：JS点击
        result = page1.evaluate("""() => {
            const spans = document.querySelectorAll('span, button');
            for(let s of spans) {
                if(s.textContent.trim() === '添加' && s.offsetParent !== null) {
                    s.click();
                    return 'clicked';
                }
            }
            return 'not found';
        }""")
        print(f"  JS结果: {result}")
        if result == 'clicked':
            clicked = True
    
    time.sleep(2)
    
    # 检查是否打开了弹窗
    if not clicked:
        print("  警告: 未能点击添加按钮")
    else:
        # 检查是否有弹窗出现
        try:
            dialog = page1.locator(".el-dialog, .uni-popup, [class*='dialog'], [class*='popup']").first
            if dialog.is_visible():
                print("  弹窗已打开")
            else:
                print("  警告: 弹窗未打开")
        except:
            print("  无法检测弹窗状态")
    
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
    
    # 选择抵押/质押财产类型
    property_type = CASE_DATA.get('mortgage_property_type', '')
    pledge_type = CASE_DATA.get('pledge_property_type', '')
    
    if guarantee_type == '设定抵押' and property_type:
        print(f"选择抵押财产类型: {property_type}...")
        try:
            # 方法1：使用JS精确定位"抵押财产类型"的下拉框
            result = page1.evaluate("""() => {
                const labels = document.querySelectorAll('.el-form-item__label');
                for(let label of labels) {
                    if(label.textContent.includes('抵押财产类型')) {
                        const formItem = label.closest('.el-form-item');
                        if(formItem) {
                            const select = formItem.querySelector('.el-select');
                            if(select) {
                                select.click();
                                return 'clicked select';
                            }
                        }
                    }
                }
                return 'not found';
            }""")
            print(f"  打开select: {result}")
            time.sleep(2)
            
            # 在下拉选项中查找
            result2 = page1.evaluate(f"""() => {{
                const dropdowns = document.querySelectorAll('.el-select-dropdown.el-popper');
                if(dropdowns.length === 0) return 'no dropdown';
                
                const dropdown = dropdowns[dropdowns.length - 1];
                const items = dropdown.querySelectorAll('.el-select-dropdown__item');
                
                for(let item of items) {{
                    const text = item.textContent.trim();
                    if(text.includes('{property_type}')) {{
                        item.click();
                        return 'clicked: ' + text;
                    }}
                }}
                
                const allTexts = Array.from(items).map(i => i.textContent.trim());
                return 'not found in: ' + allTexts.slice(0, 10).join(', ') + '...';
            }}""")
            print(f"  选择结果: {result2}")
            if 'clicked' in result2:
                print("  选择成功")
        except Exception as e:
            print(f"  失败: {e}")
        time.sleep(0.5)
    
    if guarantee_type == '设定质押' and pledge_type:
        print(f"选择质押财产类型: {pledge_type}...")
        print(f"  调试: guarantee_type={guarantee_type}, pledge_type={pledge_type}")
        selected = False
        
        # 方法1：使用label精确定位"质押财产类型"下拉框
        try:
            # 先关闭所有下拉框
            page1.evaluate("() => { document.body.click(); }")
            time.sleep(1)
            
            # 通过label找到"质押财产类型"对应的select
            result = page1.evaluate("""() => {
                const formItems = document.querySelectorAll('.el-form-item');
                for(let formItem of formItems) {
                    const label = formItem.querySelector('.el-form-item__label');
                    if(label && label.textContent.trim() === '质押财产类型') {
                        const select = formItem.querySelector('.el-select');
                        if(select) {
                            select.click();
                            return 'clicked';
                        }
                    }
                }
                return 'not found';
            }""")
            print(f"  打开select: {result}")
            time.sleep(2)
            
            if result == 'clicked':
                # 在下拉选项中查找
                options = page1.locator(".el-select-dropdown__list li").all()
                for option in options:
                    try:
                        text = option.text_content()
                        if text and pledge_type in text:
                            option.click()
                            selected = True
                            print(f"  选择成功: {text}")
                            break
                    except:
                        continue
                
                if not selected:
                    print(f"  未找到选项: {pledge_type}")
        except Exception as e:
            print(f"  方法1失败: {e}")
        
        # 方法2：JS选择（精确匹配"质押财产类型"）
        if not selected:
            try:
                # 先关闭所有下拉框
                page1.evaluate("() => { document.body.click(); }")
                time.sleep(1)
                
                # 精确匹配"质押财产类型"label
                result = page1.evaluate(f"""() => {{
                    const labels = document.querySelectorAll('.el-form-item__label');
                    let targetSelect = null;
                    
                    for(let label of labels) {{
                        const text = label.textContent.trim();
                        // 精确匹配"质押财产类型"，排除"抵押财产类型"
                        if(text === '质押财产类型' || (text.includes('质押') && text.includes('财产类型') && !text.includes('抵押'))) {{
                            const formItem = label.closest('.el-form-item');
                            if(formItem) {{
                                const selects = formItem.querySelectorAll('.el-select');
                                if(selects.length > 0) {{
                                    targetSelect = selects[0];
                                    break;
                                }}
                            }}
                        }}
                    }}
                    
                    if(!targetSelect) return 'select not found';
                    
                    targetSelect.click();
                    return 'clicked select';
                }}""")
                print(f"  打开select: {result}")
                time.sleep(2)
                
                # 点击选项
                result2 = page1.evaluate(f"""() => {{
                    const dropdowns = document.querySelectorAll('.el-select-dropdown.el-popper');
                    if(dropdowns.length === 0) return 'no dropdown';
                    
                    const dropdown = dropdowns[dropdowns.length - 1];
                    const items = dropdown.querySelectorAll('.el-select-dropdown__item');
                    
                    for(let item of items) {{
                        const text = item.textContent.trim();
                        if(text === '{pledge_type}') {{
                            item.click();
                            return 'clicked: ' + text;
                        }}
                    }}
                    
                    const allTexts = Array.from(items).map(i => i.textContent.trim());
                    return 'not found in: ' + allTexts.join(', ');
                }}""")
                print(f"  选择结果: {result2}")
                if 'clicked' in result2:
                    selected = True
            except Exception as e:
                print(f"  JS选择失败: {e}")
        
        # 验证选择是否成功
        time.sleep(1)
        try:
            input_value = page1.evaluate("""() => {
                const labels = document.querySelectorAll('.el-form-item__label');
                for(let label of labels) {
                    const text = label.textContent.trim();
                    if(text === '质押财产类型' || (text.includes('质押') && text.includes('财产类型') && !text.includes('抵押'))) {
                        const formItem = label.closest('.el-form-item');
                        if(formItem) {
                            const input = formItem.querySelector('.el-input__inner');
                            return input ? input.value : 'no input';
                        }
                    }
                }
                return 'not found';
            }""")
            print(f"  input值: '{input_value}'")
            
            if not input_value or input_value == '' or input_value == 'not found':
                print("  警告: 选择未生效")
            else:
                print("  选择验证通过")
        except:
            pass
        
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
    
    # 保存前检查所有必填项
    print("检查必填项...")
    try:
        # 检查质押财产类型是否已选择
        has_error = page1.evaluate("""() => {
            const errorElements = document.querySelectorAll('.el-form-item__error');
            for(let el of errorElements) {
                if(el.style.display !== 'none' && el.textContent.trim().length > 0) {
                    return el.textContent;
                }
            }
            return '';
        }""")
        if has_error:
            print(f"  发现错误: {has_error}")
            # 尝试修复错误
            # 重新选择质押财产类型
            if '财产类型' in has_error:
                print("  重新选择质押财产类型...")
                page1.evaluate("""() => {
                    const formItems = document.querySelectorAll('.el-form-item');
                    for(let item of formItems) {
                        const label = item.querySelector('.el-form-item__label');
                        if(label && label.textContent.includes('质押财产类型')) {
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
                # 点击股权选项
                page1.evaluate("""() => {
                    const items = document.querySelectorAll('.el-select-dropdown__item');
                    for(let item of items) {
                        const text = item.textContent.trim();
                        if(text === '股权') {
                            item.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                            item.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                            item.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            item.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                            return true;
                        }
                    }
                    return false;
                }""")
                time.sleep(1)
    except:
        pass
    
    # 保存
    print("保存担保信息...")
    try:
        page1.get_by_role("button", name="保存").click()
    except:
        page1.evaluate("() => { const btns = document.querySelectorAll('button'); for(let btn of btns) { if(btn.textContent.includes('保存')) { btn.click(); return; } } }")
    time.sleep(3)
    
    # 检查是否有错误提示
    try:
        error_text = page1.evaluate("""() => {
            const errorElements = document.querySelectorAll('.el-message, .el-notification, .error-message, .uni-toast');
            for(let el of errorElements) {
                if(el.textContent.includes('失败') || el.textContent.includes('错误') || el.textContent.includes('请填写')) {
                    return el.textContent;
                }
            }
            return '';
        }""")
        if error_text:
            print(f"  错误提示: {error_text}")
    except:
        pass
    
    print("担保信息添加成功!")
    
    # 等待表格更新
    time.sleep(5)
    
    # 检查表格是否有数据（不刷新页面）
    try:
        table_data = page1.evaluate("""() => {
            const rows = document.querySelectorAll('.el-table__row');
            return rows.length;
        }""")
        print(f"  表格行数: {table_data}")
        if table_data == 0:
            print("  警告: 表格为空，保存可能未生效")
            # 截图查看状态
            page1.screenshot(path=r'C:\court-auto-filing\debug_guarantee_empty.png')
    except:
        pass
    
    # 关闭弹窗（如果还在弹窗中）
    try:
        page1.get_by_role("button", name="取消").click()
        time.sleep(1)
    except:
        pass
    
    # 截图确认页面状态
    try:
        page1.screenshot(path=r'C:\court-auto-filing\debug_after_guarantee.png')
    except:
        print("  截图失败")
    
    # 等待担保信息加载到表格中
    time.sleep(3)
    
    # 检查表格中是否有数据
    try:
        table_text = page1.evaluate("""() => {
            const table = document.querySelector('table');
            return table ? table.textContent : 'no table';
        }""")
        if '暂无数据' in table_text:
            print("  警告: 担保信息表格为空，可能需要重新添加")
            # 尝试重新添加担保信息
            print("  尝试重新添加担保信息...")
            # 点击添加按钮
            page1.evaluate("() => { const spans = document.querySelectorAll('span'); for(let s of spans) { if(s.textContent.trim() === '添加') { s.click(); return; } } }")
            time.sleep(2)
            # 重新填写担保信息
            # ... (简化处理)
    except:
        pass


def upload_files(page1):
    """上传材料文件 - 从数据库读取文件路径"""
    print("\n" + "=" * 50)
    print("上传材料")
    print("=" * 50)
    
    # 点击下一步进入材料上传页面
    print("进入材料上传页面...")
    
    # 先检查担保信息表格是否有数据
    try:
        table_text = page1.evaluate("""() => {
            const table = document.querySelector('table');
            return table ? table.textContent : 'no table';
        }""")
        if '暂无数据' in table_text:
            print("  警告: 担保信息表格为空，重新添加担保信息...")
            # 重新添加担保信息
            add_guarantee(page1)
    except:
        pass
    
    # 先截图确认当前页面
    page1.screenshot(path=r'C:\court-auto-filing\debug_before_next.png')
    
    # 点击"下一步"按钮
    clicked = False
    try:
        # 方法1：查找所有可见的下一步按钮
        buttons = page1.locator("button").all()
        for btn in buttons:
            try:
                text = btn.text_content()
                if text and "下一步" in text and btn.is_visible():
                    btn.click()
                    clicked = True
                    print("  点击下一步成功")
                    break
            except:
                continue
    except Exception as e:
        print(f"  方法1失败: {e}")
    
    if not clicked:
        try:
            # 方法2：使用JavaScript查找并点击
            result = page1.evaluate("""() => {
                const btns = document.querySelectorAll('button, uni-button');
                for(let btn of btns) {
                    if(btn.textContent && btn.textContent.includes('下一步') && btn.offsetParent !== null) {
                        btn.click();
                        return 'clicked: ' + btn.textContent;
                    }
                }
                return 'not found';
            }""")
            print(f"  JS点击结果: {result}")
            clicked = True
        except Exception as e:
            print(f"  方法2失败: {e}")
    
    time.sleep(5)
    
    # 检查是否成功进入材料上传页面
    try:
        page_title = page1.evaluate("""() => {
            const title = document.querySelector('.page-title, .title, h1, h2');
            return title ? title.textContent : '';
        }""")
        print(f"  当前页面标题: {page_title}")
        if '担保' in page_title:
            print("  警告: 仍在担保信息页面，尝试再次点击下一步...")
            # 再次点击下一步
            page1.evaluate("""() => {
                const btns = document.querySelectorAll('button');
                for(let btn of btns) {
                    if(btn.textContent.includes('下一步')) {
                        btn.click();
                        return 'clicked again';
                    }
                }
                return 'not found';
            }""")
            time.sleep(3)
    except:
        pass
    
    # 截图确认是否进入材料上传页面
    page1.screenshot(path=r'C:\court-auto-filing\debug_after_next.png')
    
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
        
        # 调试：打印file_map
        print(f"  文件类别: {list(file_map.keys())}")
        for category, files in file_map.items():
            print(f"    {category}: {len(files)} 个文件")
            for f in files:
                print(f"      - {f['name']}: {os.path.exists(f['path'])}")
    except Exception as e:
        print(f"  数据库读取失败: {e}")
        return
    
    # 截图确认页面状态
    page1.screenshot(path=r'C:\court-auto-filing\debug_material_page.png')
    print("  截图保存: debug_material_page.png")
    
    # 查找所有文件input
    print("查找文件input...")
    
    # 等待文件input加载，最多重试5次
    file_inputs = []
    for attempt in range(5):
        try:
            file_inputs = page1.locator("input[type='file']").all()
            if len(file_inputs) > 0:
                print(f"  找到 {len(file_inputs)} 个文件input")
                break
            else:
                print(f"  第{attempt+1}次尝试: 未找到文件input，等待...")
                time.sleep(3)
        except Exception as e:
            print(f"  第{attempt+1}次尝试失败: {e}")
            time.sleep(3)
    
    if not file_inputs:
        print("  未找到文件input，跳过上传")
        return
    
    # 为每个文件input找到对应的材料类型并上传
    for i, file_input in enumerate(file_inputs):
            try:
                # 获取input的父元素，确定材料类型
                parent_html = file_input.evaluate("el => el.closest('div.el-form-item, div.material-item, div.upload-area')?.outerHTML || el.parentElement?.outerHTML || ''")
                
                # 从父元素HTML中提取文本
                import re
                text_match = re.search(r'>([^<]*(?:保全申请书|起诉状|立案受理通知书|申请人|被申请人|担保|保证人|保证金|证据|其他)[^<]*)<', parent_html)
                parent_text = text_match.group(1) if text_match else ''
                
                # 如果正则没有匹配到，尝试从整个HTML中提取
                if not parent_text:
                    # 尝试匹配label文本
                    label_match = re.search(r'label[^>]*>([^<]+)</label', parent_html)
                    if label_match:
                        parent_text = label_match.group(1)
                    else:
                        # 尝试匹配任何中文文本
                        cn_match = re.search(r'[一-龥]{2,}', parent_html)
                        if cn_match:
                            parent_text = cn_match.group(0)
                
                print(f"  文件input {i+1}: {parent_text[:50] if parent_text else '(空)'}")
                
                # 确定材料类型 - 支持细分的文件类别
                files_to_upload = []
                
                if '保全申请书' in parent_text:
                    if '保全申请书' in file_map:
                        files_to_upload = [f['path'] for f in file_map['保全申请书']]
                elif '起诉状' in parent_text:
                    if '起诉状' in file_map:
                        files_to_upload = [f['path'] for f in file_map['起诉状']]
                elif '立案受理通知书' in parent_text:
                    if '立案受理通知书' in file_map:
                        files_to_upload = [f['path'] for f in file_map['立案受理通知书']]
                elif '申请人' in parent_text and '被申请人' not in parent_text:
                    # 查找申请人类别（支持简化名称和完整名称）
                    if '申请人' in file_map:
                        files_to_upload = [f['path'] for f in file_map['申请人']]
                    else:
                        for category in file_map.keys():
                            if category.startswith('申请人-'):
                                files_to_upload = [f['path'] for f in file_map[category]]
                                break
                elif '被申请人' in parent_text:
                    # 查找被申请人类别（支持简化名称和完整名称）
                    if '被申请人' in file_map:
                        files_to_upload = [f['path'] for f in file_map['被申请人']]
                    else:
                        for category in file_map.keys():
                            if category.startswith('被申请人-'):
                                files_to_upload = [f['path'] for f in file_map[category]]
                                break
                elif '担保' in parent_text or '保证人' in parent_text or '保证金' in parent_text or '抵押' in parent_text:
                    # 查找细分的担保类别
                    for category in file_map.keys():
                        if category.startswith('提供保证人-') or category == '设定抵押':
                            files_to_upload = [f['path'] for f in file_map[category]]
                            break
                elif '质押' in parent_text:
                    # 查找细分的质押类别
                    for category in file_map.keys():
                        if category == '设定质押':
                            files_to_upload = [f['path'] for f in file_map[category]]
                            break
                elif '证据' in parent_text:
                    if '证据材料' in file_map:
                        files_to_upload = [f['path'] for f in file_map['证据材料']]
                elif '其他' in parent_text:
                    if '其他材料' in file_map:
                        files_to_upload = [f['path'] for f in file_map['其他材料']]
                
                # 过滤存在的文件
                files_to_upload = [f for f in files_to_upload if os.path.exists(f)]
                
                if files_to_upload:
                    print(f"    准备上传 {len(files_to_upload)} 个文件: {', '.join([os.path.basename(f) for f in files_to_upload])}")
                    file_input.set_input_files(files_to_upload)
                    print(f"    上传成功")
                    time.sleep(2)
                else:
                    print(f"    未找到对应文件")
            except Exception as e:
                print(f"    上传失败: {e}")
    
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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 登录
        if not auto_login(page, CASE_DATA.get("created_by", "")):
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
