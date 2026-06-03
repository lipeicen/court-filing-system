import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright
from core.base_browser import BaseBrowser
from utils.captcha_handler import CaptchaHandler
from config import settings

logger = logging.getLogger(__name__)

class CourtBrowser(BaseBrowser):
    # 法院浏览器控制器
    
    def __init__(self):
        super().__init__()
        self.captcha = CaptchaHandler(settings.CAPTCHA_SERVICE, settings.CAPTCHA_API_KEY)
    
    async def login(self, username: str = None, password: str = None) -> bool:
        # 登录法院系统
        username = username or settings.COURT_USERNAME
        password = password or settings.COURT_PASSWORD
        
        if not username or not password:
            raise ValueError("账号密码不能为空")
        
        # 先检查是否已登录
        logger.info("检查登录状态...")
        await self.goto("https://zxfw.court.gov.cn/zxfw/#/pagesIndex/index/index")
        await asyncio.sleep(2)
        
        if await self._is_logged_in():
            logger.info("已经登录，跳过登录步骤")
            return True
        
        logger.info("开始登录...")
        await self.goto("https://zxfw.court.gov.cn/zxfw/#/pagesGrxx/pc/login/index")
        await asyncio.sleep(3)
        
        # 选择律师用户
        try:
            await self.click("text=律师用户", timeout=5000)
            await asyncio.sleep(1)
            logger.info("已选择律师用户")
        except Exception as e:
            logger.warning(f"选择律师用户失败: {e}")
        
        # 选择密码登录
        try:
            await self.click("text=密码登录", timeout=3000)
            await asyncio.sleep(1)
        except:
            pass
        
        # 获取输入框
        inputs = await self.page.query_selector_all(".uni-input-input")
        logger.info(f"找到 {len(inputs)} 个输入框")
        
        if len(inputs) >= 3:
            await inputs[0].fill(username)
            await inputs[1].fill(password)
            
            # 处理验证码
            if settings.CAPTCHA_SERVICE == "manual":
                captcha_code = input("请输入验证码: ")
                await inputs[2].fill(captcha_code)
            else:
                try:
                    captcha_code = await self.captcha.solve_from_element(self.page, ".uni-input-input:nth-child(3)")
                    await inputs[2].fill(captcha_code)
                except Exception as e:
                    logger.warning(f"自动识别验证码失败: {e}")
                    captcha_code = input("请手动输入验证码: ")
                    await inputs[2].fill(captcha_code)
        else:
            raise Exception(f"输入框数量不对: {len(inputs)}")
        
        # 点击登录按钮
        try:
            await self.click(".fd-login-btn", timeout=5000)
            logger.info("点击登录按钮")
        except:
            # 尝试其他选择器
            await self.click("button:has-text('登录')", timeout=5000)
        
        await asyncio.sleep(5)
        
        # 检查登录结果
        if await self._is_logged_in():
            logger.info("登录成功")
            await self.save_session()
            return True
        
        await self.screenshot("login_failed")
        raise Exception("登录失败")
    
    async def _is_logged_in(self) -> bool:
        # 检查是否已登录
        current_url = self.page.url
        logger.info(f"当前URL: {current_url}")
        
        if "login" not in current_url and "pagesGrxx" not in current_url:
            return True
        
        try:
            await self.wait_for_selector("text=在线立案", timeout=3000)
            return True
        except:
            pass
        
        try:
            await self.wait_for_selector("text=在线保全", timeout=2000)
            return True
        except:
            pass
        
        return False
    
    async def start_preservation(self):
        # 开始保全立案流程
        logger.info("开始保全立案流程...")
        
        # 1. 点击在线立案（增加超时）
        try:
            await self.click("text=在线立案", timeout=10000)
            await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"点击在线立案失败: {e}")
            # 尝试JavaScript点击
            await self.page.evaluate('() => { document.querySelector("a[href*=\'preservation\']").click(); }')
            await asyncio.sleep(2)
        
        # 2. 点击在线保全
        try:
            await self.click("text=在线保全", timeout=10000)
            await asyncio.sleep(3)
        except Exception as e:
            logger.warning(f"点击在线保全失败: {e}")
            # 直接访问保全URL
            await self.goto("https://zxfw.court.gov.cn/zxfw/#/pagesBaqx/pc/index/index")
            await asyncio.sleep(3)
        
        # 3. 使用JavaScript处理复杂的点击逻辑
        click_result = await self.page.evaluate('''
            () => {
                const allElements = document.querySelectorAll('*');
                
                // 强制显示所有隐藏元素
                for (const el of allElements) {
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                        el.style.opacity = '1';
                    }
                }
                
                // 点击"诉讼保全须知"标签
                let tabClicked = false;
                for (const el of allElements) {
                    if ((el.textContent || '').includes('诉讼保全须知')) {
                        el.click();
                        if (el.parentElement) el.parentElement.click();
                        tabClicked = true;
                        break;
                    }
                }
                
                // 点击"我已阅读"单选框
                let radioClicked = false;
                for (const el of allElements) {
                    if ((el.textContent || '').includes('我已阅读')) {
                        el.click();
                        const radio = el.querySelector('input[type="radio"]');
                        if (radio) {
                            radio.checked = true;
                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                        radioClicked = true;
                        break;
                    }
                }
                
                // 点击"创建保全申请"按钮
                let btnClicked = false;
                for (const el of allElements) {
                    if ((el.textContent || '').includes('创建保全申请')) {
                        const btn = el.closest('button') || el;
                        btn.disabled = false;
                        btn.classList.remove('is-disabled');
                        btn.style.pointerEvents = 'auto';
                        btn.click();
                        btnClicked = true;
                        break;
                    }
                }
                
                return { tabClicked, radioClicked, btnClicked };
            }
        ''')
        
        logger.info(f"点击结果: tab={click_result['tabClicked']}, radio={click_result['radioClicked']}, btn={click_result['btnClicked']}")
        
        await asyncio.sleep(5)
        logger.info(f"当前URL: {self.page.url}")
    
    async def fill_basic_info(self, case_data: dict):
        # 填写基本信息
        logger.info("填写基本信息...")
        await self.screenshot("basic_info_before")
        
        # 申请法院
        court_selected = False
        try:
            await self.click("[placeholder*='法院'], .court-select")
            await asyncio.sleep(1)
            await self.fill(".search-input, input[placeholder*='搜索']", case_data["court_name"])
            await asyncio.sleep(1)
            await self.click(f"text={case_data['court_name']}")
            court_selected = True
        except Exception as e:
            logger.warning(f"选择法院失败: {e}")
        
        if not court_selected:
            try:
                selects = await self.page.query_selector_all("select")
                if selects:
                    await selects[0].select_option(case_data["court_name"])
            except:
                pass
        
        # 保全类型
        try:
            await self.click(f"text={case_data['preservation_type']}")
        except:
            logger.warning(f"选择保全类型失败")
        
        # 保全类别
        try:
            await self.click(f"text={case_data['preservation_category']}")
        except:
            logger.warning(f"选择保全类别失败")
        
        # 申请保全金额
        try:
            amount_inputs = await self.page.query_selector_all("input[type='number'], input[placeholder*='金额']")
            if amount_inputs:
                await amount_inputs[0].fill(str(case_data["apply_amount"]))
        except Exception as e:
            logger.warning(f"填写金额失败: {e}")
        
        # 担保情况
        try:
            await self.click(f"text={case_data['guarantee_status']}")
        except:
            pass
        
        # 提交身份人
        try:
            await self.click(f"text={case_data['submitter_type']}")
        except:
            pass
        
        # 点击下一步/创建
        try:
            await self.click("text=创建, text=下一步, text=保存")
            await asyncio.sleep(3)
        except Exception as e:
            logger.warning(f"点击下一步失败: {e}")
        
        await self.screenshot("basic_info_after")
    
    async def fill_applicant(self, applicant: dict):
        # 填写申请人
        logger.info("填写申请人信息...")
        
        await self.click("text=添加申请人")
        await asyncio.sleep(1)
        await self.click("text=法人")
        await asyncio.sleep(0.5)
        
        await self.fill("input[placeholder*='单位名称']", applicant["name"])
        await self.fill("input[placeholder*='证照号码']", applicant["cert_no"])
        await self.fill("input[placeholder*='法定代表人']", applicant["legal_person"])
        await self.fill("input[placeholder*='手机']", applicant["phone"])
        await self.fill("input[placeholder*='地址']", applicant["address"])
        
        await self.click("text=保存")
        await asyncio.sleep(1)
        logger.info("申请人填写完成")
    
    async def fill_respondent(self, respondent: dict):
        # 填写被申请人
        logger.info("填写被申请人信息...")
        
        await self.click("text=添加被申请人")
        await asyncio.sleep(1)
        await self.click("text=自然人")
        await asyncio.sleep(0.5)
        
        await self.fill("input[placeholder*='姓名']", respondent["name"])
        await self.fill("input[placeholder*='身份证']", respondent["id_card"])
        await self.click(f"text={respondent['gender']}")
        await self.fill("input[placeholder*='地址']", respondent["address"])
        
        await self.click("text=保存")
        await asyncio.sleep(1)
        logger.info("被申请人填写完成")
    
    async def fill_agent(self, agent: dict):
        # 填写代理人
        logger.info("填写代理人信息...")
        
        await self.click("text=添加代理人")
        await asyncio.sleep(1)
        
        # 勾选复选框
        checkbox = await self.page.query_selector("input[type='checkbox']")
        if checkbox:
            await checkbox.check()
        
        await self.fill("input[placeholder*='姓名']", agent["name"])
        await self.fill("input[placeholder*='身份证']", agent["id_card"])
        await self.fill("input[placeholder*='手机']", agent["phone"])
        await self.fill("input[placeholder*='执业证号']", agent["cert_no"])
        await self.fill("input[placeholder*='律所']", agent["law_firm"])
        
        await self.click("text=保存")
        await asyncio.sleep(1)
        logger.info("代理人填写完成")
    
    async def fill_property_clues(self, clues: list):
        # 填写财产线索
        logger.info(f"填写 {len(clues)} 条财产线索...")
        
        for clue in clues:
            await self.click("text=添加财产线索")
            await asyncio.sleep(1)
            
            await self.click(f"text={clue['type']}")
            
            if clue.get("owner"):
                await self.select_option("select[name='owner']", clue["owner"])
            
            if clue.get("amount"):
                await self.fill("input[name='amount']", str(clue["amount"]))
            
            if clue.get("value"):
                await self.fill("input[placeholder*='价值']", str(clue["value"]))
            
            if clue.get("location"):
                await self.fill("input[name='location']", clue["location"])
            
            await self.click("text=保存")
            await asyncio.sleep(1)
        
        logger.info("财产线索填写完成")
    
    async def fill_guarantee(self, guarantee: dict):
        # 填写担保信息
        logger.info("填写担保信息...")
        
        await self.click("text=添加担保信息")
        await asyncio.sleep(1)
        
        await self.select_option("select[name='guaranteeType']", "提供保证人")
        await self.fill("input[placeholder*='担保人']", guarantee["guarantor"])
        await self.fill("input[placeholder*='价值']", str(guarantee["value"]))
        
        if guarantee.get("description"):
            await self.fill("textarea[name='description']", guarantee["description"])
        
        await self.click("text=保存")
        await asyncio.sleep(1)
        logger.info("担保信息填写完成")
    
    async def upload_file(self, file_path: str, category: str):
        # 上传文件
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"文件不存在，跳过: {file_path}")
            return False
        
        logger.info(f"上传文件: {category} - {path.name}")
        
        try:
            # 尝试直接找到文件输入框
            file_input = await self.page.query_selector(f"div:has-text('{category}') >> input[type='file']")
            if file_input:
                await file_input.set_input_files(str(path))
            else:
                # 使用文件选择器
                async with self.page.expect_filechooser() as fc:
                    await self.click(f"text=上传{category}")
                filechooser = await fc.value
                await filechooser.set_files(str(path))
            
            # 等待上传完成
            await self.wait_for_selector("text=上传成功, .upload-success", timeout=30000)
            logger.info(f"上传成功: {category}")
            return True
            
        except Exception as e:
            logger.error(f"上传失败 {category}: {e}")
            return False
    
    async def preview_and_submit(self) -> dict:
        # 预览并提交
        logger.info("预览并提交...")
        
        await self.click("text=提交")
        await asyncio.sleep(2)
        
        try:
            await self.wait_for_selector("text=提交成功, .success", timeout=30000)
            case_no = await self.get_text(".case-number")
            return {"success": True, "court_case_no": case_no}
        except:
            error = await self.get_text(".error-message, .tips")
            return {"success": False, "message": error or "提交失败"}
