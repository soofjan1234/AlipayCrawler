#!/usr/bin/env python3
"""
抖音数据导出测试脚本
测试数据导出功能并生成Excel和Word文件
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

from douyin_service.douyin_data_exporter import DouyinDataExporter
from loguru import logger


def test_douyin_data_export():
    """测试抖音数据导出功能"""
    
    logger.info("🚀 开始测试抖音数据导出功能...")
    
    try:
        # 创建数据导出器
        exporter = DouyinDataExporter()
        
        # 解析数据
        logger.info("📊 正在解析抖音数据文件...")
        data = exporter.parse_douyin_data()
        
        if not data:
            logger.warning("⚠️ 未找到有效数据")
            return
        
        logger.info(f"✅ 成功解析 {len(data)} 条数据记录")
        
        # 显示前3条数据的摘要信息
        logger.info("📋 数据摘要（前3条）:")
        for i, item in enumerate(data[:3], 1):
            logger.info(f"  {i}. 发布时间: {item.get('publish_time', '')} | "
                       f"点赞: {item.get('like_count', 0)} | "
                       f"评论: {item.get('comment_count', 0)} | "
                       f"转发: {item.get('share_count', 0)}")
        
        # 导出所有格式
        logger.info("📤 开始导出文件...")
        results = exporter.export_all_formats(data)
        
        # 显示导出结果
        logger.info("✅ 导出完成！生成的文件:")
        for format_type, file_path in results.items():
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            logger.info(f"  📄 {format_type.upper()}: {file_path} ({file_size} bytes)")
        
        logger.success("🎉 抖音数据导出测试完成！")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # 运行测试
    test_douyin_data_export()