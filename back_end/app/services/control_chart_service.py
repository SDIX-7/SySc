import math
from typing import List, Dict, Tuple, Optional


D3_TABLE = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223, 11: 0.256, 12: 0.283, 13: 0.307, 14: 0.328, 15: 0.347, 16: 0.363, 17: 0.378, 18: 0.391, 19: 0.403, 20: 0.415, 21: 0.425, 22: 0.434, 23: 0.443, 24: 0.451, 25: 0.459}
D4_TABLE = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777, 11: 1.744, 12: 1.717, 13: 1.693, 14: 1.672, 15: 1.653, 16: 1.637, 17: 1.622, 18: 1.608, 19: 1.597, 20: 1.585, 21: 1.575, 22: 1.566, 23: 1.557, 24: 1.548, 25: 1.541}
A2_TABLE = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308, 11: 0.285, 12: 0.266, 13: 0.249, 14: 0.235, 15: 0.223, 16: 0.212, 17: 0.203, 18: 0.194, 19: 0.187, 20: 0.180, 21: 0.173, 22: 0.167, 23: 0.162, 24: 0.157, 25: 0.153}
A3_TABLE = {2: 2.659, 3: 1.954, 4: 1.628, 5: 1.427, 6: 1.287, 7: 1.182, 8: 1.099, 9: 1.032, 10: 0.975, 11: 0.927, 12: 0.886, 13: 0.850, 14: 0.817, 15: 0.789, 16: 0.763, 17: 0.739, 18: 0.718, 19: 0.698, 20: 0.680, 21: 0.663, 22: 0.647, 23: 0.633, 24: 0.619, 25: 0.606}
B3_TABLE = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0.030, 7: 0.118, 8: 0.185, 9: 0.239, 10: 0.284, 11: 0.321, 12: 0.354, 13: 0.382, 14: 0.406, 15: 0.428, 16: 0.448, 17: 0.466, 18: 0.482, 19: 0.497, 20: 0.510, 21: 0.523, 22: 0.534, 23: 0.545, 24: 0.555, 25: 0.565}
B4_TABLE = {2: 3.267, 3: 2.568, 4: 2.266, 5: 2.089, 6: 1.970, 7: 1.882, 8: 1.815, 9: 1.761, 10: 1.716, 11: 1.679, 12: 1.646, 13: 1.618, 14: 1.594, 15: 1.572, 16: 1.552, 17: 1.534, 18: 1.518, 19: 1.503, 20: 1.490, 21: 1.477, 22: 1.466, 23: 1.455, 24: 1.445, 25: 1.435}
C4_TABLE = {2: 0.7979, 3: 0.8862, 4: 0.9213, 5: 0.9400, 6: 0.9515, 7: 0.9594, 8: 0.9650, 9: 0.9693, 10: 0.9727, 11: 0.9754, 12: 0.9776, 13: 0.9794, 14: 0.9810, 15: 0.9823, 16: 0.9835, 17: 0.9845, 18: 0.9854, 19: 0.9862, 20: 0.9869, 21: 0.9876, 22: 0.9882, 23: 0.9887, 24: 0.9892, 25: 0.9896}


def get_coefficient(table: Dict[int, float], n: int) -> float:
    if n in table:
        return table[n]
    if n < 2:
        return table[2]
    return table[25]


def calculate_u_i(c_i: int, n_i: float) -> float:
    if n_i <= 0:
        raise ValueError("样本大小n_i必须大于0")
    return c_i / n_i


def calculate_mean_u(c_list: List[int], n_list: List[float]) -> float:
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
    ucl_list = []
    lcl_list = []
    
    for n_i in n_list:
        if n_i <= 0:
            raise ValueError("样本大小n_i必须大于0")
        
        sigma = math.sqrt(u_bar / n_i)
        ucl = u_bar + 3 * sigma
        lcl = u_bar - 3 * sigma
        
        ucl_list.append(ucl)
        lcl_list.append(max(0, lcl))
    
    return ucl_list, lcl_list


