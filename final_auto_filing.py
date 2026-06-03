"""
法院自动立案系统 - 最终版本
基于 Playwright Codegen 录制结果优化
"""

from playwright.sync_api import sync_playwright, expect
import time
import re


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
    """创建保全申请"""
    print("\n" + "=" * 50)
    print("开始创建保全申请")
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
    amount_input.fill("20000")
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
    name_input.fill("李小二")
    time.sleep(0.5)
    
    # 输入身份证号
    print("输入身份证号...")
    id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
    id_input.click()
    id_input.fill("445202199403060317")
    time.sleep(0.5)
    
    # 选择性别
    print("选择性别...")
    page1.get_by_role("radio", name="男性").click()
    time.sleep(0.5)
    
    # 输入手机号
    print("输入手机号...")
    phone_input = page1.locator("#addSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
    phone_input.click()
    phone_input.fill("13149930995")
    time.sleep(0.5)
    
    # 输入地址
    print("输入地址...")
    addr_input = page1.locator("div").filter(has_text=re.compile(r"^经常居住地$")).get_by_role("textbox")
    addr_input.click()
    addr_input.fill("广东省深圳市南山区文德福花园3栋1102")
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
    page1.get_by_text("添加").nth(1).click()
    time.sleep(2)
    
    # 输入姓名
    print("输入姓名...")
    name_input = page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox")
    name_input.click()
    name_input.fill("李小三")
    time.sleep(0.5)
    
    # 输入身份证号
    print("输入身份证号...")
    id_input = page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox")
    id_input.click()
    id_input.fill("445202199403060317")
    time.sleep(0.5)
    
    # 选择性别
    print("选择性别...")
    page1.get_by_role("radio", name="男性").click()
    time.sleep(0.5)
    
    # 输入手机号
    print("输入手机号...")
    phone_input = page1.locator("#addBSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox")
    phone_input.click()
    phone_input.fill("13631610603")
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
    page1.locator("li").filter(has_text="李小三").click()
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
    bank_input.fill("中国银行")
    time.sleep(0.5)
    
    # 输入开户账号
    print("输入开户账号...")
    account_input = page1.locator("div").filter(has_text=re.compile(r"^开户账号$")).get_by_role("textbox")
    account_input.click()
    account_input.fill("4325362362364342")
    time.sleep(0.5)
    
    # 输入数额
    print("输入数额...")
    amount_input = page1.locator("div").filter(has_text=re.compile(r"^数额$")).get_by_role("textbox")
    amount_input.click()
    amount_input.fill("200000")
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
    value_input.fill("200000")
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
    guarantor_input.fill("李小四")
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
    value_input.fill("200000")
    time.sleep(0.5)
    
    # 保存
    print("保存担保信息...")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("担保信息添加成功!")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 最终版本")
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
            
            # 7. 完成
            print("\n" + "=" * 60)
            print("保全申请流程完成!")
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
