import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # 法院网站配置
    COURT_BASE_URL: str = Field(default="https://zxfw.court.gov.cn/zxfw", description="法院网站基础URL")
    
    # 登录配置
    COURT_USERNAME: str = Field(default="", description="法院账号")
    COURT_PASSWORD: str = Field(default="", description="法院密码")
    
    # 验证码配置
    CAPTCHA_SERVICE: str = Field(default="2captcha", description="验证码服务: 2captcha/local/manual")
    CAPTCHA_API_KEY: str = Field(default="", description="验证码API密钥")
    CAPTCHA_TIMEOUT: int = Field(default=120, description="验证码识别超时(秒)")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别: DEBUG/INFO/WARNING/ERROR")
    
    # SQLite 配置
    USE_SQLITE: bool = Field(default=False, description="是否使用 SQLite")
    
    # 2Captcha 配置
    CAPTCHA_API_KEY_2CAPTCHA: str = Field(default="", description="2Captcha API密钥")
    
    # 浏览器配置
    BROWSER_HEADLESS: bool = Field(default=False, description="无头模式")
    BROWSER_SLOW_MO: int = Field(default=500, description="操作延迟(ms)")
    BROWSER_TIMEOUT: int = Field(default=30000, description="页面加载超时(ms)")
    BROWSER_EXECUTABLE_PATH: Optional[str] = Field(default=None, description="Chrome可执行文件路径")
    
    # 数据库配置
    DB_HOST: str = Field(default="localhost", description="数据库主机")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户")
    DB_PASSWORD: str = Field(default="", description="数据库密码")
    DB_NAME: str = Field(default="court_db", description="数据库名称")
    
    # 文件路径配置
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent, description="项目根目录")
    MATERIALS_BASE_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "uploads", description="材料基础路径")
    SESSION_FILE: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "court_session.json", description="会话文件")
    LOG_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "logs", description="日志目录")
    SCREENSHOT_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "screenshots", description="截图目录")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return f"sqlite:///{self.BASE_DIR / 'court.db'}"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def chrome_path(self) -> str:
        if self.BROWSER_EXECUTABLE_PATH and Path(self.BROWSER_EXECUTABLE_PATH).exists():
            return str(self.BROWSER_EXECUTABLE_PATH)
        
        # 自动检测常见路径
        common_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe",
        ]
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return "chrome"  # 使用系统PATH中的chrome

# 全局配置实例
settings = Settings()

# 确保目录存在
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
settings.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
settings.MATERIALS_BASE_PATH.mkdir(parents=True, exist_ok=True)
