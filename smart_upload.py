"""
法院自动立案系统 - 改进版文件上传
根据页面表头精准匹配上传
"""

from playwright.sync_api import sync_playwright
import time
import re
import os


def solve_captcha(page):
    import ddddocr
    captcha_img = page.locator("uni-image img")
    if captcha_img.count() == 0:
        return None
    captcha_img.screenshot(path="captcha_upload.png")
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open("captcha_upload.png", 'rb') as f:
        return ocr.classification(f.read())


def auto_login(page):
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(2)
    
    page.get_by_text("律师用户").click()
    time.sleep(0.5)
    
    phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
    phone_input.click()
    phone_input.fill("13723715831")
    time.sleep(0.5)
    
    page.locator("input[type=\"password\"]").fill("HU1234pp")
    time.sleep(0.5)
    
    captcha = solve_captcha(page)
    if captcha:
        print(f"验证码: {captcha}")
        page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox").fill(captcha)
    time.sleep(0.5)
    
    page.get_by_text("登录", exact=True).click()
    
    try:
        page.wait_for_selector("text=在线立案", timeout=10000)
        print("登录成功!")
        return True
    except:
        print("登录失败")
        return False


def create_preservation(page):
    print("\n" + "=" * 50)
    print("创建保全申请")
    print("=" * 50)
    
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    
    page1 = page1_info.value
    print(f"新窗口: {page1.url}")
    time.sleep(3)
    
    page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    time.sleep(0.5)
    
    page1.get_by_role("button", name="创建保全申请").click()
    time.sleep(2)
    
    page1.get_by_placeholder("选择申请法院").click()
    page1.get_by_placeholder("选择申请法院").fill("广东")
    time.sleep(1)
    page1.get_by_text("广东省深圳市中级人民法院").click()
    time.sleep(0.5)
    
    page1.get_by_placeholder("请输入您要申请的保全金额").fill("20000")
    time.sleep(0.5)
    
    page1.get_by_role("radio", name="律师").click()
    time.sleep(0.5)
    
    page1.get_by_role("button", name="创建保全").click()
    time.sleep(3)
    
    print("保全申请创建成功!")
    return page1


def fill_basic_info(page1):
    """填写基本信息"""
    
    # 添加申请人
    print("\n添加申请人...")
    page1.get_by_text("添加").first.click()
    time.sleep(2)
    page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox").fill("李小二")
    page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox").fill("445202199403060317")
    page1.get_by_role("radio", name="男性").click()
    page1.locator("#addSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox").fill("13149930995")
    page1.locator("div").filter(has_text=re.compile(r"^经常居住地$")).get_by_role("textbox").fill("广东省深圳市南山区文德福花园3栋1102")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    # 添加被申请人
    print("添加被申请人...")
    page1.get_by_text("添加").nth(1).click()
    time.sleep(2)
    page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox").fill("李小三")
    page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox").fill("445202199403060317")
    page1.get_by_role("radio", name="男性").click()
    page1.locator("#addBSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox").fill("13631610603")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    # 添加财产线索
    print("添加财产线索...")
    page1.locator("span").filter(has_text=re.compile(r"^添加$")).click()
    time.sleep(2)
    page1.get_by_placeholder("请选择财产类型").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="存款").click()
    page1.get_by_placeholder("请选择财产所有人").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="李小三").click()
    page1.locator("div").filter(has_text=re.compile(r"^开户行所在地")).get_by_role("textbox").click()
    time.sleep(1)
    page1.get_by_text("广东", exact=True).click()
    page1.locator("div").filter(has_text=re.compile(r"^开户银行名称$")).get_by_role("textbox").fill("中国银行")
    page1.locator("div").filter(has_text=re.compile(r"^开户账号$")).get_by_role("textbox").fill("4325362362364342")
    page1.locator("div").filter(has_text=re.compile(r"^数额$")).get_by_role("textbox").fill("200000")
    page1.get_by_placeholder("请选择单位").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="人民币").click()
    page1.locator("form div").filter(has_text="财产价值￥ 元").get_by_role("textbox").fill("200000")
    page1.get_by_role("button", name="保存", exact=True).click()
    time.sleep(2)
    
    # 添加担保信息
    print("添加担保信息...")
    page1.get_by_role("button", name="下一步").click()
    time.sleep(2)
    page1.locator("span").filter(has_text="添加").locator("i").click()
    time.sleep(2)
    page1.get_by_placeholder("请选择").click()
    time.sleep(1)
    page1.locator("li").filter(has_text="提供保证人").click()
    page1.get_by_placeholder("请输入担保人").fill("李小四")
    page1.get_by_placeholder("请输入担保名称").fill("现金")
    page1.locator("#addDBXX div").filter(has_text="担保价值 元").get_by_role("textbox").fill("200000")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    print("基本信息填写完成!")


