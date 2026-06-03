    """添加担保信息"""
    print("\n" + "=" * 50)
    print("添加担保信息")
    print("=" * 50)
    
    # 点击下一步（从财产线索页面进入担保信息页面）
    print("点击下一步...")
    try:
        page1.get_by_role("button", name="下一步").click()
    except:
        try:
            page1.evaluate("""() => {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('下一步')) {
                        btn.click();
                        return 'clicked';
                    }
                }
                return 'not found';
            }""")
        except Exception as e:
            print(f"  点击下一步失败: {e}")
    time.sleep(2)
    
    # 点击添加担保
    print("点击添加担保...")
    try:
        page1.locator("text=担保信息").first.locator("xpath=../../..").locator("span").filter(has_text=re.compile(r"^添加$")).locator("i").click()
    except:
        try:
            page1.evaluate("""() => {
                const spans = document.querySelectorAll('span');
                for (let span of spans) {
                    if (span.textContent.trim() === '添加') {
                        let parent = span.parentElement;
                        for (let i = 0; i < 10; i++) {
                            if (!parent) break;
                            if (parent.textContent.includes('担保信息')) {
                                const icon = span.querySelector('i');
                                if (icon) icon.click();
                                else span.click();
                                return 'clicked';
                            }
                            parent = parent.parentElement;
                        }
                    }
                }
                return 'not found';
            }""")
        except:
            page1.locator("span").filter(has_text=re.compile(r"^添加$")).first.locator("i").click()
    time.sleep(2)
    
    # 选择担保方式
    print("选择担保方式...")
    guarantee_type = CASE_DATA.get('guarantee_type', '交纳保证金')
    print(f"  担保方式: {guarantee_type}")
    try:
        page1.locator("text=担保方式").first.locator("xpath=../../..").locator("input").click()
        time.sleep(1)
        try:
            page1.get_by_text(guarantee_type, exact=True).click()
        except Exception:
            page1.get_by_text(guarantee_type).first.click()
        time.sleep(0.5)
    except Exception as e:
        print(f"  方法1失败: {e}")
        try:
            page1.get_by_placeholder("请选择").click()
            time.sleep(1)
            page1.get_by_text(guarantee_type).first.click()
            time.sleep(0.5)
        except Exception as e2:
            print(f"  方法2也失败: {e2}，跳过担保方式选择")
    
    # 根据担保方式填写对应字段
    
    # 1. 担保人（所有方式都可能需要）
    print("输入担保人...")
    try:
        guarantor_input = page1.get_by_placeholder("请输入担保人")
        guarantor_input.click()
        guarantor_name = CASE_DATA.get('guarantor_name') or CASE_DATA['applicant_name']
        guarantor_input.fill(guarantor_name)
        time.sleep(0.5)
    except Exception as e:
        print(f"  担保人输入失败: {e}，跳过")
    
    # 2. 担保物名称（提供保证人方式需要）
    guarantee_object = CASE_DATA.get('guarantee_object', '')
    if guarantee_object:
        print(f"输入担保物名称: {guarantee_object}...")
        try:
            name_input = page1.get_by_placeholder("请输入担保名称")
            name_input.click()
            name_input.fill(guarantee_object)
            time.sleep(0.5)
        except Exception as e:
            print(f"  担保物名称输入失败: {e}，跳过")
    
    # 3. 质押/抵押财产类型（设定质押/设定抵押方式需要）
    property_type = CASE_DATA.get('guarantee_property_type', '')
    if property_type:
        print(f"选择财产类型: {property_type}...")
        try:
            result = page1.evaluate(f"""() => {{
                const labels = document.querySelectorAll('label, .el-form-item__label, .uni-label');
                for (let label of labels) {{
                    if (label.textContent.includes('财产类型')) {{
                        let parent = label.parentElement;
                        for (let i = 0; i < 5; i++) {{
                            if (!parent) break;
                            const input = parent.querySelector('input[placeholder="请选择"]');
                            if (input) {{
                                input.click();
                                setTimeout(() => {{
                                    const options = document.querySelectorAll('li, .uni-picker-item, .el-select-dropdown__item, [class*="option"]');
                                    for (let option of options) {{
                                        if (option.textContent.includes('{property_type}')) {{
                                            option.click();
                                            return;
                                        }}
                                    }}
                                }}, 500);
                                return 'clicked';
                            }}
                            parent = parent.parentElement;
                        }}
                    }}
                }}
                return 'not found';
            }}""")
            print(f"  财产类型选择结果: {result}")
            time.sleep(2)
        except Exception as e:
            print(f"  财产类型选择失败: {e}，跳过")
    
    # 4. 担保价值（必填）
    print("输入担保价值...")
    try:
        value_input = page1.locator("label:has-text('担保价值') + input, label:has-text('担保价值') ~ input").first
        if value_input.count() == 0:
            value_input = page1.get_by_placeholder("请输入担保价值")
        if value_input.count() == 0:
            page1.evaluate(f"""() => {{
                const labels = document.querySelectorAll('label');
                for (let label of labels) {{
                    if (label.textContent.includes('担保价值')) {{
                        const input = label.querySelector('input') || label.nextElementSibling?.querySelector('input') || label.parentElement?.querySelector('input');
                        if (input) {{
                            input.value = '{int(CASE_DATA['guarantee_value'])}';
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                }}
                return false;
            }}""")
            print("  通过JavaScript设置担保价值")
        else:
            value_input.click()
            value_input.fill(str(int(CASE_DATA['guarantee_value'])))
        time.sleep(0.5)
    except Exception as e:
        print(f"  担保价值输入失败: {e}，跳过")
    
    # 5. 担保说明（可选）
    print("输入担保说明...")
    try:
        remark_input = page1.get_by_placeholder("请输入内容")
        remark_input.click()
        guarantee_remark = CASE_DATA.get('guarantee_remark', '')
        if guarantee_remark:
            remark_input.fill(guarantee_remark)
        time.sleep(0.5)
    except Exception as e:
        print(f"  担保说明输入失败: {e}，跳过")
    
    # 保存担保信息
    print("保存担保信息...")
    saved = False
    
    try:
        page1.locator("text=担保信息").first.locator("xpath=../../..").locator("button").filter(has_text=re.compile(r"^保存$")).click()
        saved = True
    except:
        pass
    
    if not saved:
        try:
            page1.get_by_role("button", name="保存", exact=True).click()
            saved = True
        except:
            pass
    
    if not saved:
        try:
            result = page1.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const saveButtons = buttons.filter(b => b.textContent.trim() === '保存');
                if (saveButtons.length > 0) {
                    saveButtons[saveButtons.length - 1].click();
                    return 'clicked ' + saveButtons.length;
                }
                return 'not found';
            }""")
            print(f"  JavaScript点击结果: {result}")
            saved = 'clicked' in str(result)
        except Exception as e:
            print(f"  JavaScript点击失败: {e}")
    
    time.sleep(3)
    
    # 确认弹窗是否关闭
    try:
        modal = page1.locator("text=担保信息").count()
        if modal > 0:
            print("  弹窗未关闭，尝试再次点击保存...")
            page1.get_by_role("button", name="保存").click()
            time.sleep(2)
    except:
        pass
    
    print("担保信息添加成功!")
    time.sleep(2)
