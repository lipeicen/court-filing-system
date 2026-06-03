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
    # 使用JavaScript点击
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

    print('查找在线保全...')
    page.screenshot(path='online_case.png')
    print('已截图: online_case.png')

    # 使用JavaScript查找并点击保全
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

    pages = context.pages
    print('')
    print('当前有 ' + str(len(pages)) + ' 个页面:')
    for i, p in enumerate(pages):
        print('  [' + str(i) + '] ' + p.url[:80])

    if len(pages) > 1:
        page1 = pages[-1]
        print('')
        print('切换到新页面')
        time.sleep(3)

        page1.screenshot(path='form_debug.png')
        print('已截图: form_debug.png')

        html = page1.content()
        with open('form_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('HTML已保存')

        print('')
        print('分析表单...')
        texts = re.findall(r'>[^<]{2,30}<', html)
        unique_texts = set(t.strip() for t in texts if t.strip())
        print('页面文本 (' + str(len(unique_texts)) + ' 个):')
        for t in sorted(unique_texts)[:30]:
            print('  - ' + t)

    print('')
    print('等待20秒...')
    time.sleep(20)
    browser.close()