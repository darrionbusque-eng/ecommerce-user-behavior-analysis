"""
generate_sample_data.py - 生成模拟用户行为数据（用于测试）

如果你还没有从天池下载数据集，可以先运行此脚本生成一份模拟数据，
让代码跑通。拿到真实数据后替换 data/UserBehavior.csv 即可。

模拟数据规模: 约 50,000 条记录, 1,000 个用户, 9 天数据
数据结构完全对齐天池 UserBehavior 数据集格式
"""

import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_DIR, "UserBehavior.csv")


def generate():
    # 参数
    n_users = 1000
    n_items = 500
    n_categories = 50
    start_date = pd.Timestamp("2017-11-25", tz="Asia/Shanghai")
    n_days = 9  # 11.25 ~ 12.03

    # 每个用户的行为次数（长尾分布，少数活跃用户贡献大量行为）
    behaviors_per_user = np.random.exponential(scale=50, size=n_users).astype(int) + 5

    records = []
    for user_id in range(1, n_users + 1):
        n = behaviors_per_user[user_id - 1]
        for _ in range(n):
            # 随机时间（白天概率更高）
            day_offset = random.randint(0, n_days - 1)
            hour = int(np.random.choice(range(24), p=_hour_weights()))
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            dt = start_date + pd.Timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)

            # 行为类型（浏览占绝大多数）
            behavior = np.random.choice(
                ["pv", "fav", "cart", "buy"],
                p=[0.80, 0.06, 0.08, 0.06],
            )

            item_id = random.randint(1, n_items)
            category_id = random.randint(1, n_categories)

            records.append({
                "user_id": user_id,
                "item_id": item_id,
                "category_id": category_id,
                "behavior_type": behavior,
                "timestamp": int(dt.timestamp()),
            })

    df = pd.DataFrame(records)
    # 打乱顺序
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 保存（无表头，与天池格式一致）
    df.to_csv(OUTPUT_FILE, index=False, header=False)
    print(f"模拟数据生成完成: {len(df):,} 条记录")
    print(f"用户数: {df['user_id'].nunique():,}")
    print(f"商品数: {df['item_id'].nunique():,}")
    print(f"保存到: {OUTPUT_FILE}")


def _hour_weights():
    """生成 24 小时的行为概率分布（白天活跃，夜间低迷）"""
    raw = np.array([
        0.5, 0.3, 0.2, 0.2, 0.2, 0.3,  # 0-5
        0.8, 1.5, 2.5, 3.0, 3.5, 4.0,  # 6-11
        3.5, 2.5, 2.5, 3.0, 3.5, 4.5,  # 12-17
        5.0, 5.0, 4.5, 3.5, 2.5, 1.0,  # 18-23
    ])
    return raw / raw.sum()


if __name__ == "__main__":
    generate()
