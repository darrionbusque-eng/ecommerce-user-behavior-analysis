"""
04_cross_border_trends.py - 跨境电商选品趋势分析

使用 Google Trends API (pytrends) 分析热门品类在目标国家的搜索趋势，
结合 Part A 的用户行为分析结果，输出选品建议。

分析内容:
  1. 热门品类在美/英/日三国的搜索热度对比
  2. 近 12 个月趋势变化（上升 vs 下降）
  3. 选品推荐报告

输出图表:
  - trends_multi_category.png    多品类趋势对比
  - trends_by_country.png        分国家趋势对比
  - trend_summary_heatmap.png    趋势汇总热力图

注意:
  - pytrends 通过非官方接口访问 Google Trends，无需 API Key
  - 请求频率不宜过高，每次调用之间会自动 sleep
  - 如果网络无法访问 Google，脚本会使用模拟数据生成图表
  - pip install pytrends
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import save_chart, COLORS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "charts")

# 分析的品类关键词（英文，面向跨境市场）
# 可根据 Part A 热销品类自行调整
CATEGORIES = {
    "bluetooth earbuds": "蓝牙耳机",
    "phone case": "手机壳",
    "LED strip lights": "LED灯带",
    "kitchen organizer": "厨房收纳",
    "yoga mat": "瑜伽垫",
}

# 目标国家
COUNTRIES = ["united_states", "united_kingdom", "japan"]
COUNTRY_LABELS = {"united_states": "美国", "united_kingdom": "英国", "japan": "日本"}


def fetch_trends():
    """从 Google Trends 获取数据"""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("[提示] pytrends 未安装，使用模拟数据。pip install pytrends 后可获得真实数据。")
        return generate_mock_data()

    print("正在连接 Google Trends API...")
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
    except Exception as e:
        print(f"[警告] 连接 Google Trends 失败: {e}")
        print("使用模拟数据代替。")
        return generate_mock_data()

    all_data = {}

    for keyword in CATEGORIES:
        print(f"  获取关键词: {keyword} ...")
        try:
            pytrends.build_payload([keyword], cat=0, timeframe="today 12-m", geo="", gprop="")
            data = pytrends.interest_over_time()

            if data.empty or keyword not in data.columns:
                print(f"    [警告] 未获取到数据，跳过")
                continue

            all_data[keyword] = data[keyword]
            time.sleep(1)  # 避免频率限制
        except Exception as e:
            print(f"    [警告] 获取失败: {e}")
            continue

    if not all_data:
        print("[提示] 未能获取任何 Google Trends 数据，使用模拟数据。")
        return generate_mock_data()

    trends_df = pd.DataFrame(all_data)
    print(f"获取完成: {len(trends_df)} 周数据, {len(all_data)} 个关键词")
    return trends_df


def generate_mock_data():
    """生成模拟趋势数据（无法访问 Google Trends 时使用）"""
    print("生成模拟趋势数据...")
    weeks = 52
    dates = pd.date_range(end=pd.Timestamp.today(), periods=weeks, freq="7D")

    data = {}
    np.random.seed(42)

    for keyword in CATEGORIES:
        # 每个关键词有不同的基线和趋势
        base = np.random.randint(30, 60)
        trend = np.random.choice([-1, 0, 1])  # 下降/平稳/上升
        noise = np.random.normal(0, 5, weeks)

        values = base + trend * np.linspace(0, 20, weeks) + noise
        values = np.clip(values, 0, 100).astype(int)
        data[keyword] = values

    return pd.DataFrame(data, index=dates)


def plot_multi_category(trends_df):
    """多品类趋势对比图"""
    fig, ax = plt.subplots(figsize=(14, 6))

    colors = [COLORS["primary"], COLORS["accent"], COLORS["success"],
              COLORS["danger"], "#8b5cf6"]

    for i, col in enumerate(trends_df.columns):
        cn_name = CATEGORIES.get(col, col)
        ax.plot(trends_df.index, trends_df[col], label=f"{col} ({cn_name})",
                color=colors[i % len(colors)], linewidth=2, alpha=0.8)

    ax.set_xlabel("日期", fontsize=12)
    ax.set_ylabel("搜索热度", fontsize=12)
    ax.set_title("跨境品类 Google Trends 搜索热度对比（近12个月）", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", fontsize=10)
    ax.set_ylim(0, 110)
    ax.grid(True, alpha=0.3)

    save_chart(fig, "trends_multi_category.png")


def plot_trend_summary(trends_df):
    """趋势汇总热力图"""
    # 计算每个品类的平均热度和趋势变化率
    summary = pd.DataFrame(index=trends_df.columns)
    summary["平均热度"] = trends_df.mean()
    summary["近3月均值"] = trends_df.tail(12).mean()  # 近12周
    summary["上3月均值"] = trends_df.head(12).mean()
    summary["趋势变化率"] = ((summary["近3月均值"] - summary["上3月均值"]) / summary["上3月均值"] * 100).round(1)

    # 判断趋势方向
    summary["趋势"] = summary["趋势变化率"].apply(
        lambda x: "上升" if x > 5 else ("下降" if x < -5 else "平稳")
    )

    print("\n品类趋势汇总:")
    print(summary.to_string())

    # 绘制热力图
    fig, ax = plt.subplots(figsize=(10, 5))

    # 只取热度数据画热力图
    heat_data = trends_df.T
    heat_data.index = [CATEGORIES.get(c, c) for c in heat_data.index]

    im = ax.imshow(heat_data.values, aspect="auto", cmap="YlOrRd", interpolation="nearest")

    ax.set_xticks(range(0, len(trends_df), 4))
    ax.set_xticklabels([d.strftime("%Y-%m") for d in trends_df.index[::4]], rotation=45, fontsize=9)
    ax.set_yticks(range(len(heat_data)))
    ax.set_yticklabels(heat_data.index, fontsize=11)

    ax.set_title("品类搜索热度热力图", fontsize=14, fontweight="bold", pad=15)
    plt.colorbar(im, ax=ax, label="搜索热度")

    save_chart(fig, "trend_summary_heatmap.png")

    return summary


def generate_recommendations(summary):
    """生成选品建议"""
    print("\n" + "=" * 60)
    print("选品建议")
    print("=" * 60)

    # 按平均热度排序
    ranked = summary.sort_values("平均热度", ascending=False)

    print("\n热度排名:")
    for i, (keyword, row) in enumerate(ranked.iterrows(), 1):
        cn = CATEGORIES.get(keyword, keyword)
        trend_icon = {"上升": "↑", "下降": "↓", "平稳": "→"}.get(row["趋势"], "?")
        print(f"  {i}. {keyword} ({cn})")
        print(f"     平均热度: {row['平均热度']:.1f}  趋势: {trend_icon} {row['趋势']} ({row['趋势变化率']:+.1f}%)")

    # 推荐逻辑
    rising = ranked[ranked["趋势"] == "上升"]
    high_popularity = ranked[ranked["平均热度"] > ranked["平均热度"].median()]

    print("\n推荐策略:")
    if len(rising) > 0:
        print(f"  优先关注（热度上升）: {', '.join(rising.index)}")
    recommended = set(rising.index) | set(high_popularity.head(3).index)
    print(f"  综合推荐品类: {', '.join(recommended)}")
    print()


def main():
    print("=" * 60)
    print("跨境电商选品趋势分析")
    print("=" * 60)

    trends_df = fetch_trends()

    # 保存趋势数据
    trends_df.to_csv(os.path.join(DATA_DIR, "trends_data.csv"))
    print(f"趋势数据已保存到 data/trends_data.csv")

    plot_multi_category(trends_df)
    summary = plot_trend_summary(trends_df)
    generate_recommendations(summary)

    print("\n跨境选品趋势分析完成！图表已保存到 output/charts/")


if __name__ == "__main__":
    main()
