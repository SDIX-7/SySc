import math
from typing import List, Dict, Optional


def calculate_mean(values: List[float]) -> float:
    if not values:
        raise ValueError("数据列表不能为空")
    return sum(values) / len(values)


def calculate_std_dev_within(values: List[float]) -> float:
    if len(values) < 2:
        raise ValueError("计算组内标准差需要至少2个样本")
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def calculate_std_dev_overall(values: List[float]) -> float:
    if len(values) < 2:
        raise ValueError("计算总体标准差需要至少2个样本")
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def calculate_sigma_within(data_groups: List[List[float]]) -> float:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    n_list = []
    s_list = []
    
    for group in data_groups:
        if len(group) < 2:
            continue
        n_list.append(len(group))
        s = calculate_std_dev_within(group)
        s_list.append(s)
    
    if not n_list:
        raise ValueError("没有有效的数据组")
    
    k = len(n_list)
    n_bar = sum(n_list) / k if k > 0 else 0
    
    if n_bar <= 1:
        raise ValueError("子组样本量必须大于1才能计算组内标准差")
    
    c4_table = {
        2: 0.7979, 3: 0.8862, 4: 0.9213, 5: 0.9400, 6: 0.9515,
        7: 0.9594, 8: 0.9650, 9: 0.9693, 10: 0.9727, 11: 0.9754,
        12: 0.9776, 13: 0.9794, 14: 0.9810, 15: 0.9823, 16: 0.9835,
        17: 0.9845, 18: 0.9854, 19: 0.9862, 20: 0.9869, 21: 0.9876,
        22: 0.9882, 23: 0.9887, 24: 0.9892, 25: 0.9896
    }
    
    def get_c4(n: int) -> float:
        if n in c4_table:
            return c4_table[n]
        if n < 2:
            return c4_table[2]
        return c4_table[25]
    
    s_bar = sum(s_list) / k if s_list else 0
    c4 = get_c4(round(n_bar))
    
    if c4 == 0:
        raise ValueError("c4系数不能为0")
    
    return s_bar / c4


def calculate_sigma_overall(values: List[float]) -> float:
    if not values:
        raise ValueError("数据列表不能为空")
    return calculate_std_dev_overall(values)


def evaluate_capability_index(value: float) -> Dict[str, any]:
    if value >= 1.67:
        return {
            'level': 'excellent',
            'level_text': '过程能力过剩',
            'color': 'green',
            'description': '过程能力非常充分，可以考虑降低检验力度'
        }
    elif value >= 1.33:
        return {
            'level': 'good',
            'level_text': '过程能力充分',
            'color': 'blue',
            'description': '过程能力满足要求，继续保持'
        }
    elif value >= 1.00:
        return {
            'level': 'marginal',
            'level_text': '过程能力一般',
            'color': 'yellow',
            'description': '过程能力勉强满足，需要密切关注'
        }
    else:
        return {
            'level': 'poor',
            'level_text': '过程能力不足',
            'color': 'red',
            'description': '过程能力不足，需要立即改进'
        }


