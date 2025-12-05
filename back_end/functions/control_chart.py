import math
from typing import List, Dict, Tuple


def calculate_u_i(c_i: int, n_i: float) -> float:
    """
    计算单位缺陷数
    
    Args:
        c_i: 第i个样本的总缺陷数
        n_i: 第i个样本的检验单位大小
    
    Returns:
        单位缺陷数u_i
    """
    if n_i <= 0:
        raise ValueError("样本大小n_i必须大于0")
    return c_i / n_i


def calculate_mean_u(c_list: List[int], n_list: List[float]) -> float:
    """
    计算总平均单位缺陷数
    
    Args:
        c_list: 各样本的缺陷数列表
        n_list: 各样本的检验单位大小列表
    
    Returns:
        总平均单位缺陷数u_bar
    """
    if len(c_list) != len(n_list):
        raise ValueError("c_list和n_list长度必须一致")
    if len(c_list) == 0:
        raise ValueError("样本数量不能为0")
    
    total_c = sum(c_list)
    total_n = sum(n_list)
    
    if total_n <= 0:
        raise ValueError("总检验单位大小必须大于0")
    
    return total_c / total_n


def calculate_control_limits(u_bar: float, n_list: List[float]) -> Tuple[List[float], List[float]]:
    """
    计算每个样本的控制限（一般计算公式）
    
    Args:
        u_bar: 总平均单位缺陷数
        n_list: 各样本的检验单位大小列表
    
    Returns:
        (UCL列表, LCL列表)
    """
    ucl_list = []
    lcl_list = []
    
    for n_i in n_list:
        if n_i <= 0:
            raise ValueError("样本大小n_i必须大于0")
        
        sigma = math.sqrt(u_bar / n_i)
        ucl = u_bar + 3 * sigma
        lcl = u_bar - 3 * sigma
        
        ucl_list.append(ucl)
        lcl_list.append(max(0, lcl))  # LCL不能为负数
    
    return ucl_list, lcl_list


def calculate_approximate_control_limits(u_bar: float, n_list: List[float]) -> Tuple[float, float]:
    """
    计算近似控制限（当所有n_i相近时使用）
    
    Args:
        u_bar: 总平均单位缺陷数
        n_list: 各样本的检验单位大小列表
    
    Returns:
        (近似UCL, 近似LCL)
    """
    if len(n_list) == 0:
        raise ValueError("样本数量不能为0")
    
    mean_n = sum(n_list) / len(n_list)
    
    if mean_n <= 0:
        raise ValueError("平均样本大小必须大于0")
    
    sigma = math.sqrt(u_bar / mean_n)
    ucl = u_bar + 3 * sigma
    lcl = u_bar - 3 * sigma
    
    return ucl, max(0, lcl)


