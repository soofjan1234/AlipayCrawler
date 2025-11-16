#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/Zhuanz/projects/PythonWS/Alipay')

from export_bilibili_data import BilibiliDataExporter

def test_image_link_extraction():
    """测试图片链接提取功能"""
    exporter = BilibiliDataExporter('/Users/Zhuanz/projects/PythonWS/Alipay/1.txt')
    data = exporter.parse_txt_data()
    
    print(f"总共解析了 {len(data)} 条数据")
    print("\n检查前5条数据的图片链接:")
    
    for i, item in enumerate(data[:5]):
        print(f"\n内容 {i+1}:")
        print(f"  内容ID: {item.get('content_id', 'N/A')}")
        print(f"  发布时间: {item.get('publish_time', 'N/A')}")
        print(f"  图片链接: {item.get('image_link', 'N/A')}")
        print(f"  视频链接: {item.get('video_link', 'N/A')}")
        
        # 检查图片链接是否为有效的URL
        image_link = item.get('image_link', '')
        if image_link and image_link.startswith('https://'):
            print(f"  ✓ 图片链接格式正确")
        elif image_link:
            print(f"  ⚠ 图片链接格式异常: {image_link}")
        else:
            print(f"  - 无图片链接")

if __name__ == "__main__":
    test_image_link_extraction()