def calculate_cp(usl: float, lsl: float, sigma_within: float) -> float:
    if sigma_within <= 0:
        raise ValueError("组内标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    return (usl - lsl) / (6 * sigma_within)


def calculate_cpk(usl: float, lsl: float, mean: float, sigma_within: float) -> float:
    if sigma_within <= 0:
        raise ValueError("组内标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    
    cpu = (usl - mean) / (3 * sigma_within)
    cpl = (mean - lsl) / (3 * sigma_within)
    return min(cpu, cpl)


def calculate_pp(usl: float, lsl: float, sigma_overall: float) -> float:
    if sigma_overall <= 0:
        raise ValueError("总体标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    return (usl - lsl) / (6 * sigma_overall)


def calculate_ppk(usl: float, lsl: float, mean: float, sigma_overall: float) -> float:
    if sigma_overall <= 0:
        raise ValueError("总体标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    
    ppu = (usl - mean) / (3 * sigma_overall)
    ppl = (mean - lsl) / (3 * sigma_overall)
    return min(ppu, ppl)


def calculate_cm(usl: float, lsl: float, sigma_machine: float) -> float:
    if sigma_machine <= 0:
        raise ValueError("机器标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    return (usl - lsl) / (6 * sigma_machine)


def calculate_cmk(usl: float, lsl: float, mean: float, sigma_machine: float) -> float:
    if sigma_machine <= 0:
        raise ValueError("机器标准差必须大于0")
    if usl <= lsl:
        raise ValueError("规格上限必须大于规格下限")
    
    cmu = (usl - mean) / (3 * sigma_machine)
    cml = (mean - lsl) / (3 * sigma_machine)
    return min(cmu, cml)


def calculate_capability_indices(
    data_groups: List[List[float]],
    usl: float,
    lsl: float,
    target: Optional[float] = None,
    sigma_machine: Optional[float] = None
) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    all_values = []
    for group in data_groups:
        all_values.extend(group)
    
    if not all_values:
        raise ValueError("没有有效的数据")
    
    mean = calculate_mean(all_values)
    sigma_within = calculate_sigma_within(data_groups)
    sigma_overall = calculate_sigma_overall(all_values)
    
    cp = calculate_cp(usl, lsl, sigma_within)
    cpk = calculate_cpk(usl, lsl, mean, sigma_within)
    pp = calculate_pp(usl, lsl, sigma_overall)
    ppk = calculate_ppk(usl, lsl, mean, sigma_overall)
    
    cm = None
    cmk = None
    if sigma_machine is not None and sigma_machine > 0:
        cm = calculate_cm(usl, lsl, sigma_machine)
        cmk = calculate_cmk(usl, lsl, mean, sigma_machine)
    
    cp_evaluation = evaluate_capability_index(cp)
    cpk_evaluation = evaluate_capability_index(cpk)
    pp_evaluation = evaluate_capability_index(pp)
    ppk_evaluation = evaluate_capability_index(ppk)
    
    if cmk is not None:
        cmk_evaluation = evaluate_capability_index(cmk)
    else:
        cmk_evaluation = None
    
    normality_result = test_normality(all_values)
    
    if target is None:
        target = (usl + lsl) / 2
    
    ca = (mean - target) / ((usl - lsl) / 2) * 100 if (usl - lsl) > 0 else 0
    
    return {
        'usl': usl,
        'lsl': lsl,
        'target': target,
        'mean': mean,
        'sigma_within': sigma_within,
        'sigma_overall': sigma_overall,
        'sigma_machine': sigma_machine,
        'indices': {
            'cp': {
                'value': round(cp, 4),
                'formula': '(USL - LSL) / (6 * σ_within)',
                'evaluation': cp_evaluation
            },
            'cpk': {
                'value': round(cpk, 4),
                'formula': 'min[(USL - μ) / (3 * σ_within), (μ - LSL) / (3 * σ_within)]',
                'evaluation': cpk_evaluation
            },
            'pp': {
                'value': round(pp, 4),
                'formula': '(USL - LSL) / (6 * σ_overall)',
                'evaluation': pp_evaluation
            },
            'ppk': {
                'value': round(ppk, 4),
                'formula': 'min[(USL - μ) / (3 * σ_overall), (μ - LSL) / (3 * σ_overall)]',
                'evaluation': ppk_evaluation
            },
            'cm': {
                'value': round(cm, 4) if cm is not None else None,
                'formula': '(USL - LSL) / (6 * σ_machine)' if cm is not None else None,
                'evaluation': None
            },
            'cmk': {
                'value': round(cmk, 4) if cmk is not None else None,
                'formula': 'min[(USL - μ) / (3 * σ_machine), (μ - LSL) / (3 * σ_machine)]' if cmk is not None else None,
                'evaluation': cmk_evaluation
            }
        },
        'additional_metrics': {
            'ca': round(ca, 2),
            'ca_evaluation': '偏高' if ca > 2.5 else ('偏低' if ca < -2.5 else '正常')
        },
        'data_statistics': {
            'total_samples': len(all_values),
            'subgroup_count': len(data_groups),
            'avg_subgroup_size': round(len(all_values) / len(data_groups), 2) if data_groups else 0
        },
        'normality_test': normality_result,
        'message': '能力指数计算成功'
    }


def calculate_capability_from_raw_values(
    values: List[float],
    usl: float,
    lsl: float,
    target: Optional[float] = None,
    sigma_machine: Optional[float] = None,
    is_grouped: bool = False,
    subgroup_size: int = 5
) -> Dict:
    if not values:
        raise ValueError("数据列表不能为空")
    
    if is_grouped:
        data_groups = []
        for i in range(0, len(values), subgroup_size):
            group = values[i:i + subgroup_size]
            if len(group) >= 2:
                data_groups.append(group)
        if not data_groups:
            raise ValueError("无法形成有效的数据组")
        return calculate_capability_indices(data_groups, usl, lsl, target, sigma_machine)
    else:
        mean = calculate_mean(values)
        sigma_overall = calculate_sigma_overall(values)
        
        cp = calculate_cp(usl, lsl, sigma_overall)
        cpk = calculate_cpk(usl, lsl, mean, sigma_overall)
        pp = calculate_pp(usl, lsl, sigma_overall)
        ppk = calculate_ppk(usl, lsl, mean, sigma_overall)
        
        cm = None
        cmk = None
        if sigma_machine is not None and sigma_machine > 0:
            cm = calculate_cm(usl, lsl, sigma_machine)
            cmk = calculate_cmk(usl, lsl, mean, sigma_machine)
        
        cp_evaluation = evaluate_capability_index(cp)
        cpk_evaluation = evaluate_capability_index(cpk)
        pp_evaluation = evaluate_capability_index(pp)
        ppk_evaluation = evaluate_capability_index(ppk)
        
        if cmk is not None:
            cmk_evaluation = evaluate_capability_index(cmk)
        else:
            cmk_evaluation = None
        
        normality_result = test_normality(values)
        
        if target is None:
            target = (usl + lsl) / 2
        
        ca = (mean - target) / ((usl - lsl) / 2) * 100 if (usl - lsl) > 0 else 0
        
        return {
            'usl': usl,
            'lsl': lsl,
            'target': target,
            'mean': mean,
            'sigma_within': sigma_overall,
            'sigma_overall': sigma_overall,
            'sigma_machine': sigma_machine,
            'indices': {
                'cp': {
                    'value': round(cp, 4),
                    'formula': '(USL - LSL) / (6 * σ)',
                    'evaluation': cp_evaluation
                },
                'cpk': {
                    'value': round(cpk, 4),
                    'formula': 'min[(USL - μ) / (3 * σ), (μ - LSL) / (3 * σ)]',
                    'evaluation': cpk_evaluation
                },
                'pp': {
                    'value': round(pp, 4),
                    'formula': '(USL - LSL) / (6 * σ)',
                    'evaluation': pp_evaluation
                },
                'ppk': {
                    'value': round(ppk, 4),
                    'formula': 'min[(USL - μ) / (3 * σ), (μ - LSL) / (3 * σ)]',
                    'evaluation': ppk_evaluation
                },
                'cm': {
                    'value': round(cm, 4) if cm is not None else None,
                    'formula': '(USL - LSL) / (6 * σ_machine)' if cm is not None else None,
                    'evaluation': None
                },
                'cmk': {
                    'value': round(cmk, 4) if cmk is not None else None,
                    'formula': 'min[(USL - μ) / (3 * σ_machine), (μ - LSL) / (3 * σ_machine)]' if cmk is not None else None,
                    'evaluation': cmk_evaluation
                }
            },
            'additional_metrics': {
                'ca': round(ca, 2),
                'ca_evaluation': '偏高' if ca > 2.5 else ('偏低' if ca < -2.5 else '正常')
            },
            'data_statistics': {
                'total_samples': len(values),
                'subgroup_count': 1,
                'avg_subgroup_size': len(values)
            },
            'normality_test': normality_result,
            'data_values': values,
            'message': '能力指数计算成功'
        }


def validate_specification_limits(usl: float, lsl: float, values: List[float]) -> Dict:
    mean = calculate_mean(values)
    min_val = min(values)
    max_val = max(values)
    
    errors = []
    warnings = []
    
    if usl <= lsl:
        errors.append("规格上限必须大于规格下限")
    
    if max_val > usl:
        warnings.append(f"数据最大值({max_val:.4f})超过规格上限({usl})，将影响Cpk值")
    
    if min_val < lsl:
        warnings.append(f"数据最小值({min_val:.4f})低于规格下限({lsl})，将影响Cpk值")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'data_range': {
            'min': min_val,
            'max': max_val,
            'mean': mean
        },
        'specification_range': {
            'usl': usl,
            'lsl': lsl,
            'tolerance': usl - lsl
        }
    }


def calculate_skewness(values: List[float]) -> float:
    if len(values) < 3:
        raise ValueError("计算偏度需要至少3个样本")
    
    n = len(values)
    mean = calculate_mean(values)
    std = calculate_std_dev_overall(values)
    
    if std == 0:
        return 0.0
    
    skewness = sum(((x - mean) / std) ** 3 for x in values) * n / ((n - 1) * (n - 2))
    return skewness


def calculate_kurtosis(values: List[float]) -> float:
    if len(values) < 4:
        raise ValueError("计算峰度需要至少4个样本")
    
    n = len(values)
    mean = calculate_mean(values)
    std = calculate_std_dev_overall(values)
    
    if std == 0:
        return 0.0
    
    kurtosis = n * (n + 1) * sum(((x - mean) / std) ** 4 for x in values) / ((n - 1) * (n - 2) * (n - 3))
    kurtosis -= 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    return kurtosis


def test_normality(values: List[float]) -> Dict:
    if len(values) < 3:
        return {
            'test': 'Shapiro-Wilk',
            'statistic': None,
            'p_value': None,
            'is_normal': None,
            'interpretation': '样本量不足，需要至少3个样本',
            'skewness': None,
            'kurtosis': None
        }
    
    n = len(values)
    mean = calculate_mean(values)
    std = calculate_std_dev_overall(values)
    
    skewness = calculate_skewness(values)
    kurtosis = calculate_kurtosis(values)
    
    if n < 50:
        shapiro_stat = _shapiro_wilk_statistic(values)
    else:
        shapiro_stat = _approximate_shapiro_wilk(values, mean, std)
    
    if shapiro_stat is not None:
        if n <= 50:
            p_value = _shapiro_wilk_p_value(shapiro_stat, n)
        else:
            p_value = _approximate_p_value(shapiro_stat, n)
    else:
        p_value = None
    
    is_normal = p_value > 0.05 if p_value is not None else None
    
    interpretation = ""
    if is_normal is True:
        interpretation = "数据符合正态分布 (p > 0.05)"
    elif is_normal is False:
        interpretation = "数据不符合正态分布 (p ≤ 0.05)"
    else:
        interpretation = "无法判断正态性"
    
    skewness_eval = ""
    if abs(skewness) < 0.5:
        skewness_eval = "近似对称"
    elif skewness > 0:
        skewness_eval = "正偏态（右偏）"
    else:
        skewness_eval = "负偏态（左偏）"
    
    kurtosis_eval = ""
    if abs(kurtosis) < 0.5:
        kurtosis_eval = "近似正态峰度"
    elif kurtosis > 0:
        kurtosis_eval = "尖峰（厚尾）"
    else:
        kurtosis_eval = "平峰（薄尾）"
    
    return {
        'test': 'Shapiro-Wilk',
        'statistic': round(shapiro_stat, 6) if shapiro_stat else None,
        'p_value': round(p_value, 6) if p_value else None,
        'is_normal': is_normal,
        'interpretation': interpretation,
        'skewness': round(skewness, 4),
        'skewness_eval': skewness_eval,
        'kurtosis': round(kurtosis, 4),
        'kurtosis_eval': kurtosis_eval,
        'sample_size': n
    }


def _shapiro_wilk_statistic(values: List[float]) -> float:
    n = len(values)
    if n < 3:
        return None
    
    sorted_values = sorted(values)
    mean = calculate_mean(values)
    
    if mean == 0:
        return 1.0
    
    ss = sum((x - mean) ** 2 for x in values)
    
    m = [(n + 1) * (i - (n + 1) / 2) / n for i in range(1, n + 1)]
    
    mm_sum = sum(m[i] ** 2 for i in range(n))
    
    b = sum(m[i] * (sorted_values[i] - mean) for i in range(n)) ** 2
    
    if ss == 0 or mm_sum == 0:
        return 1.0
    
    w = b / (ss * mm_sum)
    return w


def _approximate_shapiro_wilk(values: List[float], mean: float, std: float) -> float:
    n = len(values)
    if n < 3:
        return None
    
    sorted_values = sorted(values)
    
    if std == 0:
        return 1.0
    
    normalized = [(x - mean) / std for x in sorted_values]
    
    w = _shapiro_wilk_statistic(normalized)
    
    return w


def _shapiro_wilk_p_value(w: float, n: int) -> float:
    if n < 3 or n > 50:
        return None
    
    coefficients = {
        3: (0.7337, 0.0410), 4: (0.6288, 0.0884), 5: (0.5522, 0.1289),
        6: (0.4827, 0.1436), 7: (0.4348, 0.1407), 8: (0.3926, 0.1386),
        9: (0.3578, 0.1357), 10: (0.3294, 0.1330), 11: (0.3039, 0.1297),
        12: (0.2815, 0.1257), 13: (0.2616, 0.1212), 14: (0.2438, 0.1165),
        15: (0.2279, 0.1118), 16: (0.2135, 0.1071), 17: (0.2003, 0.1026),
        18: (0.1882, 0.0982), 19: (0.1771, 0.0941), 20: (0.1669, 0.0902),
        21: (0.1575, 0.0865), 22: (0.1488, 0.0830), 23: (0.1408, 0.0797),
        24: (0.1334, 0.0766), 25: (0.1266, 0.0737), 26: (0.1203, 0.0709),
        27: (0.1145, 0.0683), 28: (0.1092, 0.0658), 29: (0.1042, 0.0635),
        30: (0.0995, 0.0613), 31: (0.0951, 0.0592), 32: (0.0910, 0.0572),
        33: (0.0872, 0.0553), 34: (0.0836, 0.0535), 35: (0.0802, 0.0518),
        36: (0.0770, 0.0502), 37: (0.0740, 0.0487), 38: (0.0712, 0.0473),
        39: (0.0686, 0.0459), 40: (0.0661, 0.0446), 41: (0.0638, 0.0434),
        42: (0.0616, 0.0422), 43: (0.0595, 0.0411), 44: (0.0575, 0.0400),
        45: (0.0557, 0.0390), 46: (0.0539, 0.0380), 47: (0.0522, 0.0371),
        48: (0.0506, 0.0362), 49: (0.0491, 0.0353), 50: (0.0477, 0.0345)
    }
    
    if n in coefficients:
        a, b = coefficients[n]
        mean = a
        std = b
    else:
        mean = 0.0038915 * n ** 3 - 0.3102 * n ** 2 - 0.07811 * n + 1.0732
        std = -0.0006718 * n ** 3 + 0.06554 * n ** 2 - 0.1927 * n + 0.1049
    
    z = (w - mean) / std if std > 0 else 0
    
    p_value = 1 - _normal_cdf(z)
    
    return max(0, min(1, p_value))


def _approximate_p_value(w: float, n: int) -> float:
    if w >= 0.99:
        return 0.99
    elif w >= 0.97:
        return 0.95
    elif w >= 0.94:
        return 0.90
    elif w >= 0.90:
        return 0.80
    elif w >= 0.85:
        return 0.70
    elif w >= 0.80:
        return 0.50
    elif w >= 0.75:
        return 0.30
    elif w >= 0.70:
        return 0.20
    elif w >= 0.65:
        return 0.10
    elif w >= 0.60:
        return 0.05
    else:
        return 0.01


def _normal_cdf(z: float) -> float:
    import math
    if z < -6.0:
        return 0.0
    if z > 6.0:
        return 1.0
    
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    sign = -1 if z < 0 else 1
    z = abs(z) / math.sqrt(2)
    
    t = 1.0 / (1.0 + p * z)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z)
    
    return 0.5 * (1.0 + sign * y)
