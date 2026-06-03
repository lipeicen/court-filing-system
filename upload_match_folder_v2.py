"""
法院自动立案系统 - 文件夹名匹配上传
用子文件夹名称匹配页面上传口
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
    captcha_img.screenshot(path="captcha_match.png")
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open("captcha_match.png", 'rb') as f:
        return ocr.classification(f.read())


def auto_login(page):
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(2)
    page.get_by_text("律师用户").click()
    time.sleep(0.5)
    page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox").fill("13723715831")
    page.locator("input[type=\"password\"]").fill("HU1234pp")
    captcha = solve_captcha(page)
    if captcha:
        page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox").fill(captcha)
    time.sleep(0.5)
    page.get_by_text("登录", exact=True).click()
    page.wait_for_selector("text=在线立案", timeout=10000)
    print("登录成功!")


def create_and_fill(page):
    """创建保全申请并填写基本信息"""
    page.get_by_text("在线立案").click()
    time.sleep(2)
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    page1 = page1_info.value
    time.sleep(3)
    
    # 创建保全
    page1.get_by_role("radio", name="我已阅读网上保全须知").click()
    page1.get_by_role("button", name="创建保全申请").click()
    time.sleep(2)
    page1.get_by_placeholder("选择申请法院").click()
    page1.get_by_placeholder("选择申请法院").fill("广东")
    time.sleep(1)
    page1.get_by_text("广东省深圳市中级人民法院").click()
    page1.get_by_placeholder("请输入您要申请的保全金额").fill("20000")
    page1.get_by_role("radio", name="律师").click()
    page1.get_by_role("button", name="创建保全").click()
    time.sleep(3)
    
    # 申请人
    page1.get_by_text("添加").first.click()
    time.sleep(2)
    page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox").fill("李小二")
    page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox").fill("445202199403060317")
    page1.get_by_role("radio", name="男性").click()
    page1.locator("#addSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox").fill("13149930995")
    page1.locator("div").filter(has_text=re.compile(r"^经常居住地$")).get_by_role("textbox").fill("广东省深圳市南山区文德福花园3栋1102")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    # 被申请人
    page1.get_by_text("添加").nth(1).click()
    time.sleep(2)
    page1.locator("div").filter(has_text=re.compile(r"^姓名$")).get_by_role("textbox").fill("李小三")
    page1.locator("div").filter(has_text=re.compile(r"^证件号码$")).get_by_role("textbox").fill("445202199403060317")
    page1.get_by_role("radio", name="男性").click()
    page1.locator("#addBSQR div").filter(has_text=re.compile(r"^手机号码$")).get_by_role("textbox").fill("13631610603")
    page1.get_by_role("button", name="保存").click()
    time.sleep(2)
    
    # 财产
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
    
    # 担保
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
    
    # 进入材料上传页面
    page1.get_by_role("button", name="下一步").click()
    time.sleep(5)
    
    return page1


def get_folder_mapping(upload_dir):
    """获取文件夹到文件的映射"""
    mapping = {}
    for folder_name in os.listdir(upload_dir):
        folder_path = os.path.join(upload_dir, folder_name)
        if os.path.isdir(folder_path):
            files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
            mapping[folder_name] = {
                'path': folder_path,
                'files': files
            }
    return mapping


def upload_by_folder_name(page1, upload_dir):
    """
    用文件夹名称匹配页面上传口
    策略：
    1. 扫描本地文件夹
    2. 在页面上查找同名表头
    3. 找到对应的上传控件
    4. 上传文件夹内所有文件
    """
    print("\n" + "=" * 60)
    print("开始按文件夹名匹配上传")
    print("=" * 60)
    
    # 获取本地文件夹映射
    folder_mapping = get_folder_mapping(upload_dir)
    print(f"\n本地文件夹: {list(folder_mapping.keys())}")
    
    # 获取页面文本
    page_text = page1.evaluate("() => document.body.innerText")
    
    # 截图
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_match_before.png")
    
    # 遍历每个本地文件夹
    for folder_name, info in folder_mapping.items():
        print(f"\n{'='*50}")
        print(f"【{folder_name}】")
        print(f"{'='*50}")
        
        # 检查页面是否有这个表头
        if folder_name not in page_text:
            print(f"页面上未找到表头: {folder_name}")
            continue
        
        print(f"找到 {len(info['files'])} 个文件")
        
        # 找到该表头对应的上传区域
        # 方法：找到包含该名称的 upload-demo 或上传按钮
        try:
            # 查找包含该名称的元素
            header_els = page1.locator(f"text={folder_name}").all()
            print(f"页面上找到 {len(header_els)} 个'{folder_name}'元素")
            
            for file_name in info['files']:
                file_path = os.path.join(info['path'], file_name)
                print(f"\n  上传: {file_name}")
                
                uploaded = False
                
                # 策略1: 通过 [content] 属性找到上传区域
                try:
                    upload_demo = page1.locator(f"[content=\"{folder_name}\"]").first
                    if upload_demo.count() > 0 and upload_demo.is_visible():
                        print(f"    找到content属性匹配区域")
                        
                        # 查找区域内的input
                        inp = upload_demo.locator("input[type='file']").first
                        if inp.count() > 0:
                            inp.set_input_files(file_path)
                            print(f"    ✓ 上传成功")
                            uploaded = True
                            time.sleep(2)
                except Exception as e:
                    print(f"    策略1失败: {e}")
                
                # 策略2: 在表头元素附近查找上传按钮
                if not uploaded:
                    for hel in header_els:
                        try:
                            if not hel.is_visible():
                                continue
                            
                            # 获取元素位置
                            box = hel.bounding_box()
                            if not box:
                                continue
                            
                            print(f"    表头位置: ({box['x']:.0f}, {box['y']:.0f})")
                            
                            # 在下方查找上传按钮
                            # 使用JavaScript查找同一父容器内的上传按钮
                            parent_upload = hel.evaluate("""el => {
                                // 向上查找包含上传控件的父元素
                                let parent = el.parentElement;
                                while (parent) {
                                    if (parent.querySelector('input[type=\"file\"]')) {
                                        return true;
                                    }
                                    parent = parent.parentElement;
                                }
                                return false;
                            }""")
                            
                            if parent_upload:
                                # 找到父元素中的input
                                parent = hel.locator("xpath=ancestor::div[contains(@class, 'fd-upload-wrap') or contains(@class, 'fd-upload-center')]")
                                inp = parent.locator("input[type='file']").first
                                
                                if inp.count() > 0:
                                    inp.set_input_files(file_path)
                                    print(f"    ✓ 上传成功")
                                    uploaded = True
                                    time.sleep(2)
                                    break
                            
                        except Exception as e:
                            print(f"    策略2尝试失败: {e}")
                            continue
                
                # 策略3: 使用JavaScript直接操作DOM
                if not uploaded:
                    try:
                        print(f"    尝试JavaScript上传...")
                        result = page1.evaluate("""({folderName, filePath}) => {
                            // 找到所有upload-demo
                            const demos = document.querySelectorAll('.upload-demo, [class*="upload"]');
                            for (let demo of demos) {
                                // 检查是否包含目标名称
                                if (demo.textContent.includes(folderName) || demo.getAttribute('content') === folderName) {
                                    const input = demo.querySelector('input[type=\"file\"]');
                                    if (input) {
                                        // 创建DataTransfer对象模拟文件上传
                                        // 注意：由于安全限制，JS无法直接设置文件路径
                                        // 返回input信息供Playwright处理
                                        return {
                                            found: true,
                                            hasInput: true,
                                            inputIndex: Array.from(document.querySelectorAll('input[type=\"file\"]')).indexOf(input)
                                        };
                                    }
                                }
                            }
                            return { found: false };
                        }""", {"folderName": folder_name, "filePath": file_path})
                        
                        print(f"    JS结果: {result}")
                        
                        if result.get('found') and result.get('hasInput') and result.get('inputIndex') >= 0:
                            # 使用Playwright找到对应的input
                            all_inputs = page1.locator("input[type='file']").all()
                            if result['inputIndex'] < len(all_inputs):
                                all_inputs[result['inputIndex']].set_input_files(file_path)
                                print(f"    ✓ JS辅助上传成功")
                                uploaded = True
                                time.sleep(2)
                    except Exception as e:
                        print(f"    策略3失败: {e}")
                
                if not uploaded:
                    print(f"    ✗ 所有策略都失败")
                    
        except Exception as e:
            print(f"  处理出错: {e}")
    
    # 截图查看结果
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_match_after.png")
    print("\n" + "=" * 60)
    print("上传完成")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("法院自动立案 - 文件夹名匹配上传")
    print("=" * 60)
    
    upload_dir = r"C:\\court-auto-filing\\uploads\\保全2026001"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            auto_login(page)
            page1 = create_and_fill(page)
            upload_by_folder_name(page1, upload_dir)
            
            print("\n保持浏览器打开60秒...")
            time.sleep(60)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(30)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
