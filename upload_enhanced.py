"""
法院自动立案系统 - 文件上传（增强版）
"""

from playwright.sync_api import sync_playwright
import time
import re
import os


def solve_captcha(page, max_retries=3):
    """解决验证码，带重试"""
    import ddddocr
    
    for attempt in range(max_retries):
        try:
            # 等待验证码图片加载
            page.wait_for_selector("uni-image img", timeout=5000)
            captcha_img = page.locator("uni-image img")
            
            if captcha_img.count() == 0:
                print(f"  尝试 {attempt+1}: 未找到验证码图片")
                time.sleep(1)
                continue
            
            # 截图并识别
            captcha_img.screenshot(path=f"captcha_retry_{attempt}.png")
            ocr = ddddocr.DdddOcr(show_ad=False)
            with open(f"captcha_retry_{attempt}.png", 'rb') as f:
                result = ocr.classification(f.read())
            
            print(f"  验证码识别结果: {result}")
            return result
            
        except Exception as e:
            print(f"  尝试 {attempt+1} 失败: {e}")
            time.sleep(1)
    
    return None


def auto_login(page):
    """自动登录"""
    print("=" * 50)
    print("开始登录")
    print("=" * 50)
    
    page.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
    time.sleep(3)
    
    # 选择律师用户
    print("选择律师用户...")
    try:
        page.get_by_text("律师用户").click()
        time.sleep(0.5)
    except:
        print("  可能已经是律师用户选项")
    
    # 填写手机号
    print("填写手机号...")
    phone_input = page.locator("uni-input").filter(has_text="请输入手机号/居民身份证号").get_by_role("textbox")
    phone_input.click()
    phone_input.fill("13723715831")
    time.sleep(0.5)
    
    # 填写密码
    print("填写密码...")
    page.locator("input[type=\"password\"]").fill("HU1234pp")
    time.sleep(0.5)
    
    # 识别验证码
    print("识别验证码...")
    captcha = solve_captcha(page)
    
    if captcha:
        captcha_input = page.locator("uni-input").filter(has_text="请输入验证码").get_by_role("textbox")
        captcha_input.click()
        captcha_input.fill(captcha)
        time.sleep(0.5)
    
    # 点击登录
    print("点击登录...")
    page.get_by_text("登录", exact=True).click()
    
    # 等待结果
    print("等待登录结果...")
    time.sleep(5)
    
    # 检查是否登录成功
    url = page.url
    print(f"当前URL: {url}")
    
    if "login" not in url:
        print("登录成功!")
        return True
    
    # 检查错误信息
    error_text = page.locator("text=/错误|失败|验证码|密码/i").first
    if error_text.is_visible():
        print(f"登录错误: {error_text.inner_text()}")
    
    print("登录失败")
    return False


def analyze_page(page1):
    """分析页面结构，查找上传控件"""
    print("\n" + "=" * 60)
    print("分析页面结构")
    print("=" * 60)
    
    # 截图
    page1.screenshot(path=r"C:\court-auto-filing\analyze_page.png")
    print("页面截图已保存")
    
    # 获取所有文本
    all_text = page1.evaluate("() => document.body.innerText")
    print(f"\n页面文本长度: {len(all_text)}")
    print("文本预览:")
    print(all_text[:500])
    
    # 查找所有按钮
    buttons = page1.locator("button, .el-button, [role='button']").all()
    print(f"\n找到 {len(buttons)} 个按钮")
    for i, btn in enumerate(buttons[:15]):
        try:
            text = btn.inner_text()
            if text.strip():
                print(f"  {i+1}. '{text[:40]}'")
        except:
            pass
    
    # 查找文件上传input
    file_inputs = page1.locator("input[type='file']").all()
    print(f"\n找到 {len(file_inputs)} 个文件上传input")
    
    # 查找包含"上传"的元素
    upload_elements = page1.locator("text=/上传|附件|材料/i").all()
    print(f"找到 {len(upload_elements)} 个上传相关元素")
    for el in upload_elements[:10]:
        try:
            text = el.inner_text()
            if text.strip():
                print(f"  - {text[:50]}")
        except:
            pass
    
    return file_inputs


def upload_file_direct(page1, file_path, file_inputs):
    """直接上传文件到input元素"""
    try:
        # 查找可见的文件input
        visible_inputs = [inp for inp in file_inputs if inp.is_visible()]
        
        if visible_inputs:
            print(f"  使用可见input上传: {os.path.basename(file_path)}")
            visible_inputs[0].set_input_files(file_path)
            return True
        elif file_inputs:
            print(f"  使用第一个input上传: {os.path.basename(file_path)}")
            file_inputs[0].set_input_files(file_path)
            return True
        else:
            print("  没有找到文件上传input")
            return False
            
    except Exception as e:
        print(f"  上传失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 文件上传（增强版）")
    print("=" * 60)
    
    # 配置
    upload_dir = r"C:\court-auto-filing\uploads\保全2026001"
    
    # 文件列表
    files_to_upload = [
        ("保全申请书", "保全申请书\\01_保全申请书.pdf"),
        ("起诉状", "起诉状\\起诉状.doc"),
        ("申请人证照", "身份证明材料\\03_申请人证照.pdf"),
        ("被申请人身份证", "身份证明材料\\04_被申请人身份证.pdf"),
        ("代理人授权书", "身份证明材料\\05_代理人授权书.pdf"),
        ("证据材料", "证据材料\\证据材料.doc"),
        ("担保函", "担保材料\\06_担保函.pdf"),
        ("保证人证照", "担保材料\\07_保证人证照.pdf"),
        ("其他材料", "其他材料\\其他材料.doc"),
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录
            if not auto_login(page):
                print("登录失败，退出")
                return
            
            # 2. 进入在线立案
            print("\n进入在线立案...")
            page.get_by_text("在线立案").click()
            time.sleep(2)
            
            # 3. 点击在线保全
            print("点击在线保全...")
            with page.expect_popup() as page1_info:
                page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
            
            page1 = page1_info.value
            print(f"新窗口: {page1.url}")
            time.sleep(5)
            
            # 4. 分析页面
            file_inputs = analyze_page(page1)
            
            # 5. 尝试上传文件
            print("\n" + "=" * 60)
            print("开始上传文件")
            print("=" * 60)
            
            for category, file_rel_path in files_to_upload:
                file_path = os.path.join(upload_dir, file_rel_path)
                
                if not os.path.exists(file_path):
                    print(f"\n✗ {category}: 文件不存在 - {file_rel_path}")
                    continue
                
                print(f"\n【{category}】")
                print(f"  文件: {os.path.basename(file_path)}")
                
                success = upload_file_direct(page1, file_path, file_inputs)
                
                if success:
                    print(f"  ✓ 上传成功")
                    time.sleep(2)
                else:
                    print(f"  ✗ 上传失败")
            
            # 6. 完成
            print("\n" + "=" * 60)
            print("文件上传流程完成")
            print("=" * 60)
            
            # 保持打开
            print("\n保持浏览器打开60秒供检查...")
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
