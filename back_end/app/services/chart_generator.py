"""
图表生成工具模块

使用 matplotlib 生成 SPC 报告所需的图表：
- 直方图
- 运行图
- 概率图 (Q-Q 图)
- 控制图
"""

import io
import base64
from typing import List, Optional, Tuple, Dict
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端


def generate_histogram_plot(
    data: List[float],
    mean: float,
    std: float,
    usl: Optional[float] = None,
    lsl: Optional[float] = None,
    title: str = "Histogram",
    dpi: int = 150
) -> str:
    """
    生成直方图，并叠加正态分布曲线和规格限
    
    Args:
        data: 数据列表
        mean: 均值
        std: 标准差
        usl: 规格上限
        lsl: 规格下限
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=dpi)
    
    # 绘制直方图
    n, bins, patches = ax.hist(data, bins='auto', density=True, 
                               alpha=0.7, color='steelblue', 
                               edgecolor='black', linewidth=0.5)
    
    # 添加正态分布曲线
    x = np.linspace(min(data), max(data), 100)
    y = stats.norm.pdf(x, mean, std)
    ax.plot(x, y, 'r-', linewidth=2, label='Normal Fit')
    
    # 添加规格限
    if lsl is not None:
        ax.axvline(x=lsl, color='red', linestyle='--', linewidth=2, label='LSL')
    if usl is not None:
        ax.axvline(x=usl, color='red', linestyle='--', linewidth=2, label='USL')
    
    # 添加均值线
    ax.axvline(x=mean, color='green', linestyle='-', linewidth=1.5, label=f'Mean = {mean:.4f}')
    
    ax.set_xlabel('Value', fontsize=10)
    ax.set_ylabel('Density', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_run_chart(
    data: List[float],
    mean: Optional[float] = None,
    ucl: Optional[float] = None,
    lcl: Optional[float] = None,
    title: str = "Run Chart",
    dpi: int = 150
) -> str:
    """
    生成运行图（数据随时间变化的趋势图）
    
    Args:
        data: 数据列表
        mean: 中心线（均值）
        ucl: 控制上限
        lcl: 控制下限
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(10, 5), dpi=dpi)
    
    # 绘制数据点
    x = range(1, len(data) + 1)
    ax.plot(x, data, 'b-o', markersize=4, linewidth=1.5, label='Data')
    
    # 添加中心线
    if mean is None:
        mean = np.mean(data)
    ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, label=f'CL = {mean:.4f}')
    
    # 添加控制限
    if ucl is not None:
        ax.axhline(y=ucl, color='red', linestyle='--', linewidth=2, label=f'UCL = {ucl:.4f}')
    if lcl is not None:
        ax.axhline(y=lcl, color='red', linestyle='--', linewidth=2, label=f'LCL = {lcl:.4f}')
    
    ax.set_xlabel('Sample Number', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_probability_plot(
    data: List[float],
    title: str = "Normal Probability Plot",
    dpi: int = 150
) -> str:
    """
    生成正态概率图（Q-Q 图）
    
    Args:
        data: 数据列表
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    
    # 创建 Q-Q 图
    stats.probplot(data, dist="norm", plot=ax)
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_control_chart(
    data: List[float],
    subgroup_size: int = 1,
    chart_type: str = "Xbar-R",
    title: Optional[str] = None,
    dpi: int = 150
) -> Tuple[str, Optional[str]]:
    """
    生成控制图（Xbar-R 图或 I-MR 图）
    
    Args:
        data: 数据列表
        subgroup_size: 子组大小
        chart_type: 控制图类型 ("Xbar-R", "I-MR")
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        (主图 base64, 范围图 base64) 或 (单图 base64, None)
    """
    data_array = np.array(data)
    
    if chart_type == "I-MR" or subgroup_size == 1:
        # I-MR 图（单值 - 移动极差图）
        return generate_imr_chart(data_array, title, dpi)
    else:
        # Xbar-R 图
        return generate_xbar_r_chart(data_array, subgroup_size, title, dpi)


def generate_imr_chart(
    data: np.ndarray,
    title: Optional[str] = None,
    dpi: int = 150
) -> Tuple[str, Optional[str]]:
    """生成 I-MR 控制图"""
    
    if title is None:
        title = "I-MR Control Chart"
    
    # 计算移动极差
    moving_range = np.abs(np.diff(data))
    mr_bar = np.mean(moving_range)
    
    # 计算 I 图的控制限
    x_bar = np.mean(data)
    d2 = 1.128  # n=2 时的常数
    e2 = 2.66   # n=2 时的常数
    
    ucl_i = x_bar + e2 * mr_bar / d2
    lcl_i = x_bar - e2 * mr_bar / d2
    
    # 计算 MR 图的控制限
    d3 = 0.853
    d4 = 3.267
    
    ucl_mr = d4 * mr_bar / d2
    lcl_mr = max(0, d3 * mr_bar / d2)
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=dpi, sharex=True)
    
    # I 图
    x = range(1, len(data) + 1)
    ax1.plot(x, data, 'b-o', markersize=4, linewidth=1.5, label='Individual Value')
    ax1.axhline(y=x_bar, color='green', linestyle='-', linewidth=2, label=f'CL = {x_bar:.4f}')
    ax1.axhline(y=ucl_i, color='red', linestyle='--', linewidth=2, label=f'UCL = {ucl_i:.4f}')
    ax1.axhline(y=lcl_i, color='red', linestyle='--', linewidth=2, label=f'LCL = {lcl_i:.4f}')
    ax1.set_ylabel('Value', fontsize=9)
    ax1.set_title(title, fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # MR 图
    mr_x = range(2, len(data) + 1)
    ax2.plot(mr_x, moving_range, 'b-o', markersize=4, linewidth=1.5, label='Moving Range')
    ax2.axhline(y=mr_bar, color='green', linestyle='-', linewidth=2, label=f'CL = {mr_bar:.4f}')
    ax2.axhline(y=ucl_mr, color='red', linestyle='--', linewidth=2, label=f'UCL = {ucl_mr:.4f}')
    if lcl_mr > 0:
        ax2.axhline(y=lcl_mr, color='red', linestyle='--', linewidth=2, label=f'LCL = {lcl_mr:.4f}')
    ax2.set_xlabel('Sample Number', fontsize=9)
    ax2.set_ylabel('Moving Range', fontsize=9)
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}", None


def generate_xbar_r_chart(
    data: np.ndarray,
    subgroup_size: int,
    title: Optional[str] = None,
    dpi: int = 150
) -> Tuple[str, Optional[str]]:
    """生成 Xbar-R 控制图"""
    
    if title is None:
        title = "Xbar-R Control Chart"
    
    # 分组
    n_groups = len(data) // subgroup_size
    if n_groups == 0:
        # 数据不足，返回 I-MR 图
        return generate_imr_chart(data, title, dpi)
    
    data_trimmed = data[:n_groups * subgroup_size]
    subgroups = data_trimmed.reshape(n_groups, subgroup_size)
    
    # 计算每组的均值和极差
    xbar = np.mean(subgroups, axis=1)
    r = np.ptp(subgroups, axis=1)  # 极差 = max - min
    
    xbar_bar = np.mean(xbar)
    r_bar = np.mean(r)
    
    # 控制图常数（根据子组大小）
    A2_table = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 
                7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
    D3_table = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 
                8: 0.136, 9: 0.184, 10: 0.223}
    D4_table = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 
                7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
    
    A2 = A2_table.get(subgroup_size, 0.577)
    D3 = D3_table.get(subgroup_size, 0)
    D4 = D4_table.get(subgroup_size, 2.114)
    
    # Xbar 图控制限
    ucl_xbar = xbar_bar + A2 * r_bar
    lcl_xbar = xbar_bar - A2 * r_bar
    
    # R 图控制限
    ucl_r = D4 * r_bar
    lcl_r = D3 * r_bar
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=dpi, sharex=True)
    
    # Xbar 图
    x = range(1, n_groups + 1)
    ax1.plot(x, xbar, 'b-o', markersize=4, linewidth=1.5, label='X̄')
    ax1.axhline(y=xbar_bar, color='green', linestyle='-', linewidth=2, label=f'CL = {xbar_bar:.4f}')
    ax1.axhline(y=ucl_xbar, color='red', linestyle='--', linewidth=2, label=f'UCL = {ucl_xbar:.4f}')
    ax1.axhline(y=lcl_xbar, color='red', linestyle='--', linewidth=2, label=f'LCL = {lcl_xbar:.4f}')
    ax1.set_ylabel('X̄', fontsize=9)
    ax1.set_title(title, fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # R 图
    ax2.plot(x, r, 'b-o', markersize=4, linewidth=1.5, label='R')
    ax2.axhline(y=r_bar, color='green', linestyle='-', linewidth=2, label=f'CL = {r_bar:.4f}')
    ax2.axhline(y=ucl_r, color='red', linestyle='--', linewidth=2, label=f'UCL = {ucl_r:.4f}')
    if lcl_r > 0:
        ax2.axhline(y=lcl_r, color='red', linestyle='--', linewidth=2, label=f'LCL = {lcl_r:.4f}')
    ax2.set_xlabel('Subgroup', fontsize=9)
    ax2.set_ylabel('Range', fontsize=9)
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}", None


def generate_all_charts_for_report(
    data: List[float],
    mean: float,
    std: float,
    usl: Optional[float] = None,
    lsl: Optional[float] = None,
    subgroup_size: int = 1,
    dpi: int = 150
) -> dict:
    """
    为 SPC 报告生成所有图表
    
    Args:
        data: 数据列表
        mean: 均值
        std: 标准差
        usl: 规格上限
        lsl: 规格下限
        subgroup_size: 子组大小
        dpi: 分辨率
    
    Returns:
        包含所有图表 base64 字符串的字典
    """
    # 1. 直方图
    histogram_img = generate_histogram_plot(data, mean, std, usl, lsl, 
                                           "Histogram with Normal Fit", dpi)
    
    # 2. 运行图
    run_chart_img = generate_run_chart(data, mean, title="Run Chart", dpi=dpi)
    
    # 3. 概率图
    probability_plot_img = generate_probability_plot(data, 
                                                     "Normal Probability Plot", 
                                                     dpi)
    
    # 4. 控制图
    control_chart_img, _ = generate_control_chart(data, subgroup_size, 
                                                   "Control Chart for Stability", 
                                                   dpi)
    
    return {
        'histogram_img': histogram_img,
        'run_chart_img': run_chart_img,
        'probability_plot_img': probability_plot_img,
        'control_chart_img': control_chart_img
    }


# ============================================================================
# 偏态分布图表生成函数
# ============================================================================

def generate_skewed_histogram(
    data: List[float],
    dist_type: str = 'weibull',
    title: str = "Skewed Distribution Histogram",
    dpi: int = 150
) -> str:
    """
    生成偏态分布直方图
    
    Args:
        data: 数据列表
        dist_type: 分布类型 ('weibull', 'lognormal')
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=dpi)
    
    # 绘制直方图
    n, bins, patches = ax.hist(data, bins='auto', density=True, 
                               alpha=0.7, color='steelblue', 
                               edgecolor='black', linewidth=0.5)
    
    # 根据偏态类型拟合分布
    data_array = np.array(data)
    x = np.linspace(min(data), max(data), 100)
    
    if dist_type == 'weibull':
        # Weibull 分布拟合
        shape, loc, scale = stats.weibull_min.fit(data_array)
        y = stats.weibull_min.pdf(x, shape, loc, scale)
        ax.plot(x, y, 'r-', linewidth=2, label=f'Weibull Fit (shape={shape:.3f})')
    elif dist_type == 'lognormal':
        # 对数正态分布拟合
        shape, loc, scale = stats.lognorm.fit(data_array)
        y = stats.lognorm.pdf(x, shape, loc, scale)
        ax.plot(x, y, 'r-', linewidth=2, label=f'Lognormal Fit (shape={shape:.3f})')
    
    # 添加中位数线
    median = np.median(data)
    ax.axvline(x=median, color='green', linestyle='-', linewidth=1.5, label=f'Median = {median:.4f}')
    
    # 添加均值线
    mean = np.mean(data)
    ax.axvline(x=mean, color='orange', linestyle='--', linewidth=1.5, label=f'Mean = {mean:.4f}')
    
    ax.set_xlabel('Value', fontsize=10)
    ax.set_ylabel('Density', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_weibull_probability_plot(
    data: List[float],
    title: str = "Weibull Probability Plot",
    dpi: int = 150
) -> str:
    """
    生成 Weibull 概率图
    
    Args:
        data: 数据列表
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    
    # Weibull 分布拟合
    data_array = np.array(data)
    shape, loc, scale = stats.weibull_min.fit(data_array)
    
    # 排序数据
    sorted_data = np.sort(data_array)
    n = len(sorted_data)
    
    # 计算经验概率
    ranks = np.arange(1, n + 1)
    empirical_prob = (ranks - 0.3) / (n + 0.4)
    
    # Weibull 变换
    weibull_y = np.log(-np.log(1 - empirical_prob))
    weibull_x = np.log(sorted_data - loc)
    
    # 绘制散点
    ax.scatter(weibull_x, weibull_y, s=20, alpha=0.6, color='blue', label='Data')
    
    # 拟合直线
    z = np.polyfit(weibull_x, weibull_y, 1)
    p = np.poly1d(z)
    ax.plot(weibull_x, p(weibull_x), "r-", linewidth=2, label=f'Fit (shape={shape:.3f})')
    
    ax.set_xlabel('ln(Value)', fontsize=10)
    ax.set_ylabel('ln(-ln(1-F))', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_lognormal_probability_plot(
    data: List[float],
    title: str = "Lognormal Probability Plot",
    dpi: int = 150
) -> str:
    """
    生成对数正态概率图
    
    Args:
        data: 数据列表
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    
    # 对数变换
    log_data = np.log(data)
    
    # 创建 Q-Q 图
    stats.probplot(log_data, dist="norm", plot=ax)
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('ln(Value)', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_all_charts_for_skewed_distribution(
    data: List[float],
    dist_type: str = 'weibull',
    subgroup_size: int = 1,
    dpi: int = 150
) -> dict:
    """
    为偏态分布报告生成所有图表
    
    Args:
        data: 数据列表
        dist_type: 分布类型 ('weibull', 'lognormal')
        subgroup_size: 子组大小
        dpi: 分辨率
    
    Returns:
        包含所有图表 base64 字符串的字典
    """
    # 1. 偏态直方图
    histogram_img = generate_skewed_histogram(data, dist_type, 
                                             f"Skewed Histogram ({dist_type.capitalize()})", dpi)
    
    # 2. 运行图
    run_chart_img = generate_run_chart(data, np.mean(data), title="Run Chart", dpi=dpi)
    
    # 3. 概率图（根据分布类型选择）
    if dist_type == 'weibull':
        probability_plot_img = generate_weibull_probability_plot(data, "Weibull Probability Plot", dpi)
    else:
        probability_plot_img = generate_lognormal_probability_plot(data, "Lognormal Probability Plot", dpi)
    
    # 4. 控制图
    control_chart_img, _ = generate_control_chart(data, subgroup_size, 
                                                   "Control Chart", dpi)
    
    return {
        'histogram_img': histogram_img,
        'run_chart_img': run_chart_img,
        'probability_plot_img': probability_plot_img,
        'control_chart_img': control_chart_img
    }


# ============================================================================
# 混合分布图表生成函数
# ============================================================================

def generate_multi_modal_histogram(
    data: List[float],
    groups: Optional[Dict[str, List[float]]] = None,
    title: str = "Multi-Modal Distribution Histogram",
    dpi: int = 150
) -> str:
    """
    生成多峰分布直方图（支持分组显示）
    
    Args:
        data: 数据列表
        groups: 分组数据 dict, {group_name: data_list}
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(8, 5), dpi=dpi)
    
    if groups:
        # 分组显示
        colors = ['steelblue', 'coral', 'green', 'purple', 'orange']
        for i, (group_name, group_data) in enumerate(groups.items()):
            ax.hist(group_data, bins='auto', density=True, 
                   alpha=0.5, color=colors[i % len(colors)],
                   edgecolor='black', linewidth=0.5,
                   label=group_name)
    else:
        # 整体显示
        ax.hist(data, bins='auto', density=True, 
               alpha=0.7, color='steelblue', 
               edgecolor='black', linewidth=0.5)
    
    # 添加总体均值线
    mean = np.mean(data)
    ax.axvline(x=mean, color='red', linestyle='--', linewidth=1.5, label=f'Overall Mean = {mean:.4f}')
    
    # 如果有分组，添加各组均值线
    if groups:
        for i, (group_name, group_data) in enumerate(groups.items()):
            group_mean = np.mean(group_data)
            ax.axvline(x=group_mean, color=colors[i % len(colors)], 
                      linestyle='-', linewidth=1.5, label=f'{group_name} Mean = {group_mean:.4f}')
    
    ax.set_xlabel('Value', fontsize=10)
    ax.set_ylabel('Density', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_box_plot_comparison(
    data_dict: Dict[str, List[float]],
    title: str = "Box Plot Comparison",
    dpi: int = 150
) -> str:
    """
    生成箱线图比较图
    
    Args:
        data_dict: 分组数据 dict, {group_name: data_list}
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=dpi)
    
    # 准备数据
    labels = list(data_dict.keys())
    data_to_plot = [data_dict[label] for label in labels]
    
    # 绘制箱线图
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                   notch=True, showmeans=True)
    
    # 设置颜色
    colors = ['steelblue', 'coral', 'green', 'purple', 'orange']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax.set_xlabel('Group', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_stratified_run_chart(
    data: List[float],
    groups: Optional[List[str]] = None,
    title: str = "Stratified Run Chart",
    dpi: int = 150
) -> str:
    """
    生成分层运行图
    
    Args:
        data: 数据列表
        groups: 分组标签列表（与 data 等长）
        title: 图表标题
        dpi: 分辨率
    
    Returns:
        base64 编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(10, 5), dpi=dpi)
    
    data_array = np.array(data)
    
    if groups and len(groups) == len(data):
        # 按组分层显示
        unique_groups = list(set(groups))
        colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown']
        
        for i, group_name in enumerate(unique_groups):
            indices = [j for j, g in enumerate(groups) if g == group_name]
            group_data = data_array[indices]
            x_vals = np.array(indices) + 1
            
            ax.scatter(x_vals, group_data, c=colors[i % len(colors)], 
                      label=group_name, alpha=0.6, s=30)
            ax.plot(x_vals, group_data, c=colors[i % len(colors)], 
                   linewidth=1, alpha=0.4)
    else:
        # 不分组，显示所有数据
        x = range(1, len(data) + 1)
        ax.plot(x, data, 'b-o', markersize=4, linewidth=1.5, label='Data')
    
    # 添加总均值线
    mean = np.mean(data)
    ax.axhline(y=mean, color='gray', linestyle='--', linewidth=2, label=f'Overall Mean = {mean:.4f}')
    
    ax.set_xlabel('Sample Number', fontsize=10)
    ax.set_ylabel('Value', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 转换为 base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"


def generate_all_charts_for_mixed_distribution(
    data: List[float],
    groups: Optional[Dict[str, List[float]]] = None,
    group_labels: Optional[List[str]] = None,
    subgroup_size: int = 1,
    dpi: int = 150
) -> dict:
    """
    为混合分布报告生成所有图表
    
    Args:
        data: 数据列表
        groups: 分组数据 dict, {group_name: data_list}
        group_labels: 分组标签列表
        subgroup_size: 子组大小
        dpi: 分辨率
    
    Returns:
        包含所有图表 base64 字符串的字典
    """
    # 1. 多峰直方图
    if groups:
        histogram_img = generate_multi_modal_histogram(data, groups, 
                                                       "Multi-Modal Histogram", dpi)
    else:
        histogram_img = generate_multi_modal_histogram(data, None, 
                                                       "Multi-Modal Histogram", dpi)
    
    # 2. 分层运行图
    if groups and group_labels:
        # 构建分层标签
        stratified_data = []
        stratified_labels = []
        for group_name, group_data in groups.items():
            stratified_data.extend(group_data)
            stratified_labels.extend([group_name] * len(group_data))
        run_chart_img = generate_stratified_run_chart(stratified_data, stratified_labels,
                                                      "Stratified Run Chart", dpi)
    else:
        run_chart_img = generate_run_chart(data, np.mean(data), title="Run Chart", dpi=dpi)
    
    # 3. 箱线图比较
    if groups:
        box_plot_img = generate_box_plot_comparison(groups, "Box Plot Comparison", dpi)
    else:
        # 如果没有分组，生成一个默认箱线图
        box_plot_img = generate_box_plot_comparison({'All Data': data}, 
                                                    "Box Plot", dpi)
    
    # 4. 控制图
    control_chart_img, _ = generate_control_chart(data, subgroup_size, 
                                                   "Control Chart", dpi)
    
    return {
        'histogram_img': histogram_img,
        'run_chart_img': run_chart_img,
        'box_plot_img': box_plot_img,
        'control_chart_img': control_chart_img
    }
