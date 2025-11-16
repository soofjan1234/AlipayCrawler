"""
抖音服务模块
提供抖音相关的登录、数据提取等功能
"""

from .login import douyin_login, get_chrome_options

__version__ = "1.0.0"
__all__ = ["douyin_login", "get_chrome_options"]