def calculate_approximate_control_limits(u_bar: float, n_list: List[float]) -> Tuple[float, float]:
    if len(n_list) == 0:
        raise ValueError("样本数量不能为0")
    
    mean_n = sum(n_list) / len(n_list)
    
    if mean_n <= 0:
        raise ValueError("平均样本大小必须大于0")
    
    sigma = math.sqrt(u_bar / mean_n)
    ucl = u_bar + 3 * sigma
    lcl = u_bar - 3 * sigma
    
    return ucl, max(0, lcl)


def calculate_range(values: List[float]) -> float:
    if not values:
        return 0.0
    return max(values) - min(values)


def calculate_std_dev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def calculate_xbar_r_chart(data_groups: List[List[float]], subgroup_size: Optional[int] = None) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    x_bar_list = []
    r_list = []
    n_list = []
    
    for group in data_groups:
        if not group:
            continue
        n = len(group)
        n_list.append(n)
        x_bar = sum(group) / n
        r = calculate_range(group)
        x_bar_list.append(x_bar)
        r_list.append(r)
    
    if not x_bar_list:
        raise ValueError("没有有效的数据组")
    
    k = len(x_bar_list)
    x_double_bar = sum(x_bar_list) / k
    r_bar = sum(r_list) / k
    
    avg_n = sum(n_list) / len(n_list) if n_list else 0
    n = subgroup_size if subgroup_size else round(avg_n)
    n = max(2, min(25, n))
    
    A2 = get_coefficient(A2_TABLE, n)
    D3 = get_coefficient(D3_TABLE, n)
    D4 = get_coefficient(D4_TABLE, n)
    
    xbar_ucl = x_double_bar + A2 * r_bar
    xbar_lcl = x_double_bar - A2 * r_bar
    xbar_cl = x_double_bar
    
    r_ucl = D4 * r_bar
    r_lcl = D3 * r_bar
    r_cl = r_bar
    
    xbar_abnormal = check_all_rules_for_values(x_bar_list, xbar_cl, xbar_ucl, xbar_lcl)
    r_abnormal = check_all_rules_for_values(r_list, r_cl, r_ucl, r_lcl)
    
    xbar_abnormal_points = set()
    for indices in xbar_abnormal.values():
        xbar_abnormal_points.update(indices)
    
    r_abnormal_points = set()
    for indices in r_abnormal.values():
        r_abnormal_points.update(indices)
    
    return {
        'chart_type': 'X-R',
        'xbar_chart': {
            'data_points': x_bar_list,
            'center_line': xbar_cl,
            'ucl': xbar_ucl,
            'lcl': max(0, xbar_lcl),
            'abnormal_points': sorted(xbar_abnormal_points),
            'abnormal_rules': xbar_abnormal
        },
        'r_chart': {
            'data_points': r_list,
            'center_line': r_cl,
            'ucl': r_ucl,
            'lcl': max(0, r_lcl),
            'abnormal_points': sorted(r_abnormal_points),
            'abnormal_rules': r_abnormal
        },
        'statistics': {
            'total_groups': k,
            'subgroup_size': n,
            'grand_mean': x_double_bar,
            'avg_range': r_bar,
            'coefficients': {'A2': A2, 'D3': D3, 'D4': D4},
            'process_sigma_estimate': r_bar / get_coefficient(D4_TABLE, n) * (get_coefficient(D4_TABLE, n) - 1) / 3 if r_bar > 0 else 0
        },
        'parameters': {
            'subgroup_size': n,
            'control_limit_coefficients': {'A2': A2, 'D3': D3, 'D4': D4}
        },
        'message': 'X-R控制图数据生成成功'
    }


