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


def analyze_upload_page(page1):
    """详细分析上传页面结构"""
    print("\n" + "=" * 60)
    print("分析材料上传页面结构")
    print("=" * 60)
    
    # 1. 截图
    page1.screenshot(path=r"C:\\court-auto-filing\\upload_analysis.png", full_page=True)
    print("全页面截图已保存: upload_analysis.png")
    
    # 2. 获取所有文本
    text = page1.evaluate("() => document.body.innerText")
    print("\n页面文本:")
    print(text)
    
    # 3. 获取HTML
    html = page1.content()
    with open(r"C:\\court-auto-filing\\upload_analysis.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nHTML已保存: upload_analysis.html")
    
    # 4. 查找所有上传按钮
    print("\n" + "-" * 40)
    print("查找所有'上传'按钮:")
    print("-" * 40)
    
    upload_btns = page1.locator("text=上传").all()
    for i, btn in enumerate(upload_btns):
        try:
            box = btn.bounding_box()
            parent = btn.locator("xpath=..")
            parent_text = parent.inner_text()[:100]
            print(f"\n  按钮 {i+1}:")
            print(f"    位置: x={box['x']:.0f}, y={box['y']:.0f}")
            print(f"    父元素文本: {parent_text}")
        except Exception as e:
            print(f"  按钮 {i+1}: 无法获取信息 - {e}")
    
    # 5. 查找所有文件input
    print("\n" + "-" * 40)
    print("查找所有文件上传input:")
    print("-" * 40)
    
    file_inputs = page1.locator("input[type='file']").all()
    for i, inp in enumerate(file_inputs):
        try:
            box = inp.bounding_box()
            visible = inp.is_visible()
            enabled = inp.is_enabled()
            
            # 获取父元素信息
            parent_html = inp.evaluate("el => el.parentElement.outerHTML[:200]")
            
            print(f"\n  Input {i+1}:")
            print(f"    位置: x={box['x']:.0f}, y={box['y']:.0f}")
            print(f"    可见: {visible}, 启用: {enabled}")
            print(f"    父元素: {parent_html}")
        except Exception as e:
            print(f"  Input {i+1}: 无法获取信息 - {e}")
    
    # 6. 查找材料类别区域
    print("\n" + "-" * 40)
    print("查找材料类别区域:")
    print("-" * 40)
    
    categories = ["保全申请书", "起诉状", "立案受理通知书", "身份证明材料", "担保材料", "证据材料", "其他材料"]
    for cat in categories:
        try:
            els = page1.locator(f"text={cat}").all()
            for el in els:
                if el.is_visible():
                    box = el.bounding_box()
                    print(f"\n  {cat}:")
                    print(f"    位置: x={box['x']:.0f}, y={box['y']:.0f}")
                    
                    # 查找附近的"上传"按钮
                    nearby_upload = page1.locator("text=上传").filter(
                        lambda btn: btn.bounding_box() and 
                        abs(btn.bounding_box()['y'] - box['y']) < 150
                    ).first
                    
                    if nearby_upload.is_visible():
                        ubox = nearby_upload.bounding_box()
                        print(f"    上传按钮位置: x={ubox['x']:.0f}, y={ubox['y']:.0f}")
                    break
        except Exception as e:
            print(f"  {cat}: 出错 - {e}")
    
    # 7. 使用JavaScript获取更详细的信息
    print("\n" + "-" * 40)
    print("JavaScript分析:")
    print("-" * 40)
    
    js_result = page1.evaluate("""() => {
        const result = {
            uploadButtons: [],
            fileInputs: [],
            sections: []
        };
        
        // 查找所有上传按钮
        document.querySelectorAll('button, .el-button, [class*="upload"]').forEach((btn, i) => {
            if (btn.innerText.includes('上传') || btn.className.includes('upload')) {
                const rect = btn.getBoundingClientRect();
                result.uploadButtons.push({
                    index: i,
                    text: btn.innerText.trim(),
                    x: rect.x,
                    y: rect.y,
                    className: btn.className
                });
            }
        });
        
        // 查找所有文件input
        document.querySelectorAll('input[type="file"]').forEach((inp, i) => {
            const rect = inp.getBoundingClientRect();
            result.fileInputs.push({
                index: i,
                x: rect.x,
                y: rect.y,
                parentTag: inp.parentElement?.tagName,
                parentClass: inp.parentElement?.className
            });
        });
        
        // 查找材料区域
        const sections = ['保全申请书', '起诉状', '立案受理通知书', '身份证明材料', '担保材料', '证据材料', '其他材料'];
        sections.forEach(name => {
            const els = document.querySelectorAll('*');
            for (let el of els) {
                if (el.innerText === name || el.innerText.includes(name + '\\n')) {
                    const rect = el.getBoundingClientRect();
                    result.sections.push({
                        name: name,
                        x: rect.x,
                        y: rect.y,
                        tagName: el.tagName,
                        className: el.className
                    });
                    break;
                }
            }
        });
        
        return result;
    }""")
    
    print("\n上传按钮:")
    for btn in js_result['uploadButtons']:
        print(f"  {btn['index']}: '{btn['text']}' at ({btn['x']:.0f}, {btn['y']:.0f})")
    
    print("\n文件Inputs:")
    for inp in js_result['fileInputs']:
        print(f"  {inp['index']}: at ({inp['x']:.0f}, {inp['y']:.0f}), parent: {inp['parentTag']}")
    
    print("\n材料区域:")
    for sec in js_result['sections']:
        print(f"  {sec['name']}: at ({sec['x']:.0f}, {sec['y']:.0f})")


def main():
    print("=" * 60)
    print("分析材料上传页面")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            auto_login(page)
            page1 = create_and_fill(page)
            analyze_upload_page(page1)
            
            print("\n" + "=" * 60)
            print("分析完成，保持浏览器打开供检查")
            print("=" * 60)
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
