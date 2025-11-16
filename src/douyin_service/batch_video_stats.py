#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理抖音视频数据提取程序
遍历2.txt中的所有视频URL，提取每个视频的统计数据并保存到3.txt
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_number(text):
    """解析数字，处理万、千等单位"""
    if not text:
        return 0
    
    # 移除所有非数字字符，保留数字和单位
    text = text.strip()
    
    # 使用正则表达式提取数字和单位
    match = re.search(r'(\d+\.?\d*)([万千wW]?)', text)
    if not match:
        return 0
    
    number = float(match.group(1))
    unit = match.group(2).lower()
    
    # 根据单位转换数字
    if unit in ['w', '万']:
        return int(number * 10000)
    elif unit == '千':
        return int(number * 1000)
    else:
        return int(number)

def extract_video_stats(driver, video_url):
    """提取单个视频的统计数据"""
    try:
        logger.info(f"开始处理视频: {video_url}")
        
        # 访问视频页面
        driver.get(video_url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 等待页面主要内容加载
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 等待一下让页面完全渲染
        time.sleep(3)
        
        # 获取页面源码用于调试
        page_source = driver.page_source
        
        # 查找所有包含 fcEX2ARL class 的 div
        stats_divs = driver.find_elements(By.CSS_SELECTOR, "div.fcEX2ARL")
        
        # 写入调试信息到文件
        with open('/Users/Zhuanz/projects/PythonWS/Alipay/3.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"\n=== 视频URL: {video_url} ===\n")
            debug_file.write(f"找到 {len(stats_divs)} 个 fcEX2ARL div:\n")
            for i, div in enumerate(stats_divs):
                try:
                    div_html = div.get_attribute('outerHTML')
                    debug_file.write(f"Div {i}: {div_html}\n")
                except Exception as e:
                    debug_file.write(f"Div {i}: 获取HTML失败 - {str(e)}\n")
        
        # 初始化统计数据
        stats = {
            'likes': 0,
            'comments': 0,
            'collects': 0,
            'shares': 0,
            'publish_time': ''
        }
        
        # 遍历所有找到的 div，根据位置假设提取数据
        # 假设顺序是：点赞、评论、收藏、转发
        for i, div in enumerate(stats_divs):
            try:
                span = div.find_element(By.TAG_NAME, "span")
                text = span.text
                number = parse_number(text)
                
                if i == 0:  # 点赞
                    stats['likes'] = number
                elif i == 1:  # 评论
                    stats['comments'] = number
                elif i == 2:  # 收藏
                    stats['collects'] = number
                elif i == 3:  # 转发
                    stats['shares'] = number
                    
            except Exception as e:
                logger.warning(f"提取第{i}个div数据失败: {str(e)}")
                continue
        
        # 提取发布时间
        try:
            publish_time_element = driver.find_element(By.CSS_SELECTOR, "span.MsN3XzkF[data-e2e='detail-video-publish-time']")
            stats['publish_time'] = publish_time_element.text
        except Exception as e:
            logger.warning(f"提取发布时间失败: {str(e)}")
            stats['publish_time'] = '未找到发布时间'
        
        logger.info(f"视频数据提取完成: 点赞={stats['likes']}, 评论={stats['comments']}, 收藏={stats['collects']}, 转发={stats['shares']}, 发布时间={stats['publish_time']}")
        
        return stats
        
    except Exception as e:
        logger.error(f"提取视频统计数据失败: {str(e)}")
        return {
            'likes': 0,
            'comments': 0,
            'collects': 0,
            'shares': 0,
            'publish_time': '提取失败'
        }

def read_video_urls(file_path):
    """从文件中读取视频URL列表"""
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # 使用正则表达式提取抖音视频URL
        url_pattern = r'https://www\.douyin\.com/video/\d+'
        urls = re.findall(url_pattern, content)
        
        logger.info(f"从文件中读取到 {len(urls)} 个视频URL")
        return urls
        
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        return []

def main():
    """主函数"""
    # 清空3.txt文件
    with open('/Users/Zhuanz/projects/PythonWS/Alipay/3.txt', 'w', encoding='utf-8') as f:
        f.write("")
    
    # 读取视频URL列表
    video_urls = read_video_urls('/Users/Zhuanz/projects/PythonWS/Alipay/2.txt')
    
    if not video_urls:
        logger.error("没有找到有效的视频URL")
        return
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-data-dir=/Users/Zhuanz/projects/PythonWS/Alipay/chrome_user_data')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 设置ChromeDriver服务
    service = Service('/usr/local/bin/chromedriver')
    
    # 启动浏览器
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 处理每个视频
        all_results = []
        for i, url in enumerate(video_urls, 1):
            logger.info(f"处理第 {i}/{len(video_urls)} 个视频")
            
            # 提取视频统计数据
            stats = extract_video_stats(driver, url)
            
            # 保存结果
            result = f"""视频URL: {url}
点赞数: {stats['likes']}
评论数: {stats['comments']}
收藏数: {stats['collects']}
转发数: {stats['shares']}
发布时间: {stats['publish_time']}
"""
            all_results.append(result)
            
            # 将结果追加到3.txt文件
            with open('/Users/Zhuanz/projects/PythonWS/Alipay/3.txt', 'a', encoding='utf-8') as f:
                f.write(result)
                f.write("-" * 50 + "\n")
            
            # 添加延迟避免被限制
            time.sleep(2)
        
        logger.info(f"批量处理完成，共处理 {len(video_urls)} 个视频")
        
        # 在控制台输出汇总信息
        print(f"\n=== 批量处理完成 ===")
        print(f"共处理 {len(video_urls)} 个视频")
        print(f"结果已保存到: /Users/Zhuanz/projects/PythonWS/Alipay/3.txt")
        
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()