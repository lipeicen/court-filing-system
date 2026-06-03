from playwright.sync_api import sync_playwright
import time
import re
import ddddocr

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print('登录...')
    page.goto('https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index')
    time.sleep(3)

    page.get_by_text('律师用户').click()
    time.sleep(1)

    inputs = page.locator('input').all()
    inputs[0].fill('13723715831')
    inputs[1].fill('HU1234pp')
    time.sleep(1)

    print('识别验证码...')
    try:
        captcha_img = page.locator('uni-image img').first
        captcha_img.screenshot(path='debug_captcha.png')
        ocr = ddddocr.DdddOcr(show_ad=False)
        with open('debug_captcha.png', 'rb') as f:
            img_bytes = f.read()
        captcha = ocr.classification(img_bytes)
        print('验证码: ' + captcha)
        if captcha and len(captcha) == 4:
            inputs[2].fill(captcha)
    except Exception as e:
        print('失败: ' + str(e))

    page.get_by_text('登录', exact=True).click()
    time.sleep(5)

    if '在线立案' in page.content():
        print('登录成功!')
    else:
        print('登录失败')
        browser.close()
        exit()

    print('点击在线立案...')
    page.evaluate('''() => {
        const elements = document.querySelectorAll('*');
        for (let el of elements) {
            if (el.textContent && el.textContent.includes('在线立案')) {
                el.click();
                break;
            }
        }
    }''')
    time.sleep(5)

    print('点击在线保全...')
    page.evaluate('''() => {
        const elements = document.querySelectorAll('*');
        for (let el of elements) {
            if (el.textContent && el.textContent.includes('保全') && el.textContent.includes('在线')) {
                el.click();
                break;
            }
        }
    }''')
    time.sleep(5)

    # 检查URL是否变化
    print('当前URL: ' + page.url)
    page.screenshot(path='after_click.png')
    print('已截图: after_click.png')

    # 查找表单元素
    html = page.content()
    with open('after_click.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('HTML已保存')

    print('')
    print('分析页面...')
    texts = re.findall(r'>[^<]{2,30}<', html)
    unique_texts = set(t.strip() for t in texts if t.strip())
    print('页面文本 (' + str(len(unique_texts)) + ' 个):')
    for t in sorted(unique_texts)[:30]:
        print('  - ' + t)

    print('')
    print('等待20秒...')
    time.sleep(20)
    browser.close()