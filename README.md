# 跨境电商用户行为与选品趋势分析

基于天池百万级用户行为数据集，使用 Python 完成电商用户转化漏斗分析、RFM 用户分层，并结合 Google Trends 跨国搜索趋势数据输出选品建议。

## 项目结构

```
ecommerce-analysis/
├── src/
│   ├── utils.py                    # 公共工具（数据加载、图表样式）
│   ├── generate_sample_data.py     # 生成模拟数据（无需下载数据集即可运行）
│   ├── 01_data_exploration.py      # 数据探索与 PV/UV 趋势
│   ├── 02_funnel_analysis.py       # 转化漏斗分析
│   ├── 03_rfm_analysis.py          # RFM 用户分层
│   └── 04_cross_border_trends.py   # 跨境选品趋势（Google Trends）
├── data/                           # 数据文件（不入 Git）
├── output/charts/                  # 输出图表（不入 Git）
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

**方式一：使用模拟数据（快速体验）**

```bash
python src/generate_sample_data.py
```

会在 `data/` 目录下生成 `UserBehavior.csv`（约 5 万条模拟数据），即可跑通全部代码。

**方式二：使用真实数据（推荐）**

1. 访问天池平台下载数据集：<https://tianchi.aliyun.com/dataset/649>
2. 将下载的 `UserBehavior.csv` 放入 `data/` 目录

### 3. 运行分析

```bash
# 按顺序运行，或单独运行任意模块
python src/01_data_exploration.py       # 数据探索 + PV/UV 趋势
python src/02_funnel_analysis.py        # 转化漏斗 + 热销品类
python src/03_rfm_analysis.py           # RFM 用户分层
python src/04_cross_border_trends.py    # 跨境选品趋势
```

图表自动保存到 `output/charts/` 目录。

## 分析内容

### Part A：用户行为分析

| 模块 | 分析内容 | 输出图表 |
|------|---------|---------|
| 数据探索 | PV/UV 趋势、24h 行为分布、行为占比 | `daily_pv_uv_trend.png` `hourly_behavior_distribution.png` `behavior_type_pie.png` |
| 转化漏斗 | 浏览→收藏→加购→购买 各环节转化率 | `conversion_funnel.png` |
| 热销品类 | 购买频次 Top10 品类排名 | `top10_categories.png` |
| RFM 分层 | 用户分 8 层，识别高价值/流失用户 | `rfm_scatter.png` `rfm_user_segments.png` |

### Part C：跨境选品趋势

| 模块 | 分析内容 | 输出图表 |
|------|---------|---------|
| 趋势对比 | 5 个品类近 12 个月搜索热度 | `trends_multi_category.png` |
| 热力图 | 品类 × 时间搜索热度分布 | `trend_summary_heatmap.png` |
| 选品建议 | 上升品类 + 高热度品类综合推荐 | 控制台输出 |

## 技术栈

- **Python 3.10+**
- **pandas** — 数据清洗与聚合
- **matplotlib** — 数据可视化
- **pytrends** — Google Trends 数据获取

## 数据说明

### 天池用户行为数据集

| 字段 | 说明 |
|------|------|
| user_id | 用户 ID |
| item_id | 商品 ID |
| category_id | 品类 ID |
| behavior_type | 行为类型：pv(浏览) / fav(收藏) / cart(加购) / buy(购买) |
| timestamp | 时间戳（Unix） |

### Google Trends 数据

通过 `pytrends` 库获取，无需 API Key。分析品类包括蓝牙耳机、手机壳、LED灯带、厨房收纳、瑜伽垫等跨境电商热门品类。

> 如果网络无法访问 Google Trends，脚本会自动切换为模拟数据。

## 关键结论示例

> 以下为模拟数据的结论，使用真实数据后结论会变化。

- 严格漏斗分析：浏览 1000 → 收藏 812 → 加购 738 → 购买 658，整体转化率 **65.8%**
- 18:00-19:00 为用户最活跃时段，晚间流量占全天 40%+
- RFM 分析中"重要价值用户"占比约 **32.0%**，"一般挽留用户"占比约 **36.5%**
- Google Trends 显示 LED 灯带和蓝牙耳机搜索热度持续领先