def smart_upload_files(page1, upload_dir):
    """
    智能上传文件
    策略：
    1. 找到每个材料类别的"上传"按钮
    2. 点击按钮触发文件选择
    3. 使用 set_input_files 上传文件
    """
    print("\n" + "=" * 60)
    print("开始智能上传文件")
    print("=" * 60)
    
    # 材料类别到文件夹的映射
    categories = [
        ("保全申请书", "保全申请书"),
        ("起诉状", "起诉状"),
        ("身份证明材料", "身份证明材料"),
        ("证据材料", "证据材料"),
        ("担保材料", "担保材料"),
        ("其他材料", "其他材料")
    ]
    
    # 截图
    time.sleep(3)
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_page_v2.png")
    
    # 获取页面HTML分析结构
    html = page1.content()
    with open(r"C:\\court-auto-filing\\upload_page.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print("页面HTML已保存")
    
    # 遍历每个类别
    for header_text, folder_name in categories:
        print(f"\n【{header_text}】")
        
        # 检查文件夹
        folder_path = os.path.join(upload_dir, folder_name)
        if not os.path.exists(folder_path):
            print(f"  文件夹不存在")
            continue
        
        files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
        if not files:
            print(f"  文件夹为空")
            continue
        
        print(f"  找到 {len(files)} 个文件")
        
        # 查找该类别的上传按钮
        # 策略：找到包含表头文字的元素，然后在同层级或子层级找"上传"按钮
        try:
            # 方法1：直接查找包含表头和"上传"的父元素
            # 使用 xpath 查找包含特定文本的元素
            header_elements = page1.locator(f"text={header_text}").all()
            print(f"  找到 {len(header_elements)} 个表头元素")
            
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                print(f"\n  准备上传: {file_name}")
                
                uploaded = False
                
                # 尝试为每个文件找到对应的上传按钮
                for hel in header_elements:
                    try:
                        if not hel.is_visible():
                            continue
                        
                        # 获取元素的边界框
                        box = hel.bounding_box()
                        if not box:
                            continue
                        
                        print(f"    表头位置: x={box['x']}, y={box['y']}")
                        
                        # 在表头下方区域查找"上传"按钮
                        # 通常上传按钮在表头右侧或下方
                        upload_btn = page1.locator("text=上传").filter(
                            lambda btn: btn.bounding_box() and 
                            btn.bounding_box()['y'] >= box['y'] - 50 and 
                            btn.bounding_box()['y'] <= box['y'] + 200
                        ).first
                        
                        if upload_btn.is_visible():
                            print(f"    点击上传按钮...")
                            upload_btn.click()
                            time.sleep(1)
                            
                            # 查找当前可见的文件input
                            all_inputs = page1.locator("input[type='file']").all()
                            for inp in all_inputs:
                                try:
                                    if inp.is_visible() or inp.is_enabled():
                                        inp.set_input_files(file_path)
                                        print(f"    成功!")
                                        uploaded = True
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if uploaded:
                                break
                        
                    except Exception as e:
                        print(f"    尝试失败: {e}")
                        continue
                
                if not uploaded:
                    print(f"    未能自动上传，尝试备用方法...")
                    # 备用：直接查找所有input并尝试上传
                    all_inputs = page1.locator("input[type='file']").all()
                    for inp in all_inputs:
                        try:
                            inp.set_input_files(file_path)
                            print(f"    备用方法成功!")
                            uploaded = True
                            time.sleep(2)
                            break
                        except:
                            continue
                
                if not uploaded:
                    print(f"    上传失败")
                    
        except Exception as e:
            print(f"  处理出错: {e}")
    
    print("\n文件上传完成")


def main():
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 改进版文件上传")
    print("=" * 60)
    
    upload_dir = r"C:\\court-auto-filing\\uploads\\保全2026001"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录
            if not auto_login(page):
                return
            
            # 2. 创建保全申请
            page1 = create_preservation(page)
            
            # 3. 填写基本信息
            fill_basic_info(page1)
            
            # 4. 点击下一步进入材料上传页面
            print("\n点击下一步进入材料上传页面...")
            page1.get_by_role("button", name="下一步").click()
            time.sleep(5)
            
            # 5. 智能上传文件
            smart_upload_files(page1, upload_dir)
            
            # 6. 完成
            print("\n" + "=" * 60)
            print("流程完成!")
            print("=" * 60)
            
            # 保持打开
            print("\n保持浏览器打开60秒...")
            time.sleep(60)
            
        except Exception as e:
            print(f"\n发生错误: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)
            
        finally:
            print("\n关闭浏览器...")
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
