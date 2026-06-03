"""
法院自动立案系统 - 精准匹配上传
根据页面表头文字，上传对应文件夹中的文件
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
    """填写基本信息（申请人、被申请人、财产、担保）"""
    
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


def upload_files_by_header(page1, upload_dir):
    """
    根据页面表头匹配上传文件
    表头如：保全申请书 -> 上传 uploads/保全2026001/保全申请书/ 下的文件
    """
    print("\n" + "=" * 60)
    print("开始根据表头匹配上传文件")
    print("=" * 60)
    
    # 定义表头到文件夹的映射
    header_to_folder = {
        "保全申请书": "保全申请书",
        "起诉状": "起诉状", 
        "身份证明材料": "身份证明材料",
        "证据材料": "证据材料",
        "担保材料": "担保材料",
        "其他材料": "其他材料"
    }
    
    # 截图查看材料页面
    time.sleep(3)
    page1.screenshot(path=r"C:\court-auto-filing\materials_upload_page.png")
    print("材料上传页面截图已保存")
    
    # 获取页面所有文本
    page_text = page1.evaluate("() => document.body.innerText")
    
    # 查找所有文件上传input
    file_inputs = page1.locator("input[type='file']").all()
    print(f"\n找到 {len(file_inputs)} 个文件上传input")
    
    # 遍历每个表头，查找对应的上传区域
    for header_text, folder_name in header_to_folder.items():
        print(f"\n【{header_text}】")
        
        # 检查页面上是否有这个表头
        if header_text not in page_text:
            print(f"  页面上未找到表头: {header_text}")
            continue
        
        # 查找该表头对应的文件夹
        folder_path = os.path.join(upload_dir, folder_name)
        if not os.path.exists(folder_path):
            print(f"  文件夹不存在: {folder_path}")
            continue
        
        # 获取文件夹中的所有文件
        files = os.listdir(folder_path)
        files = [f for f in files if not f.startswith('.')]
        
        if not files:
            print(f"  文件夹为空: {folder_path}")
            continue
        
        print(f"  找到 {len(files)} 个文件: {files}")
        
        # 查找表头元素
        try:
            header_elements = page1.locator(f"text={header_text}").all()
            print(f"  页面上找到 {len(header_elements)} 个'{header_text}'元素")
            
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                print(f"\n  准备上传: {file_name}")
                
                # 策略：找到表头元素，然后在其父元素或兄弟元素中查找上传控件
                uploaded = False
                
                for header_el in header_elements:
                    try:
                        if not header_el.is_visible():
                            continue
                        
                        # 获取表头元素的父元素
                        parent = header_el.locator("xpath=..")
                        grandparent = parent.locator("xpath=..")
                        
                        # 在父元素中查找上传按钮或input
                        upload_btn = parent.locator("button, [class*='upload'], text=/上传|添加/i").first
                        
                        if upload_btn.is_visible():
                            print(f"    点击上传按钮...")
                            upload_btn.click()
                            time.sleep(1)
                            
                            # 点击后查找新出现的文件input
                            new_inputs = page1.locator("input[type='file']").all()
                            for inp in new_inputs:
                                try:
                                    inp.set_input_files(file_path)
                                    print(f"    ✓ 上传成功")
                                    uploaded = True
                                    time.sleep(2)
                                    break
                                except:
                                    continue
                            
                            if uploaded:
                                break
                        
                        # 尝试在祖父元素中查找
                        file_input = grandparent.locator("input[type='file']").first
                        if file_input.count() > 0:
                            print(f"    找到文件input，直接上传...")
                            file_input.set_input_files(file_path)
                            print(f"    ✓ 上传成功")
                            uploaded = True
                            time.sleep(2)
                            break
                            
                    except Exception as e:
                        print(f"    尝试失败: {e}")
                        continue
                
                if not uploaded:
                    print(f"    ✗ 未能上传: {file_name}")
                    
        except Exception as e:
            print(f"  处理表头时出错: {e}")
    
    print("\n文件上传流程完成")


def main():
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 精准匹配上传")
    print("=" * 60)
    
    upload_dir = r"C:\court-auto-filing\uploads\保全2026001"
    
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
            
            # 5. 根据表头上传文件
            upload_files_by_header(page1, upload_dir)
            
            # 6. 完成
            print("\n" + "=" * 60)
            print("✅ 流程完成!")
            print("=" * 60)
            
            # 保持打开供检查
            print("\n保持浏览器打开60秒...")
            time.sleep(60)
            
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(60)
            
        finally:
            print("\n关闭浏览器...")
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
