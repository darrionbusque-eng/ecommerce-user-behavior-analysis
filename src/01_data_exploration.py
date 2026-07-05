"""
01_data_exploration.py - 数据探索与 PV/UV 趋势分析

分析内容:
  1. 数据概览（记录数、用户数、商品数、行为分布）
  2. 每日 PV/UV 趋势
  3. 每小时行为分布（用户活跃时段）
  4. 行为类型占比

输出图表:
  - daily_pv_uv_trend.png
  - hourly_behavior_distribution.png
  - behavior_type_pie.png
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils import load_user_behavior, save_chart, COLORS, BEHAVIOR_CN


def data_overview(df):
    """数据概览"""
    print("=" * 60)
    print("数据概览")
    print("=" * 60)
    print(f"总记录数:     {len(df):>12,}")
    print(f"用户数:       {df['user_id'].nunique():>12,}")
    print(f"商品数:       {df['item_id'].nunique():>12,}")
    print(f"品类数:       {df['category_id'].nunique():>12,}")
    print(f"时间跨度:     {df['date'].min()} ~ {df['date'].max()}")
    print()

    # 行为类型分布
    print("行为类型分布:")
    behavior_counts = df["behavior_type"].value_counts()
    for btype, count in behavior_counts.items():
        pct = count / len(df) * 100
        cn = BEHAVIOR_CN.get(btype, btype)
        print(f"  {btype:>4} ({cn}):  {count:>10,}  ({pct:.1f}%)")
    print()


def daily_pv_uv(df):
    """每日 PV/UV 趋势"""
    print("=" * 60)
    print("每日 PV/UV 趋势")
    print("=" * 60)

    daily = df.groupby("date").agg(
        pv=("user_id", "count"),
        uv=("user_id", "nunique"),
    ).reset_index()

    print(daily.to_string(index=False))
    print()

    # 绘图
    fig, ax1 = plt.subplots(figsize=(12, 5))

    color_pv = COLORS["primary"]
    color_uv = COLORS["accent"]

    ax1.bar(daily["date"], daily["pv"], color=color_pv, alpha=0.7, label="PV (浏览量)")
    ax1.set_xlabel("日期", fontsize=12)
    ax1.set_ylabel("PV (浏览量)", color=color_pv, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=color_pv)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

    ax2 = ax1.twinx()
    ax2.plot(daily["date"], daily["uv"], color=color_uv, marker="o", linewidth=2, label="UV (访客数)")
    ax2.set_ylabel("UV (访客数)", color=color_uv, fontsize=12)
    ax2.tick_params(axis="y", labelcolor=color_uv)

    plt.title("每日 PV/UV 趋势", fontsize=14, fontweight="bold", pad=15)
    fig.autofmt_xdate()

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    save_chart(fig, "daily_pv_uv_trend.png")

    return daily


def hourly_behavior(df):
    """每小时行为分布"""
    print("=" * 60)
    print("每小时行为分布")
    print("=" * 60)

    hourly = df.groupby(["hour", "behavior_type"]).size().unstack(fill_value=0)

    # 绘图
    fig, ax = plt.subplots(figsize=(12, 5))

    behavior_order = ["pv", "fav", "cart", "buy"]
    colors = [COLORS["primary"], COLORS["accent"], COLORS["success"], COLORS["danger"]]

    bottom = None
    for i, btype in enumerate(behavior_order):
        if btype in hourly.columns:
            if bottom is None:
                ax.bar(hourly.index, hourly[btype], color=colors[i], label=BEHAVIOR_CN[btype], alpha=0.8)
                bottom = hourly[btype].copy()
            else:
                ax.bar(hourly.index, hourly[btype], bottom=bottom, color=colors[i], label=BEHAVIOR_CN[btype], alpha=0.8)
                bottom += hourly[btype]

    ax.set_xlabel("小时", fontsize=12)
    ax.set_ylabel("行为次数", fontsize=12)
    ax.set_title("24小时用户行为分布", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(range(0, 24))
    ax.legend(loc="upper right")
    ax.set_xlim(-0.5, 23.5)

    save_chart(fig, "hourly_behavior_distribution.png")

    # 找出活跃时段
    peak_hour = df.groupby("hour").size().idxmax()
    print(f"最活跃时段: {peak_hour}:00 - {peak_hour + 1}:00")
    print()


def behavior_pie(df):
    """行为类型占比饼图"""
    print("=" * 60)
    print("行为类型占比")
    print("=" * 60)

    counts = df["behavior_type"].value_counts()
    labels = [BEHAVIOR_CN.get(k, k) for k in counts.index]
    colors = [COLORS["primary"], COLORS["accent"], COLORS["success"], COLORS["danger"]]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors[: len(counts)],
        startangle=90,
        textprops={"fontsize": 12},
    )
    ax.set_title("用户行为类型占比", fontsize=14, fontweight="bold", pad=15)

    save_chart(fig, "behavior_type_pie.png")


def main():
    df = load_user_behavior()
    if df is None:
        return

    data_overview(df)
    daily_pv_uv(df)
    hourly_behavior(df)
    behavior_pie(df)

    print("\n数据探索分析完成！图表已保存到 output/charts/")


if __name__ == "__main__":
    main()
