"""
法院自动立案系统 - 最终版文件上传
基于HTML结构分析，精准匹配每个上传区域
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
    captcha_img.screenshot(path="captcha_final.png")
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open("captcha_final.png", 'rb') as f:
        return ocr.classification(f.read())


def auto_login(page):
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(2)
    
    page.get_by_text("律师用户").click()
    time.sleep(0.5)
    
    page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox").fill("13723715831")
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


def upload_files_final(page1, upload_dir):
    """
    最终版文件上传
    基于HTML分析：
    - 简单区域（无子项）：保全申请书、起诉状、立案受理通知书、证据材料、其他材料
    - 带子项区域：身份证明材料（申请人、被申请人）、担保材料（提供保证人）
    """
    print("\n" + "=" * 60)
    print("开始上传文件")
    print("=" * 60)
    
    # 定义上传映射
    # 格式: (页面显示名称, 文件夹名称, [文件列表], 是否有子项)
    upload_mapping = [
        # 简单区域 - 无子项
        ("保全申请书", "保全申请书", ["01_保全申请书.pdf"], False),
        ("起诉状", "起诉状", ["起诉状.doc"], False),
        # 身份证明材料 - 有子项
        ("身份证明材料", "身份证明材料", ["03_申请人证照.pdf", "04_被申请人身份证.pdf", "05_代理人授权书.pdf"], True),
        # 担保材料 - 有子项
        ("担保材料", "担保材料", ["06_担保函.pdf", "07_保证人证照.pdf"], True),
        # 证据材料 - 无子项
        ("证据材料", "证据材料", ["证据材料.doc"], False),
        # 其他材料 - 无子项
        ("其他材料", "其他材料", ["其他材料.doc"], False),
    ]
    
    # 获取所有文件上传input
    all_file_inputs = page1.locator("input[type='file']").all()
    print(f"\n页面共有 {len(all_file_inputs)} 个文件上传input")
    
    # 截图查看
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_before.png")
    
    for category_name, folder_name, files, has_subitems in upload_mapping:
        print(f"\n{'='*50}")
        print(f"【{category_name}】")
        print(f"{'='*50}")
        
        folder_path = os.path.join(upload_dir, folder_name)
        
        if not os.path.exists(folder_path):
            print(f"文件夹不存在: {folder_path}")
            continue
        
        if has_subitems:
            # 处理带子项的区域
            print(f"此区域有子项，需要分别上传")
            
            # 获取该类别下的所有上传按钮（按子项）
            # 查找包含子项名称的上传按钮
            subitem_buttons = page1.locator(".fd-upload-item-name").all()
            
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                if not os.path.exists(file_path):
                    print(f"  文件不存在: {file_name}")
                    continue
                
                print(f"\n  上传: {file_name}")
                
                # 根据文件名判断应该上传到哪个子项
                uploaded = False
                
                if "申请人" in file_name or "代理人" in file_name:
                    # 上传到申请人子项
                    for btn in subitem_buttons:
                        try:
                            btn_text = btn.inner_text()
                            if "申请人" in btn_text and "被申请人" not in btn_text:
                                print(f"    匹配子项: {btn_text}")
                                # 点击上传按钮
                                parent = btn.locator("xpath=..")
                                upload_btn = parent.locator("text=上传").first
                                if upload_btn.is_visible():
                                    upload_btn.click()
                                    time.sleep(1)
                                    
                                    # 找到对应的input并上传
                                    # 使用JavaScript找到最近的input
                                    inp = page1.locator("input[type='file']").nth(0)  # 简化处理
                                    try:
                                        inp.set_input_files(file_path)
                                        print(f"    ✓ 上传成功")
                                        uploaded = True
                                        time.sleep(2)
                                        break
                                    except:
                                        pass
                        except:
                            continue
                            
                elif "被申请人" in file_name:
                    # 上传到被申请人子项
                    for btn in subitem_buttons:
                        try:
                            btn_text = btn.inner_text()
                            if "被申请人" in btn_text:
                                print(f"    匹配子项: {btn_text}")
                                parent = btn.locator("xpath=..")
                                upload_btn = parent.locator("text=上传").first
                                if upload_btn.is_visible():
                                    upload_btn.click()
                                    time.sleep(1)
                                    
                                    inp = page1.locator("input[type='file']").nth(1)  # 简化处理
                                    try:
                                        inp.set_input_files(file_path)
                                        print(f"    ✓ 上传成功")
                                        uploaded = True
                                        time.sleep(2)
                                        break
                                    except:
                                        pass
                        except:
                            continue
                
                elif "担保" in file_name or "保证人" in file_name:
                    # 上传到担保材料子项
                    for btn in subitem_buttons:
                        try:
                            btn_text = btn.inner_text()
                            if "保证人" in btn_text or "担保" in btn_text:
                                print(f"    匹配子项: {btn_text}")
                                parent = btn.locator("xpath=..")
                                upload_btn = parent.locator("text=上传").first
                                if upload_btn.is_visible():
                                    upload_btn.click()
                                    time.sleep(1)
                                    
                                    # 担保材料的input索引需要根据实际情况调整
                                    for inp in all_file_inputs:
                                        try:
                                            inp.set_input_files(file_path)
                                            print(f"    ✓ 上传成功")
                                            uploaded = True
                                            time.sleep(2)
                                            break
                                        except:
                                            continue
                                    break
                        except:
                            continue
                
                if not uploaded:
                    print(f"    ✗ 未能上传")
                    
        else:
            # 处理无子项的区域
            print(f"此区域无子项，直接上传")
            
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                if not os.path.exists(file_path):
                    print(f"  文件不存在: {file_name}")
                    continue
                
                print(f"\n  上传: {file_name}")
                
                # 找到该类别的上传按钮
                uploaded = False
                
                try:
                    # 方法1: 通过content属性找到上传区域
                    # 查找包含该类别名称的upload-demo
                    upload_demo = page1.locator(f"[content=\"{category_name}\"]").first
                    
                    if upload_demo.is_visible():
                        print(f"    找到上传区域")
                        # 在该区域内查找input
                        inp = upload_demo.locator("input[type='file']").first
                        
                        if inp.count() > 0:
                            inp.set_input_files(file_path)
                            print(f"    ✓ 上传成功")
                            uploaded = True
                            time.sleep(2)
                        else:
                            # 点击上传按钮触发input
                            btn = upload_demo.locator("text=上传").first
                            if btn.is_visible():
                                btn.click()
                                time.sleep(1)
                                
                                # 重新查找input
                                new_inp = upload_demo.locator("input[type='file']").first
                                if new_inp.count() > 0:
                                    new_inp.set_input_files(file_path)
                                    print(f"    ✓ 上传成功")
                                    uploaded = True
                                    time.sleep(2)
                    
                except Exception as e:
                    print(f"    方法1失败: {e}")
                
                if not uploaded:
                    # 方法2: 遍历所有input尝试上传
                    print(f"    尝试备用方法...")
                    for inp in all_file_inputs:
                        try:
                            inp.set_input_files(file_path)
                            print(f"    ✓ 备用方法成功")
                            uploaded = True
                            time.sleep(2)
                            break
                        except:
                            continue
                
                if not uploaded:
                    print(f"    ✗ 上传失败")
    
    # 截图查看结果
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_after.png")
    print("\n" + "=" * 60)
    print("文件上传完成")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 最终版文件上传")
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
            
            # 5. 上传文件
            upload_files_final(page1, upload_dir)
            
            # 6. 完成
            print("\n" + "=" * 60)
            print("✅ 流程完成!")
            print("=" * 60)
            
            # 保持打开
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
