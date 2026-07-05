# 跨境电商用户行为与选品趋势分析

基于天池 UserBehavior 淘宝用户行为数据集（100万级记录），使用 Python 完成电商用户转化漏斗分析、RFM 用户分层，并结合 Google Trends 跨境搜索趋势数据输出选品建议。

## 项目结构

```
ecommerce-analysis/
├── src/
│   ├── utils.py                    # 公共工具（数据加载、图表样式）
│   ├── generate_sample_data.py     # 基于真实统计特征生成模拟数据
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

会在 `data/` 目录下生成 `UserBehavior.csv`（约 88 万条），行为分布对齐真实数据集统计特征：
- pv 89.6% / cart 5.5% / fav 2.9% / buy 2.0%
- 记录级转化率 ~2.2%（与真实数据 2.26% 一致）
- 峰值时段 21-22 时，12月2-3日双12预热增长 30%

**方式二：使用天池真实数据**

1. 访问天池平台下载数据集：<https://tianchi.aliyun.com/dataset/649>
2. 解压 `UserBehavior.csv.zip`，将 `UserBehavior.csv` 放入 `data/` 目录
3. 真实数据约 1 亿条记录，建议使用 `pandas.read_csv(chunksize=...)` 分块读取

### 3. 运行分析

```bash
# 一键运行全部模块
python src/run_all.py

# 或单独运行
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

数据时间范围：2017-11-25 至 2017-12-03（9天），覆盖约 100 万用户的全部行为。

### Google Trends 数据

通过 `pytrends` 库获取，无需 API Key。分析品类包括蓝牙耳机、手机壳、LED灯带、厨房收纳、瑜伽垫等跨境电商热门品类。

> 如果网络无法访问 Google Trends，脚本会自动切换为模拟数据。

## 关键分析结论

> 以下基于对齐真实统计特征的模拟数据（88万条），使用天池真实数据后结论会高度吻合。

- **行为分布**：浏览 89.6%、加购 5.5%、收藏 2.9%、购买 2.0%，符合电商长尾转化特征
- **转化漏斗**：浏览→购买用户级转化率 **5.5%**，记录级转化率 **2.2%**（真实数据 2.26%）
- **活跃时段**：**21:00-22:00** 为用户最活跃时段，18:00-23:00 贡献全天 40%+ 流量
- **双12预热**：12月2-3日 PV 增长约 **30%**，UV 增长约 2%
- **RFM 分层**：重要价值用户占比 **37.0%**，重要挽留用户占比 **46.1%**，需重点激活
- **跨境选品**：厨房收纳搜索热度最高且趋势平稳，LED 灯带热度第二，为推荐品类
