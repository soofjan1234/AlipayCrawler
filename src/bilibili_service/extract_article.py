"""
B站动态文章提取模块

该模块提供了从B站用户动态页面提取文章数据的功能，
支持提取动态的基本信息、互动数据和媒体内容。
"""

import time
import logging
import sys
import os
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.bilibili_service.login import get_chrome_options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliArticleExtractor:
    """B站动态文章提取器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化提取器
        
        Args:
            headless: 是否使用无头模式
        """
        self.chrome_options = get_chrome_options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.driver = None
        
    def __enter__(self):
        """上下文管理器入口"""
        try:
            # 尝试使用webdriver-manager自动管理ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            logger.info("✅ 使用webdriver-manager成功启动Chrome")
        except Exception as e:
            try:
                # 如果失败，尝试直接使用系统Chrome
                self.driver = webdriver.Chrome(options=self.chrome_options)
                logger.info("✅ 使用系统Chrome成功启动")
            except Exception as e2:
                logger.error(f"❌ Chrome启动失败: {e2}")
                # 最后尝试不使用任何配置
                try:
                    self.driver = webdriver.Chrome()
                    logger.info("✅ 使用默认配置启动Chrome")
                except Exception as e3:
                    logger.error(f"❌ 所有Chrome启动方式都失败: {e3}")
                    raise e3
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.driver:
            self.driver.quit()
            
    def _wait_for_login(self, timeout: int = 60) -> bool:
        """
        等待用户登录完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否登录成功
        """
        logger.info("检查登录状态...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            if "passport.bilibili.com" not in current_url and "login" not in current_url:
                logger.info("✅ 检测到登录成功！")
                return True
            time.sleep(2)
            
        logger.warning("⏰ 登录超时")
        return False
        
    def _extract_interaction_data(self, card_element) -> Dict[str, str]:
        """
        提取互动数据（点赞、评论、转发）
        
        Args:
            card_element: 动态卡片元素
            
        Returns:
            Dict: 包含点赞数、评论数、转发数的字典
        """
        interaction_data = {
            "点赞数": "0",
            "评论数": "0", 
            "转发数": "0"
        }
        
        # 提取点赞数
        try:
            like_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-action.like")
            like_text = like_element.text.strip()
            if like_text and like_text != "点赞":
                interaction_data["点赞数"] = like_text
            else:
                interaction_data["点赞数"] = "0"
        except NoSuchElementException:
            logger.debug("未找到点赞元素")
            
        # 提取评论数
        try:
            comment_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-action.comment")
            comment_text = comment_element.text.strip()
            if comment_text and comment_text != "评论":
                interaction_data["评论数"] = comment_text
            else:
                interaction_data["评论数"] = "0"
        except NoSuchElementException:
            logger.debug("未找到评论元素")
            
        # 提取转发数
        try:
            repost_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-action.forward")
            repost_text = repost_element.text.strip()
            if repost_text and repost_text != "转发":
                interaction_data["转发数"] = repost_text
            else:
                interaction_data["转发数"] = "0"
        except NoSuchElementException:
            logger.debug("未找到转发元素")
            
        return interaction_data
        
    def _extract_media_content(self, card_element) -> Dict[str, str]:
        """
        提取媒体内容（图片、视频）
        
        Args:
            card_element: 动态卡片元素
            
        Returns:
            Dict: 包含图片链接和视频链接的字典
        """
        media_data = {
            "图片链接": "",
            "视频链接": ""
        }
        
        # 提取图片链接
        try:
            # 尝试多种图片选择器（B站图片结构复杂，需要多种选择器）
            image_selectors = [
                "picture.b-img__inner img",                    # B站新版图片结构 - 用户发现的
                ".b-img__inner img",                           # B站新版图片结构（不限定picture标签）
                "picture img[src*='hdslb.com']",              # picture标签中的B站CDN图片
                ".bili-album__preview__picture__img img",      # 相册预览图
                ".bili-dyn-card-img img",                      # 动态卡片图片
                ".bili-rich-text__content img",                # 富文本内容中的图片
                ".img-box img",                               # 图片盒子
                ".album__image img",                          # 相册图片
                ".bili-dyn-card__image img",                  # 动态卡片图片
                ".dyn-card-opus img",                         # opus类型动态的图片
                ".bili-dyn-content img",                      # 动态内容中的图片
                "img[src*='hdslb.com']",                       # B站CDN图片
                "img[src*='i0.hdslb.com']",                   # B站图片服务器
                "img[src*='i1.hdslb.com']",                   # B站图片服务器
                "img[src*='i2.hdslb.com']",                   # B站图片服务器
                "img[src*='bfs/new_dyn']",                    # B站新版动态图片路径
                "img[srcset*='hdslb.com']",                   # 带srcset属性的B站图片
                "source[srcset*='hdslb.com']"                 # source标签中的B站图片
            ]
            
            img_element = None
            img_src = ""
            
            # 尝试每个选择器
            for selector in image_selectors:
                try:
                    img_element = card_element.find_element(By.CSS_SELECTOR, selector)
                    # 如果是source标签，尝试获取srcset属性
                    if selector.startswith("source"):
                        img_src = img_element.get_attribute("srcset")
                        if img_src:
                            # srcset可能包含多个URL，取第一个
                            img_src = img_src.split()[0]
                    else:
                        img_src = img_element.get_attribute("src")
                    
                    if img_src:
                        break
                except NoSuchElementException:
                    continue
            
            # 处理相对路径
            if img_src and img_src.startswith("//"):
                img_src = "https:" + img_src
            
            media_data["图片链接"] = img_src or ""
        except NoSuchElementException:
            logger.debug("未找到图片元素")
                
            # 提取视频链接
            try:
                video_element = card_element.find_element(By.CSS_SELECTOR, "video source, .video-box video, .media video")
                media_data["视频链接"] = video_element.get_attribute("src") or ""
            except NoSuchElementException:
                logger.debug("未找到视频元素")
                
        return media_data
        
    def _extract_single_dynamic(self, card_element) -> Dict[str, Any]:
        """
        提取单个动态的完整数据
        
        Args:
            card_element: 动态卡片元素
            
        Returns:
            Dict: 动态数据字典
        """
        dynamic_data = {}
        
        try:
            # 内容ID
            try:
                content_id_element = card_element.find_element(By.CSS_SELECTOR, ".dyn-card-opus[dyn-id]")
                dynamic_data["内容ID"] = content_id_element.get_attribute("dyn-id")
            except NoSuchElementException:
                try:
                    content_id_element = card_element.find_element(By.CSS_SELECTOR, "[dyn-id]")
                    dynamic_data["内容ID"] = content_id_element.get_attribute("dyn-id")
                except NoSuchElementException:
                    dynamic_data["内容ID"] = "未知"
            
            # 作者
            try:
                author_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-title__text")
                dynamic_data["作者"] = author_element.text.strip()
            except NoSuchElementException:
                dynamic_data["作者"] = "未知"
            
            # 内容类型 - 通过时间元素判断是否为视频
            try:
                time_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-time")
                time_text = time_element.text.strip()
                if "投稿了视频" in time_text:
                    dynamic_data["内容类型"] = "视频"
                else:
                    dynamic_data["内容类型"] = "动态"
            except NoSuchElementException:
                dynamic_data["内容类型"] = "动态"
            
            # 发布时间
            try:
                time_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-time")
                dynamic_data["发布时间"] = time_element.text.strip()
            except NoSuchElementException:
                dynamic_data["发布时间"] = ""
            
            # 文案内容 - 确保在bili-dyn-content元素内查找
            try:
                # 首先找到bili-dyn-content元素
                dyn_content_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-content")
                # 在bili-dyn-content元素内查找文案内容
                content_element = dyn_content_element.find_element(By.CSS_SELECTOR, ".bili-rich-text__content")
                dynamic_data["文案内容"] = content_element.text.strip()
            except NoSuchElementException:
                dynamic_data["文案内容"] = ""
            
            # 视频描述 - 如果是视频类型，提取bili-dyn-card-video__desc
            if dynamic_data.get("内容类型") == "视频":
                try:
                    video_desc_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-card-video__desc")
                    dynamic_data["视频描述"] = video_desc_element.text.strip()
                except NoSuchElementException:
                    dynamic_data["视频描述"] = ""
            else:
                dynamic_data["视频描述"] = ""
            
            # 互动数据
            interaction_data = self._extract_interaction_data(card_element)
            dynamic_data.update(interaction_data)
            
            # 媒体内容
            media_data = self._extract_media_content(card_element)
            dynamic_data.update(media_data)
            
            # 平台标识
            dynamic_data["平台标识"] = "bilibili"
            
        except Exception as e:
            logger.error(f"提取动态数据时发生错误: {str(e)}")
            dynamic_data = {"错误": str(e)}
            
        return dynamic_data
        
    def getTime(self, card_element) -> str:
        """
        获取动态的发布时间
        
        Args:
            card_element: 动态卡片元素
            
        Returns:
            str: 发布时间文本
        """
        try:
            time_element = card_element.find_element(By.CSS_SELECTOR, ".bili-dyn-time")
            return time_element.text.strip()
        except NoSuchElementException:
            return ""
    
