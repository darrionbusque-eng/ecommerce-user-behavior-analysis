"""
03_rfm_analysis.py - RFM 用户分层分析

RFM 模型:
  R (Recency):   最近一次购买距今多少天，越小越好
  F (Frequency):  购买次数，越大越好
  M (Monetary):  本数据集无金额，用购买商品种类数替代，越大越好

分层策略:
  按 R、F、M 三个维度与均值比较，分为高/低两档
  三个维度组合出 8 种用户类型

输出图表:
  - rfm_scatter.png          RFM 三维散点图
  - rfm_user_segments.png    用户分层分布
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import load_user_behavior, save_chart, COLORS


def calculate_rfm(df):
    """计算 RFM 指标"""
    print("=" * 60)
    print("RFM 指标计算")
    print("=" * 60)

    # 只看购买行为
    buy_df = df[df["behavior_type"] == "buy"].copy()

    # 参照日期：数据集最后日期 + 1 天
    ref_date = df["date"].max() + pd.Timedelta(days=1)

    rfm = buy_df.groupby("user_id").agg(
        R=("date", lambda x: (ref_date - x.max()).days),  # Recency
        F=("item_id", "count"),                            # Frequency
        M=("category_id", "nunique"),                      # Monetary proxy
    ).reset_index()

    print(f"有购买行为的用户数: {len(rfm):,}")
    print(f"\nRFM 统计描述:")
    print(rfm[["R", "F", "M"]].describe().round(2))
    print()

    return rfm


def segment_users(rfm):
    """用户分层"""
    print("=" * 60)
    print("用户分层")
    print("=" * 60)

    # 与均值比较（也可以用中位数）
    r_mean = rfm["R"].mean()
    f_mean = rfm["F"].mean()
    m_mean = rfm["M"].mean()

    # R 越小越好，F/M 越大越好
    rfm["R_flag"] = (rfm["R"] <= r_mean).astype(int)  # 1=好
    rfm["F_flag"] = (rfm["F"] >= f_mean).astype(int)
    rfm["M_flag"] = (rfm["M"] >= m_mean).astype(int)

    # 组合标签
    def label_user(row):
        r, f, m = row["R_flag"], row["F_flag"], row["M_flag"]
        if r == 1 and f == 1 and m == 1:
            return "重要价值用户"
        elif r == 1 and f == 0 and m == 1:
            return "重要发展用户"
        elif r == 1 and f == 1 and m == 0:
            return "重要保持用户"
        elif r == 1 and f == 0 and m == 0:
            return "重要挽留用户"
        elif r == 0 and f == 1 and m == 1:
            return "一般价值用户"
        elif r == 0 and f == 0 and m == 1:
            return "一般发展用户"
        elif r == 0 and f == 1 and m == 0:
            return "一般保持用户"
        else:
            return "一般挽留用户"

    rfm["segment"] = rfm.apply(label_user, axis=1)

    # 统计各层人数
    segment_counts = rfm["segment"].value_counts()
    print("用户分层结果:")
    for seg, count in segment_counts.items():
        pct = count / len(rfm) * 100
        print(f"  {seg:>8}:  {count:>6,} 人  ({pct:.1f}%)")
    print()

    return rfm, segment_counts


def plot_rfm_scatter(rfm):
    """RFM 散点图"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # R vs F
    ax = axes[0]
    ax.scatter(rfm["R"], rfm["F"], c=COLORS["primary"], alpha=0.3, s=10)
    ax.set_xlabel("R (最近购买距今天数)", fontsize=11)
    ax.set_ylabel("F (购买次数)", fontsize=11)
    ax.set_title("R vs F", fontsize=13, fontweight="bold")

    # R vs M
    ax = axes[1]
    ax.scatter(rfm["R"], rfm["M"], c=COLORS["accent"], alpha=0.3, s=10)
    ax.set_xlabel("R (最近购买距今天数)", fontsize=11)
    ax.set_ylabel("M (购买品类数)", fontsize=11)
    ax.set_title("R vs M", fontsize=13, fontweight="bold")

    # F vs M
    ax = axes[2]
    ax.scatter(rfm["F"], rfm["M"], c=COLORS["success"], alpha=0.3, s=10)
    ax.set_xlabel("F (购买次数)", fontsize=11)
    ax.set_ylabel("M (购买品类数)", fontsize=11)
    ax.set_title("F vs M", fontsize=13, fontweight="bold")

    plt.suptitle("RFM 用户分布散点图", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_chart(fig, "rfm_scatter.png")


def plot_user_segments(segment_counts):
    """用户分层分布图"""
    # 按重要性排序
    order = [
        "重要价值用户", "重要发展用户", "重要保持用户", "重要挽留用户",
        "一般价值用户", "一般发展用户", "一般保持用户", "一般挽留用户",
    ]
    segments = [s for s in order if s in segment_counts.index]
    values = [segment_counts[s] for s in segments]
    pcts = [v / sum(values) * 100 for v in values]

    # 颜色：重要=蓝色系，一般=灰色系
    colors = [
        "#1e5f9e", "#378add", "#4a90d9", "#7ab8e8",
        "#888888", "#a0a0a0", "#b8b8b8", "#d0d0d0",
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(segments) - 1, -1, -1), values, color=colors, height=0.6)

    ax.set_yticks(range(len(segments) - 1, -1, -1))
    ax.set_yticklabels(segments, fontsize=11)
    ax.set_xlabel("用户数", fontsize=12)
    ax.set_title("RFM 用户分层分布", fontsize=14, fontweight="bold", pad=15)

    # 在柱右侧显示数值和占比
    for i, (val, pct) in enumerate(zip(values, pcts)):
        ax.text(val + max(values) * 0.01, len(segments) - 1 - i,
                f"{val:,} ({pct:.1f}%)", va="center", fontsize=10, color="#555")

    ax.set_xlim(0, max(values) * 1.25)

    save_chart(fig, "rfm_user_segments.png")


def main():
    df = load_user_behavior()
    if df is None:
        return

    rfm = calculate_rfm(df)
    rfm, segment_counts = segment_users(rfm)

    plot_rfm_scatter(rfm)
    plot_user_segments(segment_counts)

    print("\nRFM 用户分层分析完成！图表已保存到 output/charts/")


if __name__ == "__main__":
    main()
