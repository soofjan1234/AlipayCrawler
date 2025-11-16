# 支付宝社交媒体内容爬取项目 - MVP文档

## 项目概述

### 目标
爬取支付宝在B站和抖音平台从5月1日到11月1日（六个月）的动态和发布内容，包括：
- 文本内容
- 图片链接
- 转发数量
- 点赞数量  
- 评论数量

### 技术方案
使用Selenium模拟浏览器操作进行数据爬取

---

## 第一阶段：B站动态爬取 MVP

### 1.1 目标页面
- URL: https://space.bilibili.com/420831218/dynamic
- 目标用户：支付宝官方账号

### 1.2 数据结构设计

#### 动态信息
```python
{
    "dynamic_id": "动态ID",
    "publish_time": "发布时间",
    "content": "文本内容",
    "images": [
        {
            "url": "图片链接",
            "description": "图片描述"
        }
    ],
    "stats": {
        "repost": "转发数",
        "like": "点赞数", 
        "comment": "评论数"
    },
    "dynamic_type": "动态类型"  # 图文、视频、转发等
}
```

### 1.3 功能模块

#### 1.3.1 页面访问与登录处理
- [x] 访问B站用户动态页面
- [x] 处理可能的登录要求（如需要）
- [x] 等待页面完全加载

#### 1.3.2 动态列表获取
- [x] 滚动加载更多动态
- [x] 提取动态卡片元素
- [x] 处理时间筛选（5.1-11.1）

#### 1.3.3 单条动态数据提取
- [x] 提取发布时间
- [x] 提取文本内容
- [x] 提取图片链接
- [x] 提取互动数据（转发、点赞、评论）

#### 1.3.4 数据存储
- [x] JSON格式保存
- [x] 按日期分组存储
- [x] 异常处理和重试机制

### 1.4 技术实现要点

#### 页面元素定位策略
```python
# B站动态卡片选择器
DYNAMIC_CARD = ".card-box"
PUBLISH_TIME = ".pub-time"
CONTENT_TEXT = ".text-con"
IMAGES = ".img-box img"
LIKE_COUNT = ".like-info"
COMMENT_COUNT = ".comment-info"
REPOST_COUNT = ".repost-info"
```

#### 时间筛选逻辑
- 解析动态发布时间
- 筛选5月1日至11月1日范围内的动态
- 处理相对时间格式（如"3天前"）

#### 反爬虫应对
- 设置随机User-Agent
- 控制滚动和点击间隔
- 处理验证码（如出现）

### 1.5 预期输出
```
bilibili_data/
├── 2024-05/
│   ├── 05-01.json
│   ├── 05-02.json
│   └── ...
├── 2024-06/
│   └── ...
└── summary.json
```

---

## 第二阶段：抖音内容爬取 MVP

### 2.1 目标页面
- URL: https://www.douyin.com/user/MS4wLjABAAAA4rbc75Wk1sycUT5ZT_bMSq31wqxeZp7PLY3ZzCenbIY?from_tab_name=main
- 目标用户：支付宝官方账号

### 2.2 数据结构设计

#### 视频信息
```python
{
    "video_id": "视频ID",
    "publish_time": "发布时间",
    "description": "视频描述",
    "cover_image": "封面图片链接",
    "video_url": "视频链接",
    "stats": {
        "like": "点赞数",
        "comment": "评论数",
        "share": "分享数",
        "collect": "收藏数"
    },
    "hashtags": ["话题标签"],
    "music_info": {
        "title": "背景音乐标题",
        "author": "音乐作者"
    }
}
```

### 2.3 功能模块

#### 2.3.1 页面访问与渲染
- [x] 访问抖音用户主页
- [x] 等待JavaScript渲染完成
- [x] 处理可能的登录弹窗

#### 2.3.2 视频列表获取
- [x] 滚动加载更多视频
- [x] 提取视频卡片元素
- [x] 时间筛选（5.1-11.1）

#### 2.3.3 单个视频数据提取
- [x] 提取视频描述
- [x] 提取发布时间
- [x] 提取封面图片
- [x] 提取互动数据
- [x] 提取话题标签

#### 2.3.4 数据存储
- [x] JSON格式保存
- [x] 按日期分组
- [x] 异常处理

### 2.4 技术实现要点

#### 页面元素定位策略
```python
# 抖音视频卡片选择器
VIDEO_CARD = "[data-e2e='user-post-list'] > div"
PUBLISH_TIME = "[data-e2e='browse-video-desc']"
DESCRIPTION = "[data-e2e='browse-video-desc']"
COVER_IMAGE = "img"
LIKE_COUNT = "[data-e2e='video-like-count']"
COMMENT_COUNT = "[data-e2e='video-comment-count']"
SHARE_COUNT = "[data-e2e='video-share-count']"
```

#### 抖音特殊处理
- 处理动态加载内容
- 应对更严格的反爬虫机制
- 处理视频播放和暂停

### 2.5 预期输出
```
douyin_data/
├── 2024-05/
│   ├── 05-01.json
│   ├── 05-02.json
│   └── ...
├── 2024-06/
│   └── ...
└── summary.json
```

---

## 第三阶段：数据整合与分析

### 3.1 数据汇总
- [x] 合并B站和抖音数据
- [x] 统一数据格式
- [x] 生成汇总报告

### 3.2 数据分析
- [x] 发布频率统计
- [x] 互动数据分析
- [x] 内容类型分布
- [x] 热门内容识别

### 3.3 可视化展示
- [x] 时间趋势图表
- [x] 互动数据对比
- [x] 内容云图

---

## 技术架构

### 依赖库
```python
selenium==4.15.0
webdriver-manager==4.0.1
beautifulsoup4==4.12.2
requests==2.31.0
pandas==2.1.3
matplotlib==3.8.2
```

### 项目结构
```
Alipay/
├── src/
│   ├── __init__.py
│   ├── bilibili_crawler.py    # B站爬虫
│   ├── douyin_crawler.py     # 抖音爬虫
│   ├── data_processor.py     # 数据处理
│   └── utils.py             # 工具函数
├── data/
│   ├── bilibili_data/
│   └── douyin_data/
├── output/
│   ├── summary.json
│   └── analysis_report.html
├── config/
│   └── settings.py          # 配置文件
├── requirements.txt
└── README.md
```

---