def check_rule_1(u_list: List[float], ucl_list: List[float]) -> List[int]:
    """
    规则1：1点外（点落在A区以外，即超过UCL或低于LCL）
    
    Args:
        u_list: 单位缺陷数列表
        ucl_list: 上控制限列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    for i, (u_i, ucl) in enumerate(zip(u_list, ucl_list)):
        if u_i > ucl:
            abnormal_indices.append(i)
    return abnormal_indices


def check_rule_2(u_list: List[float], center_line: float) -> List[int]:
    """
    规则2：9单侧（连续9个点落在中心线同一侧）
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 8):
        window = u_list[i:i+9]
        above_center = all(u > center_line for u in window)
        below_center = all(u < center_line for u in window)
        
        if above_center or below_center:
            for j in range(i, i+9):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def check_rule_3(u_list: List[float]) -> List[int]:
    """
    规则3：6连串（连续6个点递增或递减）
    
    Args:
        u_list: 单位缺陷数列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 5):
        increasing = True
        decreasing = True
        
        for j in range(i, i+5):
            if u_list[j] >= u_list[j+1]:
                increasing = False
            if u_list[j] <= u_list[j+1]:
                decreasing = False
        
        if increasing or decreasing:
            for j in range(i, i+6):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def check_rule_4(u_list: List[float]) -> List[int]:
    """
    规则4：14交替（连续14个点中相邻点交替上下）
    
    Args:
        u_list: 单位缺陷数列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 13):
        alternating = True
        
        for j in range(i, i+13):
            if j+2 < len(u_list):
                if (u_list[j] < u_list[j+1] and u_list[j+1] <= u_list[j+2]) or \
                   (u_list[j] > u_list[j+1] and u_list[j+1] >= u_list[j+2]) or \
                   (u_list[j] == u_list[j+1] and u_list[j+1] == u_list[j+2]):
                    alternating = False
                    break
        
        if alternating:
            for j in range(i, i+14):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def get_zones(u: float, center_line: float, ucl: float, lcl: float) -> Dict[str, bool]:
    """
    确定点落在控制图的哪个区域（A区、B区、C区）
    
    Args:
        u: 单位缺陷数
        center_line: 中心线值
        ucl: 上控制限
        lcl: 下控制限
    
    Returns:
        字典，包含点在各区域的布尔值
    """
    # 计算各区域边界
    distance = ucl - center_line
    zone_a_lower = center_line + (distance * 2/3)
    zone_b_lower = center_line + (distance * 1/3)
    zone_b_upper = center_line - (distance * 1/3)
    zone_a_upper = center_line - (distance * 2/3)
    
    zones = {
        'above_a': u > ucl,
        'above_b': zone_a_lower < u <= ucl,
        'above_c': zone_b_lower < u <= zone_a_lower,
        'below_c': zone_b_upper < u <= zone_b_lower,
        'below_b': zone_a_upper < u <= zone_b_upper,
        'below_a': u <= zone_a_upper
    }
    
    return zones

def check_rule_5(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    """
    规则5：2/3A（连续3个点中有2个点落在中心线同一侧的B区以外）
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
        ucl_list: 上控制限列表
        lcl_list: 下控制限列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 2):
        # 获取连续3个点的区域信息
        zones_above = 0
        zones_below = 0
        
        for j in range(i, i+3):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            if zones['above_a'] or zones['above_b']:
                zones_above += 1
            elif zones['below_a'] or zones['below_b']:
                zones_below += 1
        
        # 检查是否有2个点在同一侧的B区以外
        if zones_above >= 2 or zones_below >= 2:
            for j in range(i, i+3):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)

def check_rule_6(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    """
    规则6：4/5C（连续5个点中有4个点落在中心线同一侧的C区以外）
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
        ucl_list: 上控制限列表
        lcl_list: 下控制限列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 4):
        # 获取连续5个点的区域信息
        zones_above = 0  # 上侧C区以外的点数
        zones_below = 0  # 下侧C区以外的点数
        
        for j in range(i, i+5):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            # 只计算C区以外的点（即A区和B区）
            if zones['above_a'] or zones['above_b']:
                zones_above += 1
            elif zones['below_a'] or zones['below_b']:
                zones_below += 1
        
        # 检查是否有4个点在同一侧的C区以外
        if zones_above >= 4 or zones_below >= 4:
            for j in range(i, i+5):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)

