import asyncio
import os
import sys
import asyncio
import pymysql

sys.path.insert(0, r"C:\court-auto-filing")

from utils.ocr_captcha import ocr_solver
from core.browser_controller import CourtBrowser
from config import settings

def load_system_config(created_by=''):
    """按 created_by 读取对应的法院系统账号配置"""
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST, port=settings.DB_PORT, user=settings.DB_USER,
            password=settings.DB_PASSWORD, database=settings.DB_NAME,
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT config_key, config_value FROM system_config")
        config = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        
        if created_by:
            username = config.get(f'login_username_{created_by}', '')
            password = config.get(f'login_password_{created_by}', '')
            user_type = config.get(f'login_user_type_{created_by}', '个人用户')
            if username and password:
                config['COURT_USERNAME'] = username
                config['COURT_PASSWORD'] = password
                config['COURT_USER_TYPE'] = user_type
                print(f"使用账号配置: {created_by} -> {username}")
                return config
        
        # 兜底：使用 .env 中的配置
        config['COURT_USERNAME'] = settings.COURT_USERNAME
        config['COURT_PASSWORD'] = settings.COURT_PASSWORD
        config['COURT_USER_TYPE'] = '个人用户'
        return config
    except Exception as e:
        print(f"加载系统配置失败: {e}")
        return {}

"""自动登录 - 使用 OCR"""
async def main(created_by=''):
    
    # 加载对应账号配置
    cfg = load_system_config(created_by)
    court_username = cfg.get('COURT_USERNAME', settings.COURT_USERNAME)
    court_password = cfg.get('COURT_PASSWORD', settings.COURT_PASSWORD)
    
    browser = CourtBrowser()
    
    try:
        await browser.launch()
        
        print("=" * 50)
        print("法院自动立案系统 - 自动登录 (OCR)")
        print("=" * 50)
        
        # 访问登录页
        await browser.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
        print("[1/5] 选择律师用户...")
        await browser.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.textContent && el.textContent.includes('律师用户')) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(1)
        
        # 获取输入框
        inputs = await browser.page.query_selector_all(".uni-input-input")
        print(f"[2/5] 找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 2:
            await inputs[0].fill(court_username)
            await inputs[1].fill(court_password)
            print("[3/5] 已填写账号密码")
        
        # 处理验证码
        if len(inputs) >= 3:
            captcha_img = await browser.page.query_selector("img")
            if captcha_img:
                captcha_path = os.path.join(settings.SCREENSHOT_DIR, "captcha_auto.png")
                await captcha_img.screenshot(path=captcha_path)
                print(f"[4/5] 验证码已保存: {captcha_path}")
                
                # 使用本地 OCR 识别
                captcha_code = ocr_solver.recognize(captcha_path)
                
                if captcha_code:
                    await inputs[2].fill(captcha_code)
                    
                    # 点击登录
                    await browser.page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('*');
                            for (const el of elements) {
                                if (el.textContent && el.textContent.trim() === '登录') {
                                    el.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    print("[5/5] 已点击登录按钮")
                    
                    await asyncio.sleep(5)
                    
                    # 检查登录结果
                    if "login" not in browser.page.url:
                        print("\n✓ 登录成功!")
                        await browser.save_session()
                        print("✓ 会话已保存")
                    else:
                        print("\n✗ 登录失败，验证码可能识别错误")
                else:
                    print("\n✗ 验证码识别失败")
            else:
                print("未找到验证码图片")
        
        print("\n等待 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
