"""
法院自动立案系统 - MySQL数据库驱动版本
从数据库读取案件信息，自动填写在线立案/保全
用法: python final_auto_upload_db.py [案件编号]
"""
import os
import sys
import time
import re
import pymysql
from playwright.sync_api import sync_playwright

# ========== 数据库配置 ==========
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lijiayu123',
    'database': 'court_filing',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

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
    return {'case': case, 'properties': properties, 'files': files, 'agents': agents}

def update_case_status(case_no, status=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status = %s WHERE case_no = %s", (status, case_no))
    conn.commit()
    conn.close()

# ========== 全局变量存储案件数据 ==========
CASE_DATA = None
PROPERTY_DATA = None
FILES_DATA = None

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
    try:
        ocr = ddddocr.DdddOcr(show_ad=False)
        with open(img_path, 'rb') as f:
            img_bytes = f.read()
        
        result = ocr.classification(img_bytes)
        print(f"验证码识别结果: {result}")
        
        # 验证结果是否为4位字母数字
        if result and len(result) == 4 and result.isalnum():
            return result
        else:
            print(f"验证码识别结果异常: {result}")
            return None
    except Exception as e:
        print(f"验证码识别失败: {e}")
        return None


def auto_login(page):
    """自动登录"""
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
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
    phone_input.fill("13723715831")
    time.sleep(0.5)
    
    # 输入密码
    print("输入密码...")
    pwd_input = page.locator("input[type=\"password\"]")
    pwd_input.click()
    pwd_input.fill("HU1234pp")
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
        print("登录失败")
        return False


def create_preservation(page):
    """创建保全申请 - 支持诉前保全和诉讼保全"""
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
    
    # 等待页面加载完成
    print("等待页面加载...")
    page1.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 勾选阅读须知
    print("勾选阅读须知...")
    try:
        page1.get_by_role("radio", name="我已阅读网上保全须知").click(timeout=10000)
    except:
        # 尝试用JavaScript点击
        page1.evaluate("""() => {
            const radio = document.querySelector('uni-radio');
            if (radio) radio.click();
        }""")
    time.sleep(1)
    
    # 点击创建保全申请
    print("点击创建保全申请...")
    try:
        page1.get_by_role("button", name="创建保全申请").click(timeout=10000)
    except:
        page1.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('uni-button')).find(b => b.textContent.includes('创建保全申请'));
            if (btn) btn.click();
        }""")
    time.sleep(3)
    
    # 等待表单页面加载
    print("等待表单页面加载...")
    page1.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 选择保全类别（诉前保全/诉讼保全）
    preserve_category = CASE_DATA.get('preserve_category', '诉前保全')
    print(f"选择保全类别: {preserve_category}...")
    
    try:
        if preserve_category == '诉讼保全':
            # 先等待单选按钮出现
            page1.wait_for_selector('uni-radio:has-text("诉讼保全")', timeout=10000)
            page1.get_by_role("radio", name="诉讼保全").click(timeout=10000)
        else:
            page1.wait_for_selector('uni-radio:has-text("诉前保全")', timeout=10000)
            page1.get_by_role("radio", name="诉前保全").click(timeout=10000)
    except Exception as e:
        print(f"选择保全类别失败，尝试JavaScript: {e}")
        # 使用JavaScript选择
        page1.evaluate(f"""() => {{
            const radios = document.querySelectorAll('uni-radio');
            for (let radio of radios) {{
                if (radio.textContent.includes('{preserve_category}')) {{
                    radio.click();
                    break;
                }}
            }}
        }}""")
    time.sleep(1)
    
    # 选择申请法院
    print("选择申请法院...")
    court_input = page1.get_by_placeholder("选择申请法院")
    court_input.click()
    court_input.fill("广东")
    time.sleep(1)
    page1.get_by_text("广东省深圳市中级人民法院").click()
    time.sleep(0.5)
    
    # 输入保全金额
    print("输入保全金额...")
    amount_input = page1.get_by_placeholder("请输入您要申请的保全金额")
    amount_input.click()
    amount_input.fill(str(int(CASE_DATA['preserve_amount'])))
    time.sleep(0.5)
    
    # 诉讼保全特有字段：案件类型、案号、案由
    if preserve_category == '诉讼保全':
        print("填写诉讼保全特有信息...")
        
        # 案件类型
        if CASE_DATA.get('case_type'):
            print(f"选择案件类型: {CASE_DATA['case_type']}...")
            page1.get_by_role("radio", name=CASE_DATA['case_type']).click()
            time.sleep(0.5)
        
        # 案号
        if CASE_DATA.get('court_case_no'):
            print(f"填写案号: {CASE_DATA['court_case_no']}...")
            case_no_input = page1.get_by_placeholder("请输入案号")
            case_no_input.click()
            case_no_input.fill(CASE_DATA['court_case_no'])
            time.sleep(0.5)
        
        # 案由
        if CASE_DATA.get('case_reason'):
            print(f"选择案由: {CASE_DATA['case_reason']}...")
            reason_input = page1.get_by_placeholder("请选择案由")
            reason_input.click()
            time.sleep(0.5)
            page1.get_by_text(CASE_DATA['case_reason']).click()
            time.sleep(0.5)
    
    # 选择担保情况
    print("选择担保情况...")
    try:
        if CASE_DATA.get('has_guarantee'):
            page1.get_by_role("radio", name="有担保").click(timeout=10000)
        else:
            page1.get_by_role("radio", name="无担保").click(timeout=10000)
    except:
        pass
    time.sleep(0.5)
    
    # 选择提交身份人
    print("选择提交身份人...")
    try:
        submitter_type = CASE_DATA.get('submitter_type', '其他代理人')
        page1.get_by_role("radio", name=submitter_type).click(timeout=10000)
    except:
        pass
    time.sleep(0.5)
    
    # 选择申请人类型
    print("选择申请人类型...")
    try:
        page1.get_by_role("radio", name="律师").click(timeout=10000)
    except:
        pass
    time.sleep(0.5)
    
    # 点击创建保全
    print("点击创建保全...")
    try:
        page1.get_by_role("button", name="创建保全").click(timeout=10000)
    except:
        page1.evaluate("""() => {
            const btn = Array.from(document.querySelectorAll('uni-button')).find(b => b.textContent.includes('创建保全'));
            if (btn) btn.click();
        }""")
    time.sleep(3)
    
    print("保全申请创建成功!")
    return page1


def add_applicant(page1):
    """添加申请人"""
    print("\n" + "=" * 50)
    print("添加申请人")
    print("=" * 50)
    
    # 点击添加
    print("点击添加申请人...")
    page1.get_by_text("添加").first.click()
    time.sleep(2)
    
    # 输入姓名
    print("输入姓名...")
    name_input = page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox")
    name_input.click()
    name_input.fill(CASE_DATA['applicant_name'])
    time.sleep(0.5)
    
    # 输入身份证号
    print("输入身份证号...")
    id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
    id_input.click()
    id_input.fill(CASE_DATA['respondent_id'])
    time.sleep(0.5)
    
    # 选择性别
    print("选择性别...")
    page1.get_by_role("radio", name="男性").click()
    time.sleep(0.5)
    
    # 输入手机号
    print("输入手机号...")
    phone_input = page1.locator("#addSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
    phone_input.click()
    phone_input.fill(CASE_DATA['applicant_phone'])
    time.sleep(0.5)
    
    # 输入地址
    print("输入地址...")
    addr_input = page1.locator("div").filter(has_text=re.compile(r"^经常居住地$")).get_by_role("textbox")
    addr_input.click()
    addr_input.fill(CASE_DATA['applicant_address'])
    time.sleep(0.5)
    
    # 保存
    print("保存申请人...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("申请人添加成功!")


def add_respondent(page1):
    """添加被申请人"""
    print("\n" + "=" * 50)
    print("添加被申请人")
    print("=" * 50)
    
    # 点击添加（第二个添加按钮）
    print("点击添加被申请人...")
    
    # 策略1: 使用nth(1)
    try:
        add_buttons = page1.locator("text=添加").all()
        if len(add_buttons) >= 2:
            add_buttons[1].click()
            print("  ✓ 使用all()[1]点击")
        else:
            raise Exception("添加按钮不足2个")
    except Exception as e1:
        print(f"  策略1失败: {e1}")
        # 策略2: 查找被申请人区域的添加按钮
        try:
            # 查找包含"被申请人"文本的区域，然后找其中的添加按钮
            page1.locator("text=被申请人").first.click()
            time.sleep(1)
            page1.locator("button:has-text('添加')").first.click()
            print("  ✓ 使用区域查找点击")
        except Exception as e2:
            print(f"  策略2失败: {e2}")
            # 策略3: 使用JavaScript点击
            try:
                page1.evaluate("""() => {
                    const buttons = document.querySelectorAll('button, span, a');
                    for (let btn of buttons) {
                        if (btn.textContent.includes('添加') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                print("  ✓ 使用JS点击")
            except Exception as e3:
                print(f"  策略3失败: {e3}")
                raise
    
    time.sleep(2)
    
    # 输入姓名
    print("输入姓名...")
    name_input = page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox")
    name_input.click()
    name_input.fill(CASE_DATA['respondent_name'])
    time.sleep(0.5)
    
    # 输入身份证号
    print("输入身份证号...")
    id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
    id_input.click()
    id_input.fill(CASE_DATA['respondent_id'])
    time.sleep(0.5)
    
    # 选择性别
    print("选择性别...")
    page1.get_by_role("radio", name="男性").click()
    time.sleep(0.5)
    
    # 输入手机号
    print("输入手机号...")
    phone_input = page1.locator("#addBSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
    phone_input.click()
    phone_input.fill(CASE_DATA['respondent_phone'])
    time.sleep(0.5)
    
    # 保存
    print("保存被申请人...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("被申请人添加成功!")


def add_property(page1):
    """添加财产线索"""
    print("\n" + "=" * 50)
    print("添加财产线索")
    print("=" * 50)
    
    # 点击添加
    print("点击添加财产...")
    page1.locator("span").filter(has_text=re.compile(r"^添加$")).click()
    time.sleep(2)
    
    # 选择财产类型
    print("选择财产类型...")
    page1.get_by_placeholder("请选择财产类型").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="存款").click()
    time.sleep(0.5)
    
    # 选择财产所有人
    print("选择财产所有人...")
    page1.get_by_placeholder("请选择财产所有人").click()
    time.sleep(1)
    page1.locator("li").filter(has_text=CASE_DATA['respondent_name']).click()
    time.sleep(0.5)
    
    # 选择开户行所在地
    print("选择开户行所在地...")
    location_input = page1.locator("div").filter(has_text=re.compile(r"^开户行所在地")).get_by_role("textbox")
    location_input.click()
    time.sleep(1)
    page1.get_by_text("广东", exact=True).click()
    time.sleep(0.5)
    
    # 输入开户银行名称
    print("输入开户银行...")
    bank_input = page1.locator("div").filter(has_text=re.compile(r"^开户银行名称$")).get_by_role("textbox")
    bank_input.click()
    bank_input.fill(PROPERTY_DATA[0]['bank_name'])
    time.sleep(0.5)
    
    # 输入开户账号
    print("输入开户账号...")
    account_input = page1.locator("div").filter(has_text=re.compile(r"^开户账号$")).get_by_role("textbox")
    account_input.click()
    account_input.fill(PROPERTY_DATA[0]['bank_account'])
    time.sleep(0.5)
    
    # 输入数额
    print("输入数额...")
    amount_input = page1.locator("div").filter(has_text=re.compile(r"^数额$")).get_by_role("textbox")
    amount_input.click()
    amount_input.fill(str(int(PROPERTY_DATA[0]['amount'])))
    time.sleep(0.5)
    
    # 选择币种
    print("选择币种...")
    page1.get_by_placeholder("请选择单位").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="人民币").click()
    time.sleep(0.5)
    
    # 输入财产价值
    print("输入财产价值...")
    value_input = page1.locator("form div").filter(has_text="财产价值￥ 元").get_by_role("textbox")
    value_input.click()
    value_input.fill(str(int(CASE_DATA['guarantee_value'])))
    time.sleep(0.5)
    
    # 保存
    print("保存财产线索...")
    page1.get_by_role("button", name="保存", exact=True).click()
    time.sleep(2)
    
    print("财产线索添加成功!")


def add_guarantee(page1):
    """添加担保信息"""
    print("\n" + "=" * 50)
    print("添加担保信息")
    print("=" * 50)
    
    # 点击下一步
    print("点击下一步...")
    page1.get_by_role("button", name="下一步").click()
    time.sleep(2)
    
    # 点击添加
    print("点击添加担保...")
    page1.locator("span").filter(has_text="添加").locator("i").click()
    time.sleep(2)
    
    # 选择担保方式
    print("选择担保方式...")
    page1.get_by_placeholder("请选择").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="提供保证人").click()
    time.sleep(0.5)
    
    # 输入担保人
    print("输入担保人...")
    guarantor_input = page1.get_by_placeholder("请输入担保人")
    guarantor_input.click()
    guarantor_input.fill(CASE_DATA['applicant_name'])
    time.sleep(0.5)
    
    # 输入担保名称
    print("输入担保名称...")
    name_input = page1.get_by_placeholder("请输入担保名称")
    name_input.click()
    name_input.fill("现金")
    time.sleep(0.5)
    
    # 输入担保价值
    print("输入担保价值...")
    value_input = page1.locator("#addDBXX div").filter(has_text="担保价值 元").get_by_role("textbox")
    value_input.click()
    value_input.fill(str(int(CASE_DATA['guarantee_value'])))
    time.sleep(0.5)
    
    # 保存
    print("保存担保信息...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("担保信息添加成功!")


def main():
    """主函数 - 数据库版本"""
    import sys
    global CASE_DATA, PROPERTY_DATA, FILES_DATA
    
    # 从命令行参数获取案件编号
    case_no = sys.argv[1] if len(sys.argv) > 1 else "保全2026001"
    
    # 从数据库读取案件数据
    data = get_case_data(case_no)
    if not data:
        print(f"❌ 未找到案件: {case_no}")
        return
    
    CASE_DATA = data['case']
    PROPERTY_DATA = data['properties']
    FILES_DATA = data['files']
    
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
