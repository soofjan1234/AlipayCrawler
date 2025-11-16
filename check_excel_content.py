#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def check_excel_content():
    """检查Excel文件中的图片链接"""
    try:
        # 读取Excel文件
        df = pd.read_excel('/Users/Zhuanz/projects/PythonWS/Alipay/bilibili_data.xlsx')
        
        print(f"Excel文件包含 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        
        # 检查图片链接列
        if '图片链接' in df.columns:
            print("\n图片链接列存在")
            
            # 统计有图片链接的行数
            non_empty_images = df['图片链接'].notna() & (df['图片链接'] != '') & (df['图片链接'] != 'N/A')
            print(f"有图片链接的内容数量: {non_empty_images.sum()}")
            
            # 显示前5个图片链接
            print("\n前5个图片链接:")
            for i in range(min(5, len(df))):
                image_link = df.iloc[i]['图片链接']
                content_id = df.iloc[i]['内容ID']
                print(f"  内容ID {content_id}: {image_link}")
                
                # 检查是否为有效URL
                if isinstance(image_link, str) and image_link.startswith('https://'):
                    print(f"    ✓ URL格式正确")
                else:
                    print(f"    ⚠ URL格式异常或为空")
        else:
            print("❌ 图片链接列不存在")
            
        # 检查视频链接列
        if '视频链接' in df.columns:
            print("\n视频链接列存在")
            non_empty_videos = df['视频链接'].notna() & (df['视频链接'] != '') & (df['视频链接'] != 'N/A')
            print(f"有视频链接的内容数量: {non_empty_videos.sum()}")
        else:
            print("❌ 视频链接列不存在")
            
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")

if __name__ == "__main__":
    check_excel_content()