def calculate_xbar_s_chart(data_groups: List[List[float]], subgroup_size: Optional[int] = None) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    x_bar_list = []
    s_list = []
    n_list = []
    
    for group in data_groups:
        if not group:
            continue
        n = len(group)
        n_list.append(n)
        x_bar = sum(group) / n
        s = calculate_std_dev(group)
        x_bar_list.append(x_bar)
        s_list.append(s)
    
    if not x_bar_list:
        raise ValueError("没有有效的数据组")
    
    k = len(x_bar_list)
    x_double_bar = sum(x_bar_list) / k
    s_bar = sum(s_list) / k
    
    avg_n = sum(n_list) / len(n_list) if n_list else 0
    n = subgroup_size if subgroup_size else round(avg_n)
    n = max(2, min(25, n))
    
    A3 = get_coefficient(A3_TABLE, n)
    B3 = get_coefficient(B3_TABLE, n)
    B4 = get_coefficient(B4_TABLE, n)
    c4 = get_coefficient(C4_TABLE, n)
    
    xbar_ucl = x_double_bar + A3 * s_bar
    xbar_lcl = x_double_bar - A3 * s_bar
    xbar_cl = x_double_bar
    
    s_ucl = B4 * s_bar
    s_lcl = B3 * s_bar
    s_cl = s_bar
    
    xbar_abnormal = check_all_rules_for_values(x_bar_list, xbar_cl, xbar_ucl, xbar_lcl)
    s_abnormal = check_all_rules_for_values(s_list, s_cl, s_ucl, s_lcl)
    
    xbar_abnormal_points = set()
    for indices in xbar_abnormal.values():
        xbar_abnormal_points.update(indices)
    
    s_abnormal_points = set()
    for indices in s_abnormal.values():
        s_abnormal_points.update(indices)
    
    process_sigma = s_bar / c4 if c4 > 0 else 0
    
    return {
        'chart_type': 'X-s',
        'xbar_chart': {
            'data_points': x_bar_list,
            'center_line': xbar_cl,
            'ucl': xbar_ucl,
            'lcl': max(0, xbar_lcl),
            'abnormal_points': sorted(xbar_abnormal_points),
            'abnormal_rules': xbar_abnormal
        },
        's_chart': {
            'data_points': s_list,
            'center_line': s_cl,
            'ucl': s_ucl,
            'lcl': max(0, s_lcl),
            'abnormal_points': sorted(s_abnormal_points),
            'abnormal_rules': s_abnormal
        },
        'statistics': {
            'total_groups': k,
            'subgroup_size': n,
            'grand_mean': x_double_bar,
            'avg_std_dev': s_bar,
            'coefficients': {'A3': A3, 'B3': B3, 'B4': B4, 'c4': c4},
            'process_sigma_estimate': process_sigma
        },
        'parameters': {
            'subgroup_size': n,
            'control_limit_coefficients': {'A3': A3, 'B3': B3, 'B4': B4, 'c4': c4}
        },
        'message': 'X-s控制图数据生成成功'
    }


def check_all_rules_for_values(value_list: List[float], center_line: float, ucl: float, lcl: float) -> Dict[int, List[int]]:
    ucl_list = [ucl] * len(value_list)
    lcl_list = [lcl] * len(value_list)
    return check_all_rules(value_list, center_line, ucl_list, lcl_list)


def recommend_chart_type(data_groups: List[List[float]], data_type: str = 'measurement') -> Dict:
    if data_type == 'attribute':
        return {
            'recommended': 'U',
            'reason': '属性数据推荐使用U图（单位缺陷数图）',
            'alternatives': ['P', 'NP', 'C']
        }
    
    if not data_groups:
        return {
            'recommended': 'U',
            'reason': '无数据，默认推荐U图',
            'alternatives': []
        }
    
    avg_size = sum(len(g) for g in data_groups) / len(data_groups) if data_groups else 0
    
    if avg_size <= 10:
        return {
            'recommended': 'XR',
            'reason': f'平均样本量{avg_size:.1f}≤10，推荐使用X-R图（均值-极差图）',
            'alternatives': ['XS']
        }
    else:
        return {
            'recommended': 'XS',
            'reason': f'平均样本量{avg_size:.1f}>10，推荐使用X-s图（均值-标准差图）',
            'alternatives': ['XR']
        }


def check_rule_1(u_list: List[float], ucl_list: List[float]) -> List[int]:
    abnormal_indices = []
    for i, (u_i, ucl) in enumerate(zip(u_list, ucl_list)):
        if u_i > ucl:
            abnormal_indices.append(i)
    return abnormal_indices


def check_rule_2(u_list: List[float], center_line: float) -> List[int]:
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
    distance = ucl - center_line
    if distance <= 0:
        distance = abs(center_line - lcl)
    
    if distance <= 0:
        return {
            'above_a': u > center_line,
            'above_b': False,
            'above_c': False,
            'below_c': False,
            'below_b': False,
            'below_a': u < center_line
        }
    
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
        'below_a': u < lcl
    }
    
    return zones


def check_rule_5(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 2):
        zones_above = 0
        zones_below = 0
        
        for j in range(i, i+3):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            if zones['above_a'] or zones['above_b']:
                zones_above += 1
            elif zones['below_a'] or zones['below_b']:
                zones_below += 1
        
        if zones_above >= 2 or zones_below >= 2:
            for j in range(i, i+3):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def check_rule_6(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 4):
        zones_above = 0
        zones_below = 0
        
        for j in range(i, i+5):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            if zones['above_a'] or zones['above_b']:
                zones_above += 1
            elif zones['below_a'] or zones['below_b']:
                zones_below += 1
        
        if zones_above >= 4 or zones_below >= 4:
            for j in range(i, i+5):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def check_rule_7(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> List[int]:
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
    abnormal_indices = []
    n = len(u_list)
    
    for i in range(n - 7):
        has_above = False
        has_below = False
        all_outside_c = True
        
        for j in range(i, i+8):
            zones = get_zones(u_list[j], center_line, ucl_list[j], lcl_list[j])
            if zones['above_c'] or zones['below_c']:
                all_outside_c = False
                break
            if zones['above_a'] or zones['above_b']:
                has_above = True
            elif zones['below_a'] or zones['below_b']:
                has_below = True
        
        if has_above and has_below and all_outside_c:
            for j in range(i, i+8):
                if j not in abnormal_indices:
                    abnormal_indices.append(j)
    
    return sorted(abnormal_indices)


def check_all_rules(u_list: List[float], center_line: float, ucl_list: List[float], lcl_list: List[float]) -> Dict[int, List[int]]:
    rules = {}
    rules[1] = check_rule_1(u_list, ucl_list)
    rules[2] = check_rule_2(u_list, center_line)
    rules[3] = check_rule_3(u_list)
    rules[4] = check_rule_4(u_list)
    rules[5] = check_rule_5(u_list, center_line, ucl_list, lcl_list)
    rules[6] = check_rule_6(u_list, center_line, ucl_list, lcl_list)
    rules[7] = check_rule_7(u_list, center_line, ucl_list, lcl_list)
    rules[8] = check_rule_8(u_list, center_line, ucl_list, lcl_list)
    
    return rules


def generate_control_chart_data(c_list: List[int], n_list: List[float]) -> Dict:
    u_list = [calculate_u_i(c, n) for c, n in zip(c_list, n_list)]
    u_bar = calculate_mean_u(c_list, n_list)
    ucl_list, lcl_list = calculate_control_limits(u_bar, n_list)
    approx_ucl, approx_lcl = calculate_approximate_control_limits(u_bar, n_list)
    abnormal_rules = check_all_rules(u_list, u_bar, ucl_list, lcl_list)
    
    abnormal_points = set()
    for indices in abnormal_rules.values():
        abnormal_points.update(indices)
    abnormal_points = sorted(abnormal_points)
    
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
