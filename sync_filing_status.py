import os
import easyocr
from playwright.sync_api import sync_playwright
import time
import re
import pymysql
import sys



CASE_DATA = {}



import json
import re
from datetime import datetime

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'lijiayu123'),
    'database': os.environ.get('DB_NAME', 'court_filing'),
    'charset': 'utf8mb4'
}

STATUS_DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'lijiayu123'),
    'database': 'court_filing_status',
    'charset': 'utf8mb4'
}

def get_account_sync_status(username, category):
    """获取账号某类别的同步状态,返回是否首次同步"""
    try:
        conn = pymysql.connect(**STATUS_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_sync_time, total_cases FROM account_sync_log WHERE username = %s AND category = %s",
            (username, category)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return False, row[0], row[1]  # 不是首次,返回最后同步时间和案件数
        return True, None, 0  # 首次同步
    except Exception as e:
        print("获取同步状态失败:", e)
        return True, None, 0

def update_account_sync_status(username, category, total_cases):
    """更新账号同步记录"""
    try:
        conn = pymysql.connect(**STATUS_DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO account_sync_log (username, category, last_sync_time, total_cases)
               VALUES (%s, %s, NOW(), %s)
               ON DUPLICATE KEY UPDATE last_sync_time = NOW(), total_cases = %s""",
            (username, category, total_cases, total_cases)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("更新同步状态失败:", e)

def load_system_users():
    """从数据库加载系统用户列表(排除admin),用于轮动抓取"""
    try:
        conn = pymysql.connect(
            host="localhost", user="root", password="lijiayu123",
            database="court_filing", charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, user_type FROM system_users WHERE username != 'admin'")
        users = [{'username': row[0], 'password': row[1], 'user_type': row[2]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print("加载系统用户失败:", e)
        return []

def load_system_config():
    """从数据库加载系统配置(登录账号,密码,用户类型)"""
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
        return config
    except Exception as e:
        print(f"加载系统配置失败: {e}")
        return {}


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
        print("未找到验证码图片,尝试截图查找...")
        # 截图查看页面
        page.screenshot(path="login_page.png")
        return None
    
    # 截图
    img_path = "captcha_codegen.png"
    time.sleep(0.5)  # 等待图片加载
    try:
        captcha_img.screenshot(path=img_path)
    except:
        # 如果截图失败,尝试直接截图整个页面然后裁剪
        page.screenshot(path="full_page.png")
        return None
    
    # OCR识别
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open(img_path, 'rb') as f:
        img_bytes = f.read()
    
    result = ocr.classification(img_bytes)
    print(f"验证码识别结果: {result}")
    return result



def auto_login(page, target_username=None, max_retries=10):
    """自动登录 - 带重试机制"""
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    for attempt in range(max_retries):
        print(f"\n第 {attempt + 1} 次尝试...")
        
        # 进入登录页
        page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        time.sleep(0.5)
        
        # 选择律师用户
        print("选择律师用户...")
        page.get_by_text("律师用户").click()
        time.sleep(0.5)
        
        # 加载可用账号列表
        users = load_system_users()
        if not users:
            print("没有可用的登录账号")
            return None
        
        # 固定使用13723715831账号
        if target_username is None:
            target_username = '13723715831'
        user = None
        for u in users:
            if u['username'] == target_username:
                user = u
                break
        
        if not user:
            print("未找到指定账号 %s,使用第一个可用账号" % target_username)
            user = users[0]
        
        login_username = user['username']
        login_password = user['password']
        login_user_type = user['user_type']
        print("使用账号登录: %s, 身份: %s" % (login_username, login_user_type))
        
        # 输入手机号
        print("输入手机号...")
        phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
        phone_input.click()
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
                # 备用方法:直接用JavaScript设置验证码
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
            print("登录失败,准备重试...")
            time.sleep(0.5)
            continue
    
    print(f"\n登录失败,已达到最大重试次数 ({max_retries})")
    return False

def init_status_db():
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cur:
            cur.execute('CREATE DATABASE IF NOT EXISTS court_filing_status CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            cur.execute('USE court_filing_status')
            cur.execute("""
                CREATE TABLE IF NOT EXISTS filing_status (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_no VARCHAR(50) NOT NULL COMMENT '案件编号',
                    case_name VARCHAR(200) COMMENT '案件名称',
                    court_name VARCHAR(100) COMMENT '法院名称',
                    status VARCHAR(50) COMMENT '立案状态',
                    status_code VARCHAR(20) COMMENT '状态代码',
                    review_opinion TEXT COMMENT '审核意见',
                    apply_date DATE COMMENT '申请日期',
                    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间',
                    raw_data JSON COMMENT '原始数据',
                    INDEX idx_case_no (case_no),
                    INDEX idx_status (status),
                    INDEX idx_sync_time (sync_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_cases INT DEFAULT 0,
                    updated_cases INT DEFAULT 0,
                    error_msg TEXT,
                    INDEX idx_sync_time (sync_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        print("状态数据库初始化完成")
    finally:
        conn.close()

def save_status(case_no, case_name, court_name, status, status_code, review_opinion, apply_date, raw_data, case_category='审判'):
    conn = pymysql.connect(**STATUS_DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # 根据类别选择表名
            table_map = {
                '审判': 'filing_status_trial',
                '执行': 'filing_status_execution',
                '保全': 'filing_status_preservation',
                '调解': 'filing_status_mediation',
                '破产': 'filing_status_bankruptcy',
                '信访': 'filing_status_petition'
            }
            table_name = table_map.get(case_category, 'filing_status')
            
            # 先查询案件是否存在
            cur.execute(f"SELECT id FROM {table_name} WHERE case_no = %s", (case_no,))
            exists = cur.fetchone() is not None
            
            is_new_val = 0 if exists else 1
            
            cur.execute(f"""
                INSERT INTO {table_name}
                (case_no, case_name, court_name, status, status_code, review_opinion, apply_date, raw_data, sync_time, is_new)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                ON DUPLICATE KEY UPDATE
                case_name = VALUES(case_name),
                court_name = VALUES(court_name),
                status = VALUES(status),
                status_code = VALUES(status_code),
                review_opinion = VALUES(review_opinion),
                apply_date = VALUES(apply_date),
                raw_data = VALUES(raw_data),
                sync_time = NOW(),
                is_new = IF(is_new = 1, 1, VALUES(is_new))
            """, (case_no, case_name, court_name, status, status_code, review_opinion, apply_date, json.dumps(raw_data, ensure_ascii=False), is_new_val))
        conn.commit()
    finally:
        conn.close()


def update_main_db(case_no, status, review_opinion):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            status_map = {
                '待审核': 0,
                '审核通过': 1,
                '审核不通过': 2,
                '待补充材料': 3,
                '已立案': 1,
                '已退回': 2,
            }
            status_int = status_map.get(status, 0)
            cur.execute("""
                UPDATE cases 
                SET status = %s, filing_status = %s, remark = CONCAT(IFNULL(remark, ''), '\n[', NOW(), '] ', %s)
                WHERE case_no = %s
            """, (status_int, status, review_opinion or status, case_no))
            return cur.rowcount
    finally:
        conn.close()

def parse_status_text(status_text):
    status_map = {
        '审核不通过': 'rejected',
        '待审核': 'pending',
        '待补充材料': 'supplement',
        '审核通过': 'approved',
        '已立案': 'filed',
        '已退回': 'returned',
    }
    for key, code in status_map.items():
        if key in status_text:
            return key, code
    return status_text, 'unknown'

def parse_cases_from_html(html):
    """从HTML中解析案件数据"""
    cases = []
    
    # 查找所有案件卡片
    case_pattern = r'class="fd-case-item"[^>]*>(.*?)class="fd-case-space-btn"'
    case_blocks = re.findall(case_pattern, html, re.DOTALL)
    
    for block in case_blocks:
        # 提取状态
        status_match = re.search(r'class="fd-header-status[^"]*">([^<]+)', block)
        status = status_match.group(1).strip() if status_match else ''
        
        # 提取案件名称
        title_match = re.search(r'class="fd-header-ajmc">([^<]+)', block)
        title = title_match.group(1).strip() if title_match else ''
        
        # 提取字段
        court = ''
        date = ''
        opinion = ''
        
        field_pattern = r'class="fd-field-item"[^>]*>(.*?)</uni-view>\s*</uni-view>'
        fields = re.findall(field_pattern, block, re.DOTALL)
        for field in fields:
            label_match = re.search(r'class="fd-field-lable"[^>]*>([^<]+)', field)
            value_match = re.search(r'class="fd-field-value"[^>]*>([^<]+)', field)
            if label_match and value_match:
                label = label_match.group(1).strip()
                value = value_match.group(1).strip()
                if '法院' in label:
                    court = value
                elif '申请' in label or '立案' in label:
                    date = value
                elif '审核' in label or '意见' in label:
                    opinion = value
        
        if status and title:
            cases.append({
                'status': status,
                'title': title,
                'court': court,
                'date': date,
                'opinion': opinion
            })
    
    return cases

def sync_category(page, category, full_sync=False, batch_start=1, skip_verify_once=False):
    """同步单个类别的案件(支持翻页)"""
    # full_sync=True: 全量抓取所有页
    # full_sync=False: 增量抓取,只抓前30页(最近数据)
    print("\n===== 同步 [%s] 类别 =====" % category)
    
    try:
        categories = ['审判', '执行', '保全', '调解', '破产', '信访']
        if category not in categories:
            print("  未知类别: %s" % category)
            return 0
        
        # 点击标签
        js_code = """
        (category) => {
            const items = document.querySelectorAll('.segmented-control__item');
            for (let item of items) {
                const text = item.textContent.trim();
                if (text === category) {
                    item.click();
                    return {success: true, method: 'segmented-control', text: text};
                }
            }
            return {success: false};
        }
        """
        clicked = page.evaluate(js_code, category)
        
        print("  点击结果:", clicked)
        time.sleep(0.5)
        
        # 保全类需要额外等待页面加载
        if category == '保全':
            print("  等待保全页面加载...")
            time.sleep(8)
        
        
        total = 0
        page_num = batch_start if category == '审判' else 1
        seen_cases = set() if category == '审判' else None
        
        # 全量模式:审判类每200页重启浏览器,其他类抓取50页
        max_pages = 50
        page_batch_size = 50
        current_batch_start = batch_start
        
        while page_num <= max_pages:
            print("  正在抓取第 %d 页..." % page_num)
            
            # 获取页面内容(保全类需要截图,其他类直接获取HTML)
            if category == '保全':
                screenshot_path = r'C:\court-auto-filing\screenshots\my_cases_preservation_p%d.png' % page_num
                page.screenshot(path=screenshot_path)
            html = page.content()
            # 保全类使用OCR识别
            if category == '保全':
                print("  使用OCR识别保全页面...")
                cases = []
                try:
                    reader = get_ocr_reader()
                    screenshot_path = r'C:\court-auto-filing\screenshots\my_cases_preservation_p%d.png' % page_num
                    
                    ocr_result = reader.readtext(screenshot_path)
                    ocr_texts = [detection[1] for detection in ocr_result]
                    
                    print("  OCR识别到 %d 条文本" % len(ocr_texts))
                    
                    # 解析OCR文本
                    ocr_cases = parse_preservation_from_ocr(ocr_texts)
                    print("  解析到 %d 条案件" % len(ocr_cases))
                    
                    for ocr_case in ocr_cases:
                        cases.append({
                            'case_no': ocr_case.get('case_no', ''),
                            'title': ocr_case.get('case_no', '') or ocr_case.get('defendant', '未知'),
                            'status': ocr_case.get('status', '未知'),
                            'court': ocr_case.get('court', '未知法院'),
                            'date': ocr_case.get('apply_date', datetime.now().strftime('%Y-%m-%d')),
                            'opinion': '',
                            'case_type': '财产保全'
                        })
                except Exception as e:
                    print("  OCR识别失败:", str(e))
            else:
                cases = parse_cases_from_html(html)
            
            print("  第%d页获取到 %d 条案件" % (page_num, len(cases)))
            
            if not cases:
                print("  当前页无数据,结束")
                break
            
            # 审判类:全局循环检测
            if category == '审判' and seen_cases is not None:
                case_keys = [c.get('title','') + '|' + c.get('court','') for c in cases if c.get('title')]
                if case_keys and all(k in seen_cases for k in case_keys):
                    print("  当前页数据已全部存在,停止抓取(数据循环)")
                    break
                for k in case_keys:
                    seen_cases.add(k)
            
            # 检测与上一页数据是否完全相同(仅非审判类别)
            if category != '审判' and page_num > 1:
                current_page_keys = [c.get('title','') + '|' + c.get('court','') + '|' + c.get('date','') for c in cases]
                if current_page_keys == last_page_keys:
                    print("  本页数据与上一页完全相同,结束翻页")
                    break
                last_page_keys = current_page_keys
            else:
                last_page_keys = [c.get('title','') + '|' + c.get('court','') + '|' + c.get('date','') for c in cases]
            
            for case in cases:
                # 优先使用J编号作为case_no
                case_no = case.get('case_no', '')
                print("    MAIN_LOOP: case_no='%s', title='%s', defendant='%s'" % (case_no, case.get('title', ''), case.get('defendant', '')))
                if not case_no:
                    # 从title中提取J编号
                    case_no_match = re.search(r'J[A-Z0-9]+', case.get('title', ''))
                    case_no = case_no_match.group(0) if case_no_match else ''
                
                # 如果还是为空，使用title的MD5作为case_no
                if not case_no:
                    import hashlib
                    case_no = 'AUTO_' + hashlib.md5(case['title'].encode()).hexdigest()[:16]
                
                # 保全类case_name使用编号格式
                if category == '保全':
                    if case_no:
                        case['title'] = case_no
                    else:
                        case['title'] = '保全-' + case.get('defendant', '未知')[:30]
                
                status_text, status_code = parse_status_text(case['status'])
                
                # 日期字段兼容:date或apply_date
                apply_date = case.get('date', '') or case.get('apply_date', '')
                
                save_status(
                    case_no=case_no,
                    case_name=case['title'],
                    court_name=case.get('court', ''),
                    status=status_text,
                    status_code=status_code,
                    review_opinion=case.get('opinion', ''),
                    apply_date=apply_date if apply_date else None,
                    raw_data=case,
                    case_category=category
                )
                
                total += 1
                print("    [%s][%s] %s | 法院:%s | 日期:%s" % (category, status_text, case['title'], case.get('court',''), case.get('date','')))
            
            # 点击下一页
            next_page = page_num + 1
            if next_page > max_pages:
                print("  已达到最大页数")
                break
            
            if category == '保全':
                # 保全类使用坐标点击翻页
                page_coords = {
                    1: (1555, 1036), 2: (1593, 1036), 3: (1632, 1036),
                    4: (1670, 1036), 5: (1708, 1036), 6: (1716, 1036),
                    7: (1724, 1036), 8: (1732, 1036), 9: (1740, 1036),
                    10: (1748, 1036),
                }
                if next_page in page_coords:
                    x, y = page_coords[next_page]
                    print("  点击页码 %d (%d, %d)..." % (next_page, x, y))
                    page.mouse.click(x, y)
                    time.sleep(10)
                else:
                    print("  未知页码,跳过")
                    break
            else:
                # 审判/执行/调解/破产/信访类使用定位器翻页
                # 审判类:使用全局重复检测,不依赖相邻页对比
                if category == '审判':
                    try:
                        next_btn = page.locator("text=下一页").or_(page.locator("text=>")).first
                        if next_btn.is_visible(timeout=5000) and next_btn.is_enabled(timeout=5000):
                            print("  点击下一页...")
                            next_btn.click()
                            time.sleep(3)
                            flipped = True
                        else:
                            print("  没有下一页按钮,结束")
                            break
                    except Exception as e:
                        print("  翻页失败: %s" % e)
                        break
                else:
                    retry_count = 0
                    max_retry = 5
                    flipped = False
                    while retry_count < max_retry:
                        try:
                            next_btn = page.locator("text=下一页").or_(page.locator("text=>")).first
                            if next_btn.is_visible(timeout=5000) and next_btn.is_enabled(timeout=5000):
                                print("  点击下一页...")
                                prev_titles = [c.get('title','') + '|' + c.get('court','') + '|' + c.get('date','') for c in cases]
                                next_btn.click()
                                time.sleep(3)
                                new_html = page.content()
                                new_cases = parse_cases_from_html(new_html)
                                new_titles = [c.get('title','') for c in new_cases]
                                if new_titles and new_titles != prev_titles:
                                    flipped = True
                                    break
                                else:
                                    retry_count += 1
                                    print("  翻页后数据未变化,重试(%d/%d)" % (retry_count, max_retry))
                                    time.sleep(5)
                            else:
                                print("  没有下一页按钮,结束")
                                break
                        except Exception as e:
                            retry_count += 1
                            err_msg = str(e)
                            if 'Timeout' in err_msg:
                                print("  翻页按钮检测超时,直接尝试点击...")
                                try:
                                    next_btn = page.locator("text=下一页").or_(page.locator("text=>")).first
                                    next_btn.click(timeout=10000)
                                    time.sleep(3)
                                    flipped = True
                                    break
                                except Exception as e2:
                                    print("  点击也失败: %s" % e2)
                            else:
                                print("  翻页失败(%d/%d): %s" % (retry_count, max_retry, e))
                            if retry_count >= max_retry:
                                print("  翻页重试耗尽,结束")
                                break
                            time.sleep(5)
                    if not flipped and retry_count >= max_retry:
                        break
            
            page_num += 1
            time.sleep(0.5)
            
            # 审判类每200页重启浏览器,避免翻页循环
            if False:  # 禁用批次重启
                print("  [%s] 已达到批次上限(%d页),重启浏览器继续..." % (category, page_batch_size))
                break
        
        print("[%s] 本批次抓取 %d 条案件" % (category, total))
        return total
    except Exception as e:
        print("[%s] 同步出错: %s" % (category, str(e)))
        import traceback
        traceback.print_exc()
        return 0

def sync_filing_status(full_sync=False):
    print("开始同步立案状态... %s" % datetime.now())
    print("模式: %s" % ('全量同步' if full_sync else '增量同步'))
    print("注意:全量同步可能需要较长时间,请耐心等待...")
    
    categories = ['审判', '执行', '保全', '调解', '破产', '信访']
    
    # 限制Chromium内存使用不超过6GB
    os.environ["PLAYWRIGHT_CHROMIUM_ARGS"] = "--js-flags=--max-old-space-size=6144 --disable-dev-shm-usage"
    
    # 加载所有账号
    users = load_system_users()
    if not users:
        print("没有可用的登录账号")
        return
    
    print(f"发现 {len(users)} 个账号,开始轮动同步...")
    
    for user_idx, user in enumerate(users):
        username = user['username']
        grand_total = 0
        print("="*60)
        print("账号 %d/%d: %s" % (user_idx+1, len(users), username))
        print("="*60)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--js-flags=--max-old-space-size=6144', '--disable-dev-shm-usage', '--disable-gpu', '--no-sandbox'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            try:
                if not auto_login(page, target_username=username):
                    print(f"账号 {username} 登录失败,跳过")
                    browser.close()
                    continue
                
                print("登录成功,进入我的立案...")
                page.get_by_text("我的立案").click()
                time.sleep(0.5)
                
                grand_total = 0
                for category in categories:
                    if category == '审判' and full_sync:
                        count = sync_category(page, category, full_sync=full_sync)
                        grand_total += count
                    else:
                        count = sync_category(page, category, full_sync=full_sync)
                        grand_total += count
                
                print(f"账号 {username} 同步完成: {grand_total} 条")
                
            except Exception as e:
                print("账号 %s 同步出错: %s" % (username, str(e)))
                import traceback
                traceback.print_exc()
            finally:
                browser.close()
        
        # 记录同步日志
        conn = pymysql.connect(**STATUS_DB_CONFIG)
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO sync_log (sync_time, total_cases, updated_cases) VALUES (NOW(), %s, %s)", (grand_total, 0))
            conn.commit()
        finally:
            conn.close()
        
        print("\n账号 %s 同步完成: 共 %d 条" % (username, grand_total))


# 初始化EasyOCR(只初始化一次)
_ocr_reader = None

def preprocess_for_ocr(image_path):
    # 图像预处理提高OCR精度
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 自适应阈值二值化
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    
    # 去噪
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
    
    # 保存预处理后的图像
    preprocessed_path = image_path.replace('.png', '_preprocessed.png')
    cv2.imwrite(preprocessed_path, denoised)
    
    return preprocessed_path

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        print("  初始化EasyOCR...")
        _ocr_reader = easyocr.Reader(['ch_sim', 'en'])
        print("  EasyOCR初始化完成")
    return _ocr_reader

def parse_preservation_from_ocr(texts):
    # 从OCR文本解析保全案件
    cases = []
    i = 0
    
    # 调试:打印前20条文本
    print("    OCR文本样本: %s" % str(texts[:20]))
    
    while i < len(texts):
        text = texts[i]
        
        # 查找状态
        status = None
        if '已撤销' in text:
            status = '已撤销'
        elif '待裁定' in text:
            status = '待裁定'
        elif '待提交' in text:
            status = '待提交'
        elif '已立案' in text:
            status = '已立案'
        elif '审核不通过' in text:
            status = '审核不通过'
        elif '待审核' in text:
            status = '待审核'
        
        if status:
            case = {'status': status}
            
            # 查找被申请人(下一条通常是"被申请人:",再下一条是名称)
            defendant = ''
            if i + 1 < len(texts) and '被申请人' in texts[i + 1]:
                # 被申请人在下下一条
                if i + 2 < len(texts):
                    defendant = texts[i + 2].strip()
                    i += 2
            elif i + 1 < len(texts):
                next_text = texts[i + 1]
                if len(next_text) > 1 and '保全' not in next_text and '编号' not in next_text and '法院' not in next_text:
                    defendant = next_text
                    i += 1
            
            # 如果defendant为空,尝试在整个文本列表中查找被申请人
            if not defendant:
                for j in range(len(texts)):
                    if '被申请人' in texts[j] and j + 1 < len(texts):
                        defendant = texts[j + 1].strip()
                        break
            
            case['defendant'] = defendant
            
            # 查找保全编号(在后续几行中找包含J/]或编号的)
            case_no = ''
            for j in range(i, min(i + 15, len(texts))):
                text = texts[j]
                # OCR可能把J识别成]
                if 'J' in text or ']' in text or '编号' in text:
                    # 匹配编号格式:J1C1120251115070 或 ]1C1120251115070(允许空格)
                    match = re.search(r'[\]J]\s*[A-Z0-9]{9,}', text)
                    if match:
                        case_no = match.group().replace(']', 'J').replace(' ', '')
                        break
            case['case_no'] = case_no
            
            # Debug: print case_no and title
            print("    DEBUG: case_no='%s', title='%s', defendant='%s'" % (case_no, case.get('title', ''), defendant))
            
            # 查找申请人(在后续文本中找银行名称)
            applicant = ''
            for j in range(i, min(i + 30, len(texts))):
                if '银行' in texts[j] or '支行' in texts[j]:
                    applicant = texts[j]
                    break
            case['applicant'] = applicant
            
            # 查找法院(在后续文本中)
            court = ''
            for j in range(i, min(i + 30, len(texts))):
                if '人民法院' in texts[j]:
                    court = texts[j]
                    break
            case['court'] = court
            
            # 查找日期(在后续文本中)
            apply_date = ''
            for j in range(i, min(i + 30, len(texts))):
                match = re.search(r'(\d{4}-\d{2}-\d{2})', texts[j])
                if match:
                    apply_date = match.group(1)
                    break
            case['apply_date'] = apply_date
            
            # 查找金额(在后续文本中)
            amount = ''
            for j in range(i, min(i + 30, len(texts))):
                match = re.search(r'(\d{4,})', texts[j])
                if match and len(match.group(1)) >= 4:
                    amount = match.group(1)
                    break
            case['amount'] = amount
            
            # 构建case_name:优先使用编号
            if case_no:
                case['title'] = case_no
            elif applicant and defendant:
                case['title'] = '%s诉%s财产保全' % (applicant[:20], defendant[:20])
            elif defendant:
                case['title'] = '%s财产保全' % defendant[:30]
            else:
                case['title'] = '未知保全案件'
            
            cases.append(case)
        
        i += 1
    
    return cases

if __name__ == '__main__':
    import sys
    full_sync = '--full' in sys.argv
    init_status_db()
    
    # 记录开始时间
    start_time = datetime.now()
    print("=" * 60)
    print("同步任务开始: %s" % start_time)
    print("模式: %s" % ('全量同步' if full_sync else '增量同步'))
    print("=" * 60)
    
    try:
        sync_filing_status(full_sync=full_sync)
    except Exception as e:
        print("同步过程出错: %s" % str(e))
        import traceback
        traceback.print_exc()
    
    # 记录结束时间
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print("=" * 60)
    print("同步任务结束: %s" % end_time)
    print("总耗时: %.1f分钟" % (duration / 60))
    print("=" * 60)