def check_rule_7(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    """
    规则7：15全C（连续15个点落在中心线两侧的C区内）
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
        ucl_list: 上控制限列表
        lcl_list: 下控制限列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 14):
        all_in_c = True
        
        for j in range(i, i+15):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            if not (zones['above_c'] or zones['below_c']):
                all_in_c = False
                break
        
        if all_in_c:
            for j in range(i, i+15):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)

def check_rule_8(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    """
    规则8：8缺C（连续8个点落在中心线两侧且无一在C区内）
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
        ucl_list: 上控制限列表
        lcl_list: 下控制限列表
    
    Returns:
        异常点的索引列表
    """
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 7):
        # 检查是否有上下交替
        has_above = False
        has_below = False
        all_outside_c = True
        
        for j in range(i, i+8):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            # 检查是否在C区内
            if zones['above_c'] or zones['below_c']:
                all_outside_c = False
                break
            # 检查是否有上下交替
            if zones['above_a'] or zones['above_b']:
                has_above = True
            elif zones['below_a'] or zones['below_b']:
                has_below = True
        
        # 检查是否有上下交替且无点在C区内
        if has_above and has_below and all_outside_c:
            for j in range(i, i+8):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)

def check_all_rules(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> Dict[int, List[int]]:
    """
    检查所有8大异常规则
    
    Args:
        u_list: 单位缺陷数列表
        center_line: 中心线值（u_bar）
        ucl_list: 上控制限列表
        lcl_list: 下控制限列表
    
    Returns:
        字典，键为异常规则编号，值为该规则检测到的异常点索引列表
    """
    rules = {}
    
    # 规则1：1点外
    rules[1] = check_rule_1(u_list, ucl_list)
    
    # 规则2：9单侧
    rules[2] = check_rule_2(u_list, center_line)
    
    # 规则3：6连串
    rules[3] = check_rule_3(u_list)
    
    # 规则4：14交替
    rules[4] = check_rule_4(u_list)
    
    # 规则5：2/3A
    rules[5] = check_rule_5(u_list, center_line, ucl_list, lcl_list)
    
    # 规则6：4/5C
    rules[6] = check_rule_6(u_list, center_line, ucl_list, lcl_list)
    
    # 规则7：15全C
    rules[7] = check_rule_7(u_list, center_line, ucl_list, lcl_list)
    
    # 规则8：8缺C
    rules[8] = check_rule_8(u_list, center_line, ucl_list, lcl_list)
    
    return rules


def generate_control_chart_data(c_list: List[int], n_list: List[float]) -> Dict:
    """
    生成控制图所需的所有数据，包含完整的异常检测结果
    
    Args:
        c_list: 各样本的缺陷数列表
        n_list: 各样本的检验单位大小列表
    
    Returns:
        控制图数据字典，包含所有8个异常规则的检测结果
    """
    # 计算单位缺陷数
    u_list = [calculate_u_i(c, n) for c, n in zip(c_list, n_list)]
    
    # 计算总平均单位缺陷数
    u_bar = calculate_mean_u(c_list, n_list)
    
    # 计算控制限
    ucl_list, lcl_list = calculate_control_limits(u_bar, n_list)
    
    # 计算近似控制限
    approx_ucl, approx_lcl = calculate_approximate_control_limits(u_bar, n_list)
    
    # 检查所有8个异常规则
    abnormal_rules = check_all_rules(u_list, u_bar, ucl_list, lcl_list)
    
    # 汇总异常点
    abnormal_points = set()
    for indices in abnormal_rules.values():
        abnormal_points.update(indices)
    abnormal_points = sorted(abnormal_points)
    
    # 计算统计信息
    total_samples = len(c_list)
    total_defects = sum(c_list)
    
    return {
        'u_list': u_list,
        'c_list': c_list,
        'n_list': n_list,
        'center_line': u_bar,
        'ucl_list': ucl_list,
        'lcl_list': lcl_list,
        'approx_ucl': approx_ucl,
        'approx_lcl': approx_lcl,
        'abnormal_rules': abnormal_rules,
        'abnormal_points': abnormal_points,
        'statistics': {
            'total_samples': total_samples,
            'total_defects': total_defects,
            'mean_defects_per_sample': total_defects / total_samples if total_samples > 0 else 0,
            'mean_u': u_bar,
            'total_abnormal_count': len(abnormal_points)
        },
        'message': '控制图数据生成成功，包含完整的8大异常规则检测结果'
    }


if __name__ == "__main__":
    # 示例用法
    c_list = [5, 3, 7, 4, 6, 2, 8, 5, 3, 6]
    n_list = [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]  # 假设每个样本都是3张PCB
    
    try:
        result = generate_control_chart_data(c_list, n_list)
        print(f"总平均单位缺陷数: {result['center_line']:.4f}")
        print(f"单位缺陷数列表: {[round(u, 4) for u in result['u_list']]}")
        print(f"控制限列表: UCL={[round(ucl, 4) for ucl in result['ucl_list']]}")
        print(f"异常点索引: {result['abnormal_points']}")
        print(f"各规则异常点: {result['abnormal_rules']}")
    except Exception as e:
        print(f"计算错误: {e}")