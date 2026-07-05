"""
generate_sample_data.py - 基于天池 UserBehavior 真实统计特征生成模拟数据

数据规模: 约 100 万条记录, 10,000 个用户, 9 天数据 (2017-11-25 ~ 2017-12-03)
行为分布对齐真实数据集统计:
  pv  89.5%   cart  5.5%   fav  2.9%   buy  2.0%
  浏览→购买转化率 ~2.3% (记录级)   用户级购买率 ~5%
  峰值时段 21-22 时   12月2-3日双12预热 PV/UV 增长约 30%

核心建模思路:
  真实电商中用户行为高度分化:
  - ~95% 用户: 仅浏览, 偶尔收藏/加购, 不产生购买
  - ~5%  用户: 活跃购买者, 行为覆盖 pv/fav/cart/buy 全链路
  这样总行为占比才能同时满足 pv~89.5% 和 buy~2.0%

数据结构完全对齐天池 UserBehavior.csv 格式:
  user_id, item_id, category_id, behavior_type, timestamp
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_DIR, "UserBehavior.csv")

# 真实数据集参数
N_USERS = 10_000
N_ITEMS = 50_000
N_CATEGORIES = 5_000
START_DATE = pd.Timestamp("2017-11-25", tz="Asia/Shanghai")
N_DAYS = 9  # 11.25 ~ 12.03

# 用户类型比例 (对齐真实数据: 约5%用户产生购买)
BUYER_RATIO = 0.055  # 5.5% 的用户是购买者

# 浏览型用户行为概率 (无购买行为)
BROWSER_PROBS = [0.929, 0.048, 0.023, 0.000]  # pv, cart, fav, buy
# 购买型用户行为概率 (有购买行为, 购买占比更高)
BUYER_PROBS = [0.600, 0.120, 0.080, 0.200]  # pv, cart, fav, buy

# 24小时行为权重 (峰值 21-22 时)
HOUR_WEIGHTS = np.array([
    0.4, 0.25, 0.15, 0.12, 0.12, 0.20,   # 0-5
    0.50, 1.20, 2.50, 3.50, 4.00, 4.20,  # 6-11
    3.80, 2.80, 2.80, 3.20, 3.80, 4.50,  # 12-17
    5.00, 5.20, 5.50, 6.00, 4.50, 1.80,  # 18-23  峰值21-22
])
HOUR_WEIGHTS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()

# 每日行为量权重 (12月2-3日双12预热增长约30%)
DAY_WEIGHTS = np.array([1.0, 0.97, 0.95, 0.94, 0.96, 0.98, 1.02, 1.30, 1.28])
DAY_WEIGHTS = DAY_WEIGHTS / DAY_WEIGHTS.sum()

BEHAVIOR_TYPES = ["pv", "cart", "fav", "buy"]


def generate():
    # 分配用户类型
    n_buyers = int(N_USERS * BUYER_RATIO)
    n_browsers = N_USERS - n_buyers
    user_types = np.array(["browser"] * n_browsers + ["buyer"] * n_buyers)
    np.random.shuffle(user_types)

    # 每个用户的行为总数: 长尾分布
    # 浏览型: 人均约 80 条 (exponential scale=80)
    # 购买型: 人均约 150 条 (更活跃)
    behaviors_per_user = np.zeros(N_USERS, dtype=int)
    for i in range(N_USERS):
        if user_types[i] == "buyer":
            behaviors_per_user[i] = int(np.random.exponential(scale=150)) + 10
        else:
            behaviors_per_user[i] = int(np.random.exponential(scale=80)) + 5

    total_behaviors = behaviors_per_user.sum()
    print(f"正在生成 {total_behaviors:,} 条记录...")
    print(f"  浏览型用户: {n_browsers:,}  购买型用户: {n_buyers:,}")

    # 向量化生成
    all_user_ids = np.repeat(np.arange(1, N_USERS + 1), behaviors_per_user)

    # 根据用户类型分配行为概率
    all_behaviors = np.empty(total_behaviors, dtype="U4")
    idx = 0
    for i in range(N_USERS):
        n = behaviors_per_user[i]
        if user_types[i] == "buyer":
            all_behaviors[idx:idx + n] = np.random.choice(BEHAVIOR_TYPES, size=n, p=BUYER_PROBS)
        else:
            all_behaviors[idx:idx + n] = np.random.choice(BEHAVIOR_TYPES, size=n, p=BROWSER_PROBS)
        idx += n

    # 商品和品类
    all_items = np.random.randint(1, N_ITEMS + 1, size=total_behaviors)
    all_categories = np.random.randint(1, N_CATEGORIES + 1, size=total_behaviors)

    # 时间戳
    day_choices = np.random.choice(N_DAYS, size=total_behaviors, p=DAY_WEIGHTS)
    hour_choices = np.random.choice(24, size=total_behaviors, p=HOUR_WEIGHTS)
    minute_choices = np.random.randint(0, 60, size=total_behaviors)
    second_choices = np.random.randint(0, 60, size=total_behaviors)

    base_ts = int(START_DATE.timestamp())
    all_timestamps = (
        base_ts
        + day_choices * 86400
        + hour_choices * 3600
        + minute_choices * 60
        + second_choices
    )

    # 组装 DataFrame
    df = pd.DataFrame({
        "user_id": all_user_ids,
        "item_id": all_items,
        "category_id": all_categories,
        "behavior_type": all_behaviors,
        "timestamp": all_timestamps,
    })

    # 打乱顺序
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 保存
    df.to_csv(OUTPUT_FILE, index=False, header=False)

    # 统计输出
    print(f"\n数据生成完成!")
    print(f"  总记录数:   {len(df):,}")
    print(f"  用户数:     {df['user_id'].nunique():,}")
    print(f"  商品数:     {df['item_id'].nunique():,}")
    print(f"  品类数:     {df['category_id'].nunique():,}")
    print(f"  行为分布:")
    for bt in BEHAVIOR_TYPES:
        count = (df["behavior_type"] == bt).sum()
        pct = count / len(df) * 100
        print(f"    {bt:>4}: {count:>8,}  ({pct:.1f}%)")
    # 用户级购买率
    buyers = df[df["behavior_type"] == "buy"]["user_id"].nunique()
    total_users = df["user_id"].nunique()
    print(f"  购买用户:   {buyers:,} / {total_users:,}  ({buyers/total_users*100:.1f}%)")
    # 记录级转化率
    pv_count = (df["behavior_type"] == "pv").sum()
    buy_count = (df["behavior_type"] == "buy").sum()
    print(f"  记录级转化率 (buy/pv): {buy_count/pv_count*100:.2f}%")
    print(f"  保存到: {OUTPUT_FILE}")
    print(f"  文件大小: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    generate()
