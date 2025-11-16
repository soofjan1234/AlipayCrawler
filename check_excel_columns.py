#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def check_excel_columns():
    """检查Excel文件的列"""
    try:
        df = pd.read_excel('bilibili_data.xlsx')
        print("Excel文件列名:")
        print(df.columns.tolist())
        print(f"\n数据行数: {len(df)}")
        
        # 检查图片链接列
        if '图片链接' in df.columns:
            print(f"\n图片链接列存在")
            non_empty_images = df['图片链接'].notna() & (df['图片链接'] != '') & (df['图片链接'] != 'N/A')
            print(f"有图片链接的内容数量: {non_empty_images.sum()}")
        else:
            print("\n图片链接列不存在")
        
        # 检查视频链接列
        if '视频链接' in df.columns:
            print(f"视频链接列存在")
            non_empty_videos = df['视频链接'].notna() & (df['视频链接'] != '') & (df['视频链接'] != 'N/A')
            print(f"有视频链接的内容数量: {non_empty_videos.sum()}")
        else:
            print("视频链接列不存在")
            
        return True
    except Exception as e:
        print(f"检查Excel文件时出错: {e}")
        return False

if __name__ == "__main__":
    check_excel_columns()