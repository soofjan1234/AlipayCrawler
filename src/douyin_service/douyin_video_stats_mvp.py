#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频数据提取MVP
提取视频的点赞数、评论数、转发数
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def setup_driver():
    """设置Chrome浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 使用用户数据目录以保持登录状态
    chrome_options.add_argument('--user-data-dir=/Users/Zhuanz/projects/PythonWS/Alipay/chrome_user_data')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_video_stats(driver, video_url):
    """
    提取视频的点赞数、评论数、转发数
    
    根据b.txt的新规则：
    - 查找div[data-e2e="detail-video-info"]元素
    - 找到该元素的第三个子元素div (x)
    - x的子元素的子元素总共有四个：点赞、评论、收藏、转发
    - 数量都在span里面
    """
    try:
        print(f"正在访问视频: {video_url}")
        driver.get(video_url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 调试：打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        # 调试：检查页面源码中是否包含目标元素
        page_source = driver.page_source
        if 'video-share-icon-container' in page_source:
            print("页面源码中包含video-share-icon-container")
        else:
            print("页面源码中不包含video-share-icon-container")
            print("页面源码前500字符:", page_source[:500])
        
        # 直接查找所有包含fcEX2ARL class的div元素
        debug_info = []
        try:
            # 查找所有包含fcEX2ARL class的div
            all_fc_divs = driver.find_elements(By.CSS_SELECTOR, "div.fcEX2ARL")
            debug_info.append(f"找到 {len(all_fc_divs)} 个包含fcEX2ARL class的div")
            
            # 初始化所有数据为0
            likes = "0"
            comments = "0" 
            favorites = "0"
            shares = "0"
            
            # 调试：将所有找到的div内容写入3.txt
            with open('/Users/Zhuanz/projects/PythonWS/Alipay/3.txt', 'w', encoding='utf-8') as debug_file:
                for i, div in enumerate(all_fc_divs):
                    div_html = div.get_attribute('outerHTML')
                    debug_file.write(f"第{i+1}个fcEX2ARL div内容: {div_html}\n\n")
            
            # 遍历所有fcEX2ARL div，根据位置和内容判断是哪种数据
            for i, div in enumerate(all_fc_divs):
                try:
                    # 查找span元素
                    span = div.find_element(By.TAG_NAME, "span")
                    span_text = span.text.strip()
                    
                    # 根据div在页面中的位置或其他特征来判断数据类型
                    # 通常顺序是：点赞、评论、收藏、转发
                    if i == 0:  # 假设第一个是点赞
                        likes = span_text
                        debug_info.append(f"点赞数: {likes}")
                    elif i == 1:  # 假设第二个是评论
                        comments = span_text
                        debug_info.append(f"评论数: {comments}")
                    elif i == 2:  # 假设第三个是收藏
                        favorites = span_text
                        debug_info.append(f"收藏数: {favorites}")
                    elif i == 3:  # 假设第四个是转发
                        shares = span_text
                        debug_info.append(f"转发数: {shares}")
                        
                except Exception as e:
                    debug_info.append(f"第{i+1}个fcEX2ARL div中未找到span元素: {e}")
                    
        except Exception as e:
            debug_info.append(f"查找fcEX2ARL div失败: {e}")
        
        # 写入所有调试信息
        with open('/Users/Zhuanz/projects/PythonWS/Alipay/3.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write('\n'.join(debug_info))
            
        stats = {
            'likes': parse_number(likes),
            'comments': parse_number(comments),
            'favorites': parse_number(favorites),
            'shares': parse_number(shares),
            'video_url': video_url
        }
        
        return stats
        
    except Exception as e:
        print(f"提取视频数据时出错: {e}")
        return None


def parse_number(text):
    """解析数字文本，处理万、千等单位"""
    if not text:
        return 0
    
    # 移除非数字字符，保留数字和万、千等单位
    text = text.strip()
    
    # 使用正则表达式提取数字
    match = re.search(r'(\d+\.?\d*)([万千wWkK]?)', text)
    if match:
        number = float(match.group(1))
        unit = match.group(2).lower()
        
        if unit in ['万', 'w']:
            return int(number * 10000)
        elif unit in ['千', 'k']:
            return int(number * 1000)
        else:
            return int(number)
    
    return 0


def main():
    """主函数"""
    video_url = "https://www.douyin.com/video/7562360638024207674"
    
    print("抖音视频数据提取MVP启动")
    print(f"目标视频: {video_url}")
    
    # 设置浏览器驱动
    driver = setup_driver()
    
    try:
        # 提取视频数据
        stats = extract_video_stats(driver, video_url)
        
        if stats:
            print("\n=== 提取结果 ===")
            print(f"视频URL: {stats['video_url']}")
            print(f"点赞数: {stats['likes']:,}")
            print(f"评论数: {stats['comments']:,}")
            print(f"收藏数: {stats['favorites']:,}")
            print(f"转发数: {stats['shares']:,}")
            
            # 保存结果到文件
            with open('/Users/Zhuanz/projects/PythonWS/Alipay/video_stats.txt', 'w', encoding='utf-8') as f:
                f.write(f"视频URL: {stats['video_url']}\n")
                f.write(f"点赞数: {stats['likes']}\n")
                f.write(f"评论数: {stats['comments']}\n")
                f.write(f"收藏数: {stats['favorites']}\n")
                f.write(f"转发数: {stats['shares']}\n")
            
            print("\n结果已保存到 video_stats.txt")
        else:
            print("提取失败")
            
    except Exception as e:
        print(f"程序执行出错: {e}")
        
    finally:
        driver.quit()
        print("程序结束")


if __name__ == "__main__":
    main()