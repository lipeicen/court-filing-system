import os
import sys

def show_menu():
    print("=" * 50)
    print("法院自动立案系统 - 登录工具")
    print("=" * 50)
    print()
    print("请选择登录方式:")
    print()
    print("  [1] 自动登录 (2Captcha)")
    print("      - 需要配置 2CAPTCHA_API_KEY")
    print("      - 自动识别验证码")
    print()
    print("  [2] 手动登录")
    print("      - 显示验证码图片")
    print("      - 手动输入验证码")
    print()
    print("  [3] 测试当前会话")
    print("      - 检查是否已登录")
    print()
    print("  [0] 退出")
    print()
    print("=" * 50)

def main():
    show_menu()
    
    while True:
        choice = input("请选择 [0-3]: ").strip()
        
        if choice == "1":
            # 检查 API Key
            with open(r"C:\court-auto-filing\.env", 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '2CAPTCHA_API_KEY=' in content:
                api_key = content.split('2CAPTCHA_API_KEY=')[1].split('\n')[0].strip()
                if api_key:
                    print(f"\n使用 API Key: {api_key[:10]}...")
                    os.system(r"cd C:\court-auto-filing && python auto_login.py")
                else:
                    print("\n错误: 未配置 2CAPTCHA_API_KEY")
                    print("请在 .env 文件中设置:")
                    print("2CAPTCHA_API_KEY=your_api_key_here")
                    print("\n注册地址: https://2captcha.com/")
            else:
                print("\n错误: 未找到 2CAPTCHA_API_KEY 配置")
            
        elif choice == "2":
            print("\n启动手动登录...")
            os.system(r"cd C:\court-auto-filing && python manual_login.py")
            
        elif choice == "3":
            print("\n测试当前会话...")
            os.system(r"cd C:\court-auto-filing && python quick_test.py")
            
        elif choice == "0":
            print("\n退出")
            break
            
        else:
            print("无效选择，请重试")
        
        print()

if __name__ == "__main__":
    main()
