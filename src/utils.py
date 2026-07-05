"""
utils.py - 公共工具模块
负责数据加载、图表样式配置、通用辅助函数
"""

import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ============================================================
# 图表样式配置
# ============================================================

# 设置中文字体（Windows 用微软雅黑，macOS 用 PingFang SC）
def _setup_font():
    candidates = ["Microsoft YaHei", "SimHei", "PingFang SC", "WenQuanYi Micro Hei"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["axes.unicode_minus"] = False
            return name
    # 没找到中文字体就用默认
    return None

_setup_font()

# 全局配色方案
COLORS = {
    "primary": "#1e5f9e",
    "secondary": "#4a90d9",
    "accent": "#e87d3e",
    "success": "#2ea66b",
    "danger": "#d85a30",
    "gray": "#888888",
    "light": "#e8f0fa",
}

# 漏斗各阶段颜色
FUNNEL_COLORS = ["#1e5f9e", "#378add", "#4a90d9", "#7ab8e8", "#a5d0f0"]

# 图表保存路径
CHART_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "charts")
os.makedirs(CHART_DIR, exist_ok=True)


def save_chart(fig, name, dpi=200):
    """保存图表到 output/charts/ 目录"""
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [saved] {path}")
    return path


# ============================================================
# 数据加载
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_user_behavior(filename="UserBehavior.csv"):
    """
    加载天池用户行为数据集

    数据格式（天池标准格式）:
        user_id, item_id, category_id, behavior_type, timestamp

    behavior_type 取值:
        pv    - 浏览
        fav   - 收藏
        cart  - 加购
        buy   - 购买

    Returns:
        pd.DataFrame
    """
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[错误] 数据文件不存在: {filepath}")
        print("请先从天池平台下载数据集:")
        print("  https://tianchi.aliyun.com/dataset/649")
        print("下载后放入 data/ 目录，文件名为 UserBehavior.csv")
        return None

    df = pd.read_csv(
        filepath,
        names=["user_id", "item_id", "category_id", "behavior_type", "timestamp"],
        dtype={
            "user_id": "int32",
            "item_id": "int32",
            "category_id": "int32",
            "behavior_type": "category",
            "timestamp": "int32",
        },
    )

    # 转换时间戳
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert(
        "Asia/Shanghai"
    )
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour

    # 行为类型中文映射
    behavior_map = {"pv": "浏览", "fav": "收藏", "cart": "加购", "buy": "购买"}
    df["behavior_cn"] = df["behavior_type"].map(behavior_map)

    print(f"数据加载完成: {len(df):,} 条记录, {df['user_id'].nunique():,} 个用户")
    print(f"时间范围: {df['date'].min()} ~ {df['date'].max()}")
    return df


# ============================================================
# 行为类型常量
# ============================================================

BEHAVIOR_TYPES = ["pv", "fav", "cart", "buy"]
BEHAVIOR_CN = {"pv": "浏览", "fav": "收藏", "cart": "加购", "buy": "购买"}
FUNNEL_STEPS = ["pv", "fav", "cart", "buy"]
