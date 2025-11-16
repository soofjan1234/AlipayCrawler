"""
B站批量内容提取模块

该模块提供了批量提取B站用户动态内容的功能，
支持调用extract_article模块进行单个内容的提取。
"""

import logging
import time
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

from src.bilibili_service.extract_article import BilibiliArticleExtractor
from datetime import datetime, timedelta
import re
from src.bilibili_service.data_exporter import DataExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliMultiExtractor:
    """B站批量内容提取器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化批量提取器
        
        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.extractor = None
        
    def __enter__(self):
        """上下文管理器入口"""
        self.extractor = BilibiliArticleExtractor(headless=self.headless)
        self.extractor.__enter__()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.extractor:
            self.extractor.__exit__(exc_type, exc_val, exc_tb)
            
    def _parse_time_text(self, time_text: str) -> Optional[datetime]:
        """
        解析时间文本为datetime对象
        
        Args:
            time_text: 时间文本（如："1天前"、"2天前"、"3天前"、"08月19日"等）
            
        Returns:
            datetime: 解析后的datetime对象，失败时返回None
        """
        if not time_text:
            return None
            
        try:
            # 格式1: 相对时间 "x天前"
            match = re.match(r'(\d{1,2})天前', time_text)
            if match:
                days_ago = int(match.group(1))
                current_date = datetime.now()
                return current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)
            
            # 格式2: 绝对时间 "MM月DD日"
            match = re.match(r'(\d{1,2})月(\d{1,2})日', time_text)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))
                current_year = datetime.now().year
                return datetime(current_year, month, day)
            
            logger.warning(f"无法解析时间格式: {time_text}")
            return None
            
        except Exception as e:
            logger.error(f"解析时间时出错: {time_text}, 错误: {str(e)}")
            return None
            
    def extract_first_content(self, user_url: str) -> Optional[Dict[str, Any]]:
        """
        提取用户的第一个内容（MVP第一个动作）
        
        Args:
            user_url: B站用户动态页面URL
            
        Returns:
            Dict: 第一个内容的详细数据，失败时返回None
        """
        logger.info(f"开始提取用户第一个内容: {user_url}")
        
        if not self.extractor:
            logger.error("提取器未初始化")
            return None
            
        try:
            # 访问用户动态页面
            self.extractor.driver.get(user_url)
            logger.info("已访问用户动态页面")
            
            # 等待登录
            if not self.extractor._wait_for_login():
                logger.error("登录失败或超时")
                return None
                
            # 等待页面加载
            time.sleep(3)
            
            # 查找第一个动态卡片
            try:
                wait = WebDriverWait(self.extractor.driver, 10)
                first_card = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".bili-dyn-item__main"))
                )
                logger.info("找到第一个动态卡片")
            except TimeoutException:
                logger.error("未找到动态卡片，页面可能未加载完成")
                return None
                
            # 提取第一个动态的数据
            first_content_data = self.extractor._extract_single_dynamic(first_card)
            
            if first_content_data and "错误" not in first_content_data:
                logger.info("✅ 成功提取第一个内容")
                logger.info(f"内容ID: {first_content_data.get('内容ID', '未知')}")
                logger.info(f"作者: {first_content_data.get('作者', '未知')}")
                logger.info(f"内容类型: {first_content_data.get('内容类型', '未知')}")
                return first_content_data
            else:
                logger.error("提取第一个内容失败")
                return None
                
        except Exception as e:
            logger.error(f"提取第一个内容时发生错误: {str(e)}")
            return None
            
    def extract_contents_by_date_range(self, user_url: str, start_time_str: str, end_time_str: str) -> List[Dict[str, Any]]:
        """
        按指定时间范围提取用户动态内容（倒序：从结束日期到开始日期）
        
        Args:
            user_url: B站用户动态页面URL
            start_time_str: 开始时间字符串（如："08月19日"）
            end_time_str: 结束时间字符串（如："09月25日"）
            
        Returns:
            List[Dict]: 提取的内容数据列表（时间范围内的所有内容）
        """
        logger.info(f"开始按时间范围提取用户动态内容")
        logger.info(f"时间范围: {start_time_str} 到 {end_time_str}")
        
        if not self.extractor:
            logger.error("提取器未初始化")
            return []
            
        try:
            # 访问用户动态页面
            self.extractor.driver.get(user_url)
            logger.info("已访问用户动态页面")
            
            # 等待登录
            if not self.extractor._wait_for_login():
                logger.error("登录失败或超时")
                return []
                
            # 等待页面加载
            time.sleep(3)
            
            contents_data = []
            extracted_ids = set()  # 记录已提取的内容ID，避免重复
            scroll_count = 0
            max_scrolls = 50  # 增加最大滚动次数，确保能提取时间范围内的所有内容
            total_cards_seen = 0  # 记录总共看到的卡片数量（不管是否提取）
            total_scrolled_height = 0  # 累计滚动高度
            
            # 解析时间范围
            start_date = self._parse_time_text(start_time_str)
            end_date = self._parse_time_text(end_time_str)
            
            if not start_date or not end_date:
                logger.error("时间范围解析失败")
                return []
            
            logger.info(f"解析后的时间范围: {start_date} 到 {end_date}")
            
            while scroll_count < max_scrolls:
                logger.info(f"第 {scroll_count + 1} 轮提取，当前已提取 {len(contents_data)} 个内容")
                
                # 查找当前页面的所有动态卡片
                try:
                    wait = WebDriverWait(self.extractor.driver, 10)
                    cards = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".bili-dyn-item__main"))
                    )
                    logger.info(f"当前页面找到 {len(cards)} 个动态卡片")
                    
                    # 计算本轮所有卡片的总高度
                    current_round_height = 0
                    for card in cards:
                        card_height = card.size["height"]
                        current_round_height += card_height
                        total_cards_seen += 1
                    
                    logger.info(f"本轮 {len(cards)} 个卡片总高度: {current_round_height} 像素")
                    logger.info(f"累计已看到 {total_cards_seen} 个卡片")
                    
                except TimeoutException:
                    logger.warning("未找到动态卡片，尝试滚动加载更多内容")
                    break
                
                # 遍历卡片，检查时间范围
                new_contents_this_round = 0
                reached_start_time = False
                
                for i, card in enumerate(cards):
                    try:
                        # 获取内容ID（使用与extract_article.py相同的逻辑）
                        try:
                            content_id_elem = card.find_element(By.CSS_SELECTOR, ".dyn-card-opus[dyn-id]")
                            content_id = content_id_elem.get_attribute("dyn-id")
                        except NoSuchElementException:
                            try:
                                content_id_elem = card.find_element(By.CSS_SELECTOR, "[dyn-id]")
                                content_id = content_id_elem.get_attribute("dyn-id")
                            except NoSuchElementException:
                                content_id = f"card_{i}"
                        
                        # 跳过已提取的内容
                        if content_id in extracted_ids:
                            continue
                            
                        # 获取发布时间
                        publish_time_text = self.extractor.getTime(card)
                        
                        if not publish_time_text:
                            logger.debug(f"卡片 {content_id} 未获取到发布时间，跳过")
                            continue
                            
                        logger.info(f"卡片 {content_id} 发布时间: {publish_time_text}")
                        
                        # 解析发布时间
                        publish_date = self._parse_time_text(publish_time_text)
                        
                        if not publish_date:
                            logger.debug(f"无法解析发布时间: {publish_time_text}")
                            continue
                        
                        # 检查是否在时间范围内
                        if start_date <= publish_date <= end_date:
                            logger.info(f"✅ 卡片 {content_id} 在时间范围内，开始提取内容")
                            
                            # 获取卡片高度
                            card_height = card.size["height"]
                            logger.info(f"卡片高度: {card_height} 像素")
                            
                            # 提取卡片数据
                            content_data = self.extractor._extract_single_dynamic(card)
                            
                            if content_data and "错误" not in content_data:
                                # 添加额外信息
                                content_data["卡片高度"] = f"{card_height}px"
                                content_data["提取轮次"] = scroll_count + 1
                                content_data["发布时间_原始"] = publish_time_text
                                content_data["发布时间_解析"] = publish_date.strftime("%Y-%m-%d")
                                contents_data.append(content_data)
                                extracted_ids.add(content_id)
                                new_contents_this_round += 1
                                logger.info(f"✅ 成功提取内容，当前总数: {len(contents_data)}")
                        elif publish_date < start_date:
                            # 如果发布时间早于开始时间，说明已经到达开始时间了
                            logger.info(f"✅ 到达开始时间 {start_time_str}，停止提取")
                            reached_start_time = True
                            break
                        else:
                            # 发布时间晚于结束时间，继续滚动
                            logger.debug(f"卡片 {content_id} 发布时间 {publish_time_text} 晚于结束时间 {end_time_str}，继续滚动")
                            
                    except Exception as e:
                        logger.warning(f"处理单个卡片时出错: {str(e)}")
                        continue
                
                logger.info(f"第 {scroll_count + 1} 轮提取完成，新增 {new_contents_this_round} 个内容")
                
                # 如果到达开始时间或本轮没有新内容，停止提取
                if reached_start_time or new_contents_this_round == 0:
                    if reached_start_time:
                        logger.info("已到达开始时间，停止提取")
                    else:
                        logger.info("本轮未提取到新内容，可能已到达页面底部")
                    break
                
                # 向下滑动加载更多内容
                # 使用本轮所有卡片的总高度作为滚动距离，并增加额外距离确保加载新内容
                scroll_distance = current_round_height + 500 if current_round_height > 0 else 1500
                total_scrolled_height += scroll_distance
                
                logger.info(f"向下滑动 {scroll_distance} 像素加载更多内容")
                logger.info(f"累计滚动高度: {total_scrolled_height} 像素")
                
                # 使用JavaScript执行平滑滚动
                scroll_script = f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});"
                self.extractor.driver.execute_script(scroll_script)
                
                # 等待新内容加载
                time.sleep(10)  # 增加等待时间，确保新内容完全加载
                
                scroll_count += 1
            
            logger.info(f"按时间范围提取完成，共提取 {len(contents_data)} 个内容")
            logger.info(f"时间范围: {start_time_str} 到 {end_time_str}")
            logger.info(f"总共进行了 {scroll_count} 轮提取")
            
            # 将提取结果汇总到1.txt文件
            try:
                with open('/Users/Zhuanz/projects/PythonWS/Alipay/1.txt', 'w', encoding='utf-8') as f:
                    f.write("B站动态内容按时间范围提取结果汇总\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"提取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"时间范围: {start_time_str} 到 {end_time_str}\n")
                    f.write(f"实际提取: {len(contents_data)} 个内容\n")
                    f.write(f"提取轮次: {scroll_count} 轮\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, content in enumerate(contents_data, 1):
                        f.write(f"内容 {i}:\n")
                        f.write(f"  内容ID: {content.get('内容ID', '未知')}\n")
                        f.write(f"  作者: {content.get('作者', '未知')}\n")
                        f.write(f"  发布时间: {content.get('发布时间', '未知')}\n")
                        f.write(f"  发布时间_原始: {content.get('发布时间_原始', '未知')}\n")
                        f.write(f"  发布时间_解析: {content.get('发布时间_解析', '未知')}\n")
                        f.write(f"  文案内容: {content.get('文案内容', '未知')}\n")
                        f.write(f"  内容类型: {content.get('内容类型', '未知')}\n")
                        if content.get('内容类型') == '视频':
                            f.write(f"  视频描述: {content.get('视频描述', '未知')}\n")
                        f.write(f"  点赞数: {content.get('点赞数', '0')}\n")
                        f.write(f"  评论数: {content.get('评论数', '0')}\n")
                        f.write(f"  转发数: {content.get('转发数', '0')}\n")
                        f.write(f"  图片链接: {content.get('图片链接', '无')}\n")
                        f.write(f"  视频链接: {content.get('视频链接', '无')}\n")
                        f.write(f"  卡片高度: {content.get('卡片高度', '未知')}\n")
                        f.write(f"  提取轮次: {content.get('提取轮次', '未知')}\n")
                        f.write("-" * 40 + "\n")
                    
                    f.write(f"\n总计提取 {len(contents_data)} 个动态内容\n")
                
                logger.info("✅ 提取结果已保存到 1.txt 文件")
                
            except Exception as e:
                logger.error(f"保存结果到文件时出错: {str(e)}")
                
            return contents_data  # 返回时间范围内的所有内容
            
        except Exception as e:
            logger.error(f"按时间范围提取内容时发生错误: {str(e)}")
            return []

    def extract_multiple_contents(self, user_url: str, target_count: int = 20) -> List[Dict[str, Any]]:
        """
        循环增量提取用户动态内容，直到达到目标数量
        
        Args:
            user_url: B站用户动态页面URL
            target_count: 目标提取数量（默认20个）
            
        Returns:
            List[Dict]: 提取的内容数据列表
        """
        logger.info(f"开始循环增量提取用户动态内容，目标数量: {target_count}")
        
        if not self.extractor:
            logger.error("提取器未初始化")
            return []
            
        try:
            # 访问用户动态页面
            self.extractor.driver.get(user_url)
            logger.info("已访问用户动态页面")
            
            # 等待登录
            if not self.extractor._wait_for_login():
                logger.error("登录失败或超时")
                return []
                
            # 等待页面加载
            time.sleep(3)
            
            contents_data = []
            extracted_ids = set()  # 记录已提取的内容ID，避免重复
            scroll_count = 0
            max_scrolls = 10  # 最大滚动次数，防止无限循环
            
            while len(contents_data) < target_count and scroll_count < max_scrolls:
                logger.info(f"第 {scroll_count + 1} 轮提取，当前已提取 {len(contents_data)}/{target_count} 个")
                
                # 查找当前页面的所有动态卡片
                try:
                    wait = WebDriverWait(self.extractor.driver, 10)
                    cards = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".bili-dyn-item__main"))
                    )
                    logger.info(f"当前页面找到 {len(cards)} 个动态卡片")
                except TimeoutException:
                    logger.warning("未找到动态卡片，尝试滚动加载更多内容")
                    break
                
                # 提取当前页面的新内容
                new_contents_this_round = 0
                for i, card in enumerate(cards):
                    try:
                        # 获取内容ID（使用与extract_article.py相同的逻辑）
                        try:
                            content_id_elem = card.find_element(By.CSS_SELECTOR, ".dyn-card-opus[dyn-id]")
                            content_id = content_id_elem.get_attribute("dyn-id")
                        except NoSuchElementException:
                            try:
                                content_id_elem = card.find_element(By.CSS_SELECTOR, "[dyn-id]")
                                content_id = content_id_elem.get_attribute("dyn-id")
                            except NoSuchElementException:
                                content_id = f"card_{i}"
                        
                        # 跳过已提取的内容
                        if content_id in extracted_ids:
                            continue
                            
                        logger.info(f"正在提取新内容 ID: {content_id}")
                        
                        # 获取卡片高度
                        card_height = card.size["height"]
                        logger.info(f"卡片高度: {card_height} 像素")
                        
                        # 提取卡片数据
                        content_data = self.extractor._extract_single_dynamic(card)
                        
                        if content_data and "错误" not in content_data:
                            # 添加卡片高度信息
                            content_data["卡片高度"] = f"{card_height}px"
                            content_data["提取轮次"] = scroll_count + 1
                            contents_data.append(content_data)
                            extracted_ids.add(content_id)
                            new_contents_this_round += 1
                            logger.info(f"✅ 成功提取内容，当前总数: {len(contents_data)}")
                            
                            # 如果达到目标数量，提前退出
                            if len(contents_data) >= target_count:
                                logger.info(f"已达到目标数量 {target_count}，停止提取")
                                break
                                
                    except Exception as e:
                        logger.warning(f"提取单个卡片时出错: {str(e)}")
                        continue
                
                logger.info(f"第 {scroll_count + 1} 轮提取完成，新增 {new_contents_this_round} 个内容")
                
                # 如果本轮没有新内容，说明已经到底了
                if new_contents_this_round == 0:
                    logger.info("本轮未提取到新内容，可能已到达页面底部")
                    break
                
                # 如果还没达到目标数量，向下滑动加载更多内容
                if len(contents_data) < target_count:
                    # 计算本轮所有卡片的总高度
                    current_round_height = 0
                    for card in cards:
                        current_round_height += card.size["height"]
                    
                    # 使用本轮所有卡片的总高度作为滚动距离
                    scroll_distance = current_round_height if current_round_height > 0 else 1000
                    
                    logger.info(f"向下滑动 {scroll_distance} 像素加载更多内容")
                    
                    # 使用JavaScript执行平滑滚动
                    scroll_script = f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});"
                    self.extractor.driver.execute_script(scroll_script)
                    
                    # 等待新内容加载
                    time.sleep(5)
                
                scroll_count += 1
            
            logger.info(f"循环提取完成，共提取 {len(contents_data)} 个内容")
            logger.info(f"总共进行了 {scroll_count} 轮提取")
            
            
            # 将提取结果汇总到1.txt文件
            try:
                with open('/Users/Zhuanz/projects/PythonWS/Alipay/1.txt', 'w', encoding='utf-8') as f:
                    f.write("B站动态内容提取结果汇总\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"提取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"目标数量: {target_count}\n")
                    f.write(f"实际提取: {len(contents_data)} 个内容\n")
                    f.write(f"提取轮次: {scroll_count} 轮\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, content in enumerate(contents_data, 1):
                        f.write(f"内容 {i}:\n")
                        f.write(f"  内容ID: {content.get('内容ID', '未知')}\n")
                        f.write(f"  作者: {content.get('作者', '未知')}\n")
                        f.write(f"  发布时间: {content.get('发布时间', '未知')}\n")
                        f.write(f"  文案内容: {content.get('文案内容', '未知')}\n")
                        f.write(f"  内容类型: {content.get('内容类型', '未知')}\n")
                        f.write(f"  点赞数: {content.get('点赞数', '0')}\n")
                        f.write(f"  评论数: {content.get('评论数', '0')}\n")
                        f.write(f"  转发数: {content.get('转发数', '0')}\n")
                        f.write(f"  卡片高度: {content.get('卡片高度', '未知')}\n")
                        f.write(f"  提取轮次: {content.get('提取轮次', '未知')}\n")
                    
                        
                        f.write("-" * 40 + "\n")
                    
                    f.write(f"\n总计提取 {len(contents_data)} 个动态内容\n")
                
                logger.info("✅ 提取结果已保存到 1.txt 文件")
                
            except Exception as e:
                logger.error(f"保存结果到文件时出错: {str(e)}")
                
            return contents_data[:target_count]  # 返回目标数量的内容
            
        except Exception as e:
            logger.error(f"循环增量提取内容时发生错误: {str(e)}")
            return []


def test_first_content_extraction():
    """测试第一个内容提取功能"""
    test_url = "https://space.bilibili.com/420831218/dynamic"  # B站动态首页
    
    with BilibiliMultiExtractor(headless=False) as extractor:
        results = extractor.extract_multiple_contents(test_url)
        


if __name__ == "__main__":
    start_time_str = "05月01日"  # 开始时间
    end_time_str =  "11月01日"   # 结束时间
    
    with BilibiliMultiExtractor() as extractor:
        contents = extractor.extract_contents_by_date_range(
            user_url="https://space.bilibili.com/420831218/dynamic",
            start_time_str=start_time_str,
            end_time_str=end_time_str
        )
        print(f"按时间范围 {start_time_str} 到 {end_time_str} 提取了 {len(contents)} 个内容")