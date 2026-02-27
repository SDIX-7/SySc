import math
from typing import List, Dict, Tuple


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
