"""
法院自动立案系统 - 带文件上传功能
"""

from playwright.sync_api import sync_playwright
import time
import re
import os
import json


def solve_captcha(page):
    """解决验证码"""
    import ddddocr
    
    captcha_img = page.locator("uni-image img")
    if captcha_img.count() == 0:
        return None
    
    captcha_img.screenshot(path="captcha_upload.png")
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open("captcha_upload.png", 'rb') as f:
        return ocr.classification(f.read())


def auto_login(page):
    """自动登录"""
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


def upload_files(page1, upload_dir, file_mapping):
    """上传文件到保全系统"""
    print("\n" + "=" * 60)
    print("开始上传文件")
    print("=" * 60)
    
    # 查找所有上传按钮
    print("\n查找上传控件...")
    
    # 方法1: 查找input[type=file]
    file_inputs = page1.locator("input[type='file']").all()
    print(f"找到 {len(file_inputs)} 个文件上传input")
    
    # 方法2: 查找包含"上传"文本的元素
    upload_buttons = page1.locator("text=/上传|选择文件|附件/i").all()
    print(f"找到 {len(upload_buttons)} 个上传按钮")
    
    # 方法3: 查找点击上传区域
    upload_areas = page1.locator("[class*='upload'], [class*='file-upload'], .el-upload").all()
    print(f"找到 {len(upload_areas)} 个上传区域")
    
    # 遍历文件映射并上传
    for category, info in file_mapping.items():
        print(f"\n【{category}】")
        
        for file_rel_path in info['files']:
            file_path = os.path.join(upload_dir, file_rel_path)
            
            if not os.path.exists(file_path):
                print(f"  ✗ 文件不存在: {file_path}")
                continue
            
            print(f"  准备上传: {os.path.basename(file_path)}")
            
            # 查找对应的上传控件
            # 策略: 根据类别名称查找附近的上传按钮
            try:
                # 先查找包含类别名称的元素
                category_label = page1.locator(f"text={category}").first
                
                if category_label.is_visible():
                    # 在该元素附近查找上传按钮
                    # 通常上传按钮在右侧或下方
                    print(f"    找到类别标签: {category}")
                    
                    # 尝试点击上传按钮（可能需要根据实际情况调整）
                    # 这里使用通用的文件上传方法
                    
                    # 查找当前可见的文件input
                    visible_inputs = [inp for inp in file_inputs if inp.is_visible()]
                    
                    if visible_inputs:
                        # 使用第一个可见的input上传
                        visible_inputs[0].set_input_files(file_path)
                        print(f"    ✓ 已上传: {os.path.basename(file_path)}")
                        time.sleep(2)
                    else:
                        # 尝试触发文件选择对话框
                        print(f"    尝试点击上传区域...")
                        # 这里需要根据实际页面结构调整
                        
            except Exception as e:
                print(f"    ✗ 上传失败: {e}")
    
    print("\n文件上传完成")


def navigate_to_upload_page(page):
    """导航到文件上传页面"""
    print("\n" + "=" * 50)
    print("导航到保全申请页面")
    print("=" * 50)
    
    # 点击在线立案
    print("点击在线立案...")
    page.get_by_text("在线立案").click()
    time.sleep(2)
    
    # 点击在线保全
    print("点击在线保全...")
    with page.expect_popup() as page1_info:
        page.locator("uni-view").filter(has_text=re.compile(r"^保全在线保全$")).locator("uni-view").nth(3).click()
    
    page1 = page1_info.value
    print(f"新窗口已打开: {page1.url}")
    time.sleep(3)
    
    return page1


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("法院自动立案系统 - 文件上传")
    print("=" * 60)
    
    # 文件路径配置
    upload_dir = r"C:\court-auto-filing\uploads\保全2026001"
    
    # 文件映射
    file_mapping = {
        "保全申请书": {
            "files": ["保全申请书\\01_保全申请书.pdf"],
            "type": "保全申请书"
        },
        "起诉状": {
            "files": ["起诉状\\起诉状.doc"],
            "type": "起诉状"
        },
        "身份证明材料": {
            "files": [
                "身份证明材料\\03_申请人证照.pdf",
                "身份证明材料\\04_被申请人身份证.pdf",
                "身份证明材料\\05_代理人授权书.pdf"
            ],
            "type": "身份证明材料"
        },
        "证据材料": {
            "files": ["证据材料\\证据材料.doc"],
            "type": "证据材料"
        },
        "担保材料": {
            "files": [
                "担保材料\\06_担保函.pdf",
                "担保材料\\07_保证人证照.pdf"
            ],
            "type": "担保材料"
        },
        "其他材料": {
            "files": ["其他材料\\其他材料.doc"],
            "type": "其他材料"
        }
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录
            if not auto_login(page):
                print("登录失败")
                return
            
            # 2. 导航到上传页面
            page1 = navigate_to_upload_page(page)
            
            # 3. 等待页面完全加载
            print("\n等待页面加载...")
            time.sleep(5)
            
            # 4. 截图查看当前页面
            page1.screenshot(path=r"C:\court-auto-filing\upload_page.png")
            print("页面截图已保存")
            
            # 5. 上传文件
            upload_files(page1, upload_dir, file_mapping)
            
            # 6. 保持打开供检查
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
