"""
02_funnel_analysis.py - 转化漏斗分析

分析内容:
  1. 浏览 → 收藏 → 加购 → 购买 转化漏斗
  2. 各环节转化率
  3. 整体转化率
  4. 热销品类 Top10

输出图表:
  - conversion_funnel.png
  - top10_categories.png
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils import load_user_behavior, save_chart, COLORS, BEHAVIOR_CN, FUNNEL_COLORS


def conversion_funnel(df):
    """转化漏斗分析"""
    print("=" * 60)
    print("转化漏斗分析")
    print("=" * 60)

    # 严格漏斗：每个阶段必须完成前面所有行为
    # 例如：购买 = 浏览且收藏且加购且购买的用户
    funnel_data = []
    behavior_order = ["pv", "fav", "cart", "buy"]

    users_so_far = set(df["user_id"].unique())
    for btype in behavior_order:
        users_with_behavior = set(df[df["behavior_type"] == btype]["user_id"].unique())
        users_so_far = users_so_far & users_with_behavior
        funnel_data.append({"behavior": btype, "cn": BEHAVIOR_CN[btype], "users": len(users_so_far)})

    funnel_df = pd.DataFrame(funnel_data)

    # 计算转化率
    funnel_df["conv_rate"] = funnel_df["users"] / funnel_df["users"].iloc[0] * 100
    funnel_df["step_rate"] = funnel_df["users"] / funnel_df["users"].shift(1) * 100
    funnel_df["step_rate"] = funnel_df["step_rate"].fillna(100)

    print(funnel_df.to_string(index=False))
    print()

    overall_conv = funnel_df.loc[funnel_df["behavior"] == "buy", "conv_rate"].values[0]
    print(f"整体转化率（浏览→购买）: {overall_conv:.2f}%")
    print()

    # 绘制漏斗图
    fig, ax = plt.subplots(figsize=(10, 6))

    stages = funnel_df["cn"].tolist()
    values = funnel_df["users"].tolist()
    max_val = max(values)

    bar_height = 0.6
    y_positions = range(len(stages) - 1, -1, -1)

    for i, (stage, value, y) in enumerate(zip(stages, values, y_positions)):
        # 漏斗效果：宽度逐渐缩小
        width_ratio = value / max_val
        bar_width = width_ratio * 0.8
        left = (1 - bar_width) / 2

        bar = mpatches.FancyBboxPatch(
            (left, y - bar_height / 2),
            bar_width,
            bar_height,
            boxstyle="round,pad=0.02",
            facecolor=FUNNEL_COLORS[i],
            edgecolor="white",
            linewidth=1,
        )
        ax.add_patch(bar)

        # 在柱内显示数值
        ax.text(
            0.5, y,
            f"{stage}\n{value:,} 人 ({funnel_df.loc[i, 'conv_rate']:.1f}%)",
            ha="center", va="center",
            fontsize=12, fontweight="bold",
            color="white" if i < 3 else "#333",
        )

        # 在右侧显示环节转化率
        if i > 0:
            step_rate = funnel_df.loc[i, "step_rate"]
            ax.annotate(
                f"环节转化率: {step_rate:.1f}%",
                xy=(1, y + 0.35),
                fontsize=10,
                color=COLORS["accent"],
                fontweight="bold",
            )

    ax.set_xlim(-0.1, 1.4)
    ax.set_ylim(-0.8, len(stages) - 0.2)
    ax.axis("off")
    ax.set_title("用户转化漏斗分析", fontsize=16, fontweight="bold", pad=20)

    save_chart(fig, "conversion_funnel.png")

    return funnel_df


def top_categories(df, top_n=10):
    """热销品类 Top N"""
    print("=" * 60)
    print(f"热销品类 Top {top_n}")
    print("=" * 60)

    # 按购买行为统计品类销量
    buy_df = df[df["behavior_type"] == "buy"]
    category_sales = buy_df.groupby("category_id").agg(
        sales=("item_id", "count"),
        buyers=("user_id", "nunique"),
    ).reset_index()

    category_sales = category_sales.sort_values("sales", ascending=False).head(top_n)
    category_sales["rank"] = range(1, len(category_sales) + 1)

    print(category_sales.to_string(index=False))
    print()

    # 绘制水平柱状图
    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = range(len(category_sales) - 1, -1, -1)
    bars = ax.barh(
        y_pos,
        category_sales["sales"],
        color=COLORS["primary"],
        alpha=0.8,
        height=0.6,
    )

    # 渐变色效果
    for i, bar in enumerate(bars):
        alpha = 0.4 + 0.6 * (len(bars) - i) / len(bars)
        bar.set_alpha(alpha)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"品类 {cid}" for cid in category_sales["category_id"]])
    ax.set_xlabel("销量（购买次数）", fontsize=12)
    ax.set_title(f"热销品类 Top {top_n}", fontsize=14, fontweight="bold", pad=15)

    # 在柱右侧显示数值
    for i, (sales, buyers) in enumerate(zip(category_sales["sales"], category_sales["buyers"])):
        ax.text(sales + max(category_sales["sales"]) * 0.01, len(category_sales) - 1 - i,
                f"{sales} ({buyers} 人购买)", va="center", fontsize=10, color="#555")

    ax.set_xlim(0, max(category_sales["sales"]) * 1.2)

    save_chart(fig, "top10_categories.png")

    return category_sales


def main():
    df = load_user_behavior()
    if df is None:
        return

    conversion_funnel(df)
    top_categories(df)

    print("\n转化漏斗分析完成！图表已保存到 output/charts/")


if __name__ == "__main__":
    main()
