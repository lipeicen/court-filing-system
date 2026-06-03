import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config import settings

logger = logging.getLogger(__name__)

class BaseBrowser(ABC):
    # 浏览器基类
    
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.playwright = None
        self._closed = False
    
    async def launch(self):
        # 启动浏览器
        self.playwright = await async_playwright().start()
        
        # 加载会话状态
        storage_state = None
        if settings.SESSION_FILE.exists():
            storage_state = str(settings.SESSION_FILE)
            logger.info("加载已有会话")
        
        # 启动参数
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--start-maximized",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ]
        
        launch_options = {
            "headless": settings.BROWSER_HEADLESS,
            "slow_mo": settings.BROWSER_SLOW_MO,
            "args": launch_args,
        }
        
        # 指定Chrome路径
        chrome_path = settings.chrome_path
        if chrome_path and chrome_path != "chrome":
            launch_options["executable_path"] = chrome_path
            logger.info(f"使用Chrome: {chrome_path}")
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        # 创建上下文
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        if storage_state:
            context_options["storage_state"] = storage_state
        
        self.context = await self.browser.new_context(**context_options)
        
        # 创建页面
        self.page = await self.context.new_page()
        
        # 最大化窗口
        await self.page.evaluate("window.moveTo(0, 0); window.resizeTo(screen.width, screen.height);")
        
        # 反检测脚本
        await self._apply_stealth()
        
        logger.info("浏览器启动完成")
    
    async def _apply_stealth(self):
        # 应用反检测
        await self.page.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            window.chrome = { runtime: {} };
            window.Notification = function() {};
            window.Notification.permission = 'default';
            window.Notification.requestPermission = function() { return Promise.resolve('default'); };
        ''')
    
    async def goto(self, url: str, wait_until: str = "networkidle"):
        # 访问页面
        logger.info(f"访问: {url}")
        await self.page.goto(url, wait_until=wait_until, timeout=settings.BROWSER_TIMEOUT)
    
    async def click(self, selector: str, timeout: int = None):
        # 点击元素
        timeout = timeout or settings.BROWSER_TIMEOUT
        await self.page.click(selector, timeout=timeout)
    
    async def fill(self, selector: str, value: str):
        # 填写输入框
        await self.page.fill(selector, value)
    
    async def select_option(self, selector: str, value: str):
        # 选择下拉框
        await self.page.select_option(selector, value)
    
    async def screenshot(self, name: str = None, full_page: bool = True):
        # 截图
        if name is None:
            from datetime import datetime
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        path = settings.SCREENSHOT_DIR / f"{name}.png"
        await self.page.screenshot(path=str(path), full_page=full_page)
        logger.info(f"截图已保存: {path}")
        return path
    
    async def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = None):
        # 等待元素
        timeout = timeout or settings.BROWSER_TIMEOUT
        await self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    async def is_visible(self, selector: str) -> bool:
        # 检查元素是否可见
        element = await self.page.query_selector(selector)
        if element:
            return await element.is_visible()
        return False
    
    async def get_text(self, selector: str) -> str:
        # 获取元素文本
        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content() or ""
        return ""
    
    async def save_session(self):
        # 保存会话
        if self.context:
            await self.context.storage_state(path=str(settings.SESSION_FILE))
            logger.info(f"会话已保存: {settings.SESSION_FILE}")
    
    async def close(self):
        # 关闭浏览器
        if self._closed:
            return
        
        self._closed = True
        
        try:
            if self.context:
                await self.context.close()
                self.context = None
        except Exception as e:
            logger.warning(f"关闭context失败: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            logger.warning(f"关闭browser失败: {e}")
        
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.warning(f"关闭playwright失败: {e}")
        
        logger.info("浏览器已关闭")
    
    async def __aenter__(self):
        await self.launch()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
