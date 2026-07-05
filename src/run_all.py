"""
run_all.py - 一键运行全部分析

执行顺序：
  1. 生成模拟数据（如果 data/UserBehavior.csv 不存在）
  2. 用户行为探索分析
  3. 转化漏斗分析
  4. RFM 用户分层
  5. 跨境选品趋势

用法：
  python src/run_all.py
"""

import sys
import os
import importlib.util
sys.path.insert(0, os.path.dirname(__file__))

import generate_sample_data
from utils import DATA_DIR


def _load_module(name, filename):
    """动态加载数字开头的模块"""
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


explore = _load_module("explore", "01_data_exploration.py")
funnel = _load_module("funnel", "02_funnel_analysis.py")
rfm = _load_module("rfm", "03_rfm_analysis.py")
trends = _load_module("trends", "04_cross_border_trends.py")


def main():
    # 检查数据是否存在，不存在则生成模拟数据
    data_path = os.path.join(DATA_DIR, "UserBehavior.csv")
    if not os.path.exists(data_path):
        print("数据文件不存在，生成模拟数据...")
        generate_sample_data.generate()
    else:
        print("数据文件已存在，跳过模拟数据生成。")

    print("\n" + "=" * 60)
    print("开始运行全部分析")
    print("=" * 60 + "\n")

    explore.main()
    funnel.main()
    rfm.main()
    trends.main()

    print("\n" + "=" * 60)
    print("所有分析完成！图表已保存到 output/charts/")
    print("=" * 60)


if __name__ == "__main__":
    main()
