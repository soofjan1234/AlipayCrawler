"""
项目配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
BILIBILI_DATA_DIR = DATA_DIR / "bilibili_data"
DOUYIN_DATA_DIR = DATA_DIR / "douyin_data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保目录存在
for dir_path in [DATA_DIR, BILIBILI_DATA_DIR, DOUYIN_DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# 目标URL
BILIBILI_URL = "https://space.bilibili.com/420831218/dynamic"
DOUYIN_URL = "https://www.douyin.com/user/MS4wLjABAAAA4rbc75Wk1sycUT5ZT_bMSq31wqxeZp7PLY3ZzCenbIY?from_tab_name=main"

# 时间范围
START_DATE = "2024-05-01"
END_DATE = "2024-11-01"

# Selenium配置
SELENIUM_CONFIG = {
    "headless": True,  # 无头模式
    "window_size": (1920, 1080),
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "explicit_wait": 20,
}

# 浏览器配置
BROWSER_CONFIG = {
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "disable_images": False,  # 是否禁用图片加载
    "disable_javascript": False,  # 是否禁用JavaScript
}

# 爬取配置
CRAWLER_CONFIG = {
    "max_retries": 3,
    "retry_delay": 2,  # 重试延迟（秒）
    "scroll_delay": 2,  # 滚动延迟（秒）
    "request_delay": 1,  # 请求延迟（秒）
    "max_scroll_times": 50,  # 最大滚动次数
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    "rotation": "10 MB",
    "retention": "7 days",
}

# 数据存储配置
STORAGE_CONFIG = {
    "format": "json",  # 存储格式：json, csv, excel
    "encoding": "utf-8",
    "indent": 2,  # JSON缩进
}

# B站特定配置
BILIBILI_SELECTORS = {
    "dynamic_card": ".card-box",
    "publish_time": ".pub-time",
    "content_text": ".text-con",
    "images": ".img-box img",
    "like_count": ".like-info",
    "comment_count": ".comment-info",
    "repost_count": ".repost-info",
    "dynamic_type": ".dynamic-type",
}

# 抖音特定配置
DOUYIN_SELECTORS = {
    "video_card": "[data-e2e='user-post-list'] > div",
    "publish_time": "[data-e2e='browse-video-desc']",
    "description": "[data-e2e='browse-video-desc']",
    "cover_image": "img",
    "like_count": "[data-e2e='video-like-count']",
    "comment_count": "[data-e2e='video-comment-count']",
    "share_count": "[data-e2e='video-share-count']",
}