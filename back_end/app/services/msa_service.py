import math
from typing import Dict, List, Optional
from datetime import datetime
import json

D2_CONSTANTS = {
    2: 1.128,
    3: 1.693,
    4: 2.059,
    5: 2.326,
    6: 2.534,
    7: 2.704,
    8: 2.847,
    9: 2.970,
    10: 3.078
}

D3_D4_CONSTANTS = {
    2: (0, 3.267),
    3: (0, 2.574),
    4: (0, 2.282),
    5: (0, 2.114),
    6: (0, 2.004),
    7: (0, 1.924),
    8: (0, 1.864),
    9: (0, 1.816),
    10: (0, 1.777)
}

A2_CONSTANTS = {
    2: 1.880,
    3: 1.023,
    4: 0.729,
    5: 0.577,
    6: 0.483,
    7: 0.419,
    8: 0.373,
    9: 0.337,
    10: 0.308
}


def get_d2(n: int) -> float:
    return D2_CONSTANTS.get(n, 1.128)


def get_d3_d4(n: int) -> tuple:
    return D3_D4_CONSTANTS.get(n, (0, 3.267))


def get_a2(n: int) -> float:
    return A2_CONSTANTS.get(n, 1.880)


def calculate_range(data: List[float]) -> float:
    if not data:
        return 0.0
    return max(data) - min(data)


def calculate_mean(data: List[float]) -> float:
    if not data:
        return 0.0
    return sum(data) / len(data)


def calculate_grr_xr(study_data: Dict) -> Dict:
    parts = study_data.get('parts', [])
    operators = study_data.get('operators', [])
    measurements = study_data.get('measurements', [])
    
    num_parts = len(parts)
    num_operators = len(operators)
    num_replicates = 0
    
    if measurements:
        replicate_counts = {}
        for meas in measurements:
            key = (meas.get('part_id'), meas.get('operator_id'))
            replicate_counts[key] = replicate_counts.get(key, 0) + 1
        if replicate_counts:
            num_replicates = max(replicate_counts.values())
    
    if num_parts < 2 or num_operators < 2 or num_replicates < 2:
        return {
            'error': '数据不足：需要至少2个零件、2个操作员和2次重复测量',
            'valid': False
        }
    
    data_matrix = {}
    for meas in measurements:
        part_id = meas.get('part_id')
        op_id = meas.get('operator_id')
        replicate = meas.get('replicate', 1)
        try:
            value = float(meas.get('measurement_value', 0))
        except (ValueError, TypeError):
            value = 0.0
        
        key = (part_id, op_id, replicate)
        data_matrix[key] = value
    
    ranges_operator_part = []
    x_bar_operator_part = []
    x_bar_parts = {p['id']: [] for p in parts}
    x_bar_operators = {o['id']: [] for o in operators}
    all_measurements = []
    
    for part in parts:
        part_id = part['id']
        for op in operators:
            op_id = op['id']
            replicate_values = []
            for r in range(1, num_replicates + 1):
                key = (part_id, op_id, r)
                if key in data_matrix:
                    val = data_matrix[key]
                    replicate_values.append(val)
                    x_bar_parts[part_id].append(val)
                    x_bar_operators[op_id].append(val)
                    all_measurements.append(val)
            
            if replicate_values:
                r_ij = calculate_range(replicate_values)
                x_ij = calculate_mean(replicate_values)
                ranges_operator_part.append(r_ij)
                x_bar_operator_part.append(x_ij)
    
    if not ranges_operator_part:
        return {
            'error': '没有有效的测量数据',
            'valid': False
        }
    
    R_bar = calculate_mean(ranges_operator_part)
    X_double_bar = calculate_mean(x_bar_operator_part)
    
    part_averages = []
    for part in parts:
        if x_bar_parts[part['id']]:
            part_averages.append(calculate_mean(x_bar_parts[part['id']]))
    R_p = calculate_range(part_averages) if part_averages else 0
    
    X_bar_parts = []
    for part in parts:
        if x_bar_parts[part['id']]:
            X_bar_parts.append(calculate_mean(x_bar_parts[part['id']]))
    X_bar_part = calculate_mean(X_bar_parts)
    
    X_bar_operators = []
    for op in operators:
        if x_bar_operators[op['id']]:
            X_bar_operators.append(calculate_mean(x_bar_operators[op['id']]))
    
    d2 = get_d2(num_replicates)
    d2_prime = get_d2(num_operators)
    
    sigma_e_sq = (R_bar / d2) ** 2
    
    X_diff_bar = 0
    if len(X_bar_operators) >= 2:
        X_diff_bar = calculate_range(X_bar_operators)
    
    sigma_o_sq = max(0, ((X_diff_bar / d2_prime) ** 2 - sigma_e_sq / num_replicates))
    
    sigma_grr_sq = sigma_e_sq + sigma_o_sq
    
    sigma_p_sq = max(0, ((R_p / d2) ** 2 - sigma_grr_sq / num_replicates))
    
    sigma_total_sq = sigma_grr_sq + sigma_p_sq
    
    sigma_e = math.sqrt(sigma_e_sq) if sigma_e_sq > 0 else 0
    sigma_o = math.sqrt(sigma_o_sq) if sigma_o_sq > 0 else 0
    sigma_grr = math.sqrt(sigma_grr_sq) if sigma_grr_sq > 0 else 0
    sigma_p = math.sqrt(sigma_p_sq) if sigma_p_sq > 0 else 0
    sigma_total = math.sqrt(sigma_total_sq) if sigma_total_sq > 0 else 0
    
    percent_grr = (sigma_grr / sigma_total * 100) if sigma_total > 0 else 0
    
    ndc = 1.41 * (sigma_p / sigma_grr) if sigma_grr > 0 else 0
    
    tolerance = study_data.get('tolerance')
    percent_tolerance = None
    if tolerance:
        try:
            tol = float(tolerance)
            if tol > 0:
                percent_tolerance = (6 * sigma_grr / tol) * 100
        except (ValueError, TypeError):
            pass
    
    if percent_grr < 10:
        grr_acceptance = 'acceptable'
    elif percent_grr < 30:
        grr_acceptance = 'conditional'
    else:
        grr_acceptance = 'unacceptable'
    
    ndc_acceptance = 'acceptable' if ndc >= 5 else 'unacceptable'
    
    if grr_acceptance == 'acceptable' and ndc_acceptance == 'acceptable':
        overall_acceptance = 'acceptable'
    elif grr_acceptance == 'unacceptable' or ndc_acceptance == 'unacceptable':
        overall_acceptance = 'unacceptable'
    else:
        overall_acceptance = 'conditional'
    
    detailed_results = {
        'data_summary': {
            'number_of_parts': num_parts,
            'number_of_operators': num_operators,
            'number_of_replicates': num_replicates,
            'total_measurements': len(all_measurements)
        },
        'range_analysis': {
            'R_bar': round(R_bar, 6),
            'R_p': round(R_p, 6),
            'X_bar_part': round(X_bar_part, 6),
            'X_double_bar': round(X_double_bar, 6),
            'X_diff_bar': round(X_diff_bar, 6)
        },
        'constants': {
            'd2': round(d2, 4),
            'd2_prime': round(d2_prime, 4),
            'n': num_replicates,
            'o': num_operators,
            'p': num_parts
        },
        'variance_components': {
            'repeatability': round(sigma_e_sq, 6),
            'reproducibility': round(sigma_o_sq, 6),
            'grr': round(sigma_grr_sq, 6),
            'part_to_part': round(sigma_p_sq, 6),
            'total': round(sigma_total_sq, 6)
        },
        'standard_deviations': {
            'repeatability': round(sigma_e, 6),
            'reproducibility': round(sigma_o, 6),
            'grr': round(sigma_grr, 6),
            'part_to_part': round(sigma_p, 6),
            'total': round(sigma_total, 6)
        },
        'acceptance_criteria': {
            'grr_acceptance_threshold': {
                'acceptable': '< 10%',
                'conditional': '10% - 30%',
                'unacceptable': '>= 30%'
            },
            'ndc_acceptance_threshold': {
                'acceptable': '>= 5',
                'unacceptable': '< 5'
            }
        }
    }
    
    return {
        'valid': True,
        'study_type': 'grr',
        'calculation_method': 'xr',
        'variance_repeatability': str(round(sigma_e_sq, 6)),
        'variance_reproducibility': str(round(sigma_o_sq, 6)),
        'variance_grr': str(round(sigma_grr_sq, 6)),
        'variance_part': str(round(sigma_p_sq, 6)),
        'variance_total': str(round(sigma_total_sq, 6)),
        'stddev_repeatability': str(round(sigma_e, 6)),
        'stddev_reproducibility': str(round(sigma_o, 6)),
        'stddev_grr': str(round(sigma_grr, 6)),
        'stddev_part': str(round(sigma_p, 6)),
        'stddev_total': str(round(sigma_total, 6)),
        'percent_grr': str(round(percent_grr, 2)),
        'percent_tolerance': str(round(percent_tolerance, 2)) if percent_tolerance else None,
        'ndc': str(round(ndc, 2)),
        'grr_acceptance': grr_acceptance,
        'ndc_acceptance': ndc_acceptance,
        'overall_acceptance': overall_acceptance,
        'detailed_results': detailed_results
    }


def calculate_grr_anova(study_data: Dict) -> Dict:
    parts = study_data.get('parts', [])
    operators = study_data.get('operators', [])
    measurements = study_data.get('measurements', [])
    
    num_parts = len(parts)
    num_operators = len(operators)
    num_replicates = 0
    
    if measurements:
        replicate_counts = {}
        for meas in measurements:
            key = (meas.get('part_id'), meas.get('operator_id'))
            replicate_counts[key] = replicate_counts.get(key, 0) + 1
        if replicate_counts:
            num_replicates = max(replicate_counts.values())
    
    if num_parts < 2 or num_operators < 2 or num_replicates < 2:
        return {
            'error': '数据不足：需要至少2个零件、2个操作员和2次重复测量',
            'valid': False
        }
    
    data_matrix = {}
    all_measurements = []
    for meas in measurements:
        part_id = meas.get('part_id')
        op_id = meas.get('operator_id')
        replicate = meas.get('replicate', 1)
        try:
            value = float(meas.get('measurement_value', 0))
        except (ValueError, TypeError):
            value = 0.0
        
        key = (part_id, op_id, replicate)
        data_matrix[key] = value
        all_measurements.append(value)
    
    if not all_measurements:
        return {
            'error': '没有有效的测量数据',
            'valid': False
        }
    
    n = num_replicates
    o = num_operators
    p = num_parts
    N = len(all_measurements)
    
    grand_mean = sum(all_measurements) / N
    
    part_means = {}
    for part in parts:
        part_id = part['id']
        values = []
        for op in operators:
            op_id = op['id']
            for r in range(1, n + 1):
                key = (part_id, op_id, r)
                if key in data_matrix:
                    values.append(data_matrix[key])
        if values:
            part_means[part_id] = sum(values) / len(values)
    
    operator_means = {}
    for op in operators:
        op_id = op['id']
        values = []
        for part in parts:
            part_id = part['id']
            for r in range(1, n + 1):
                key = (part_id, op_id, r)
                if key in data_matrix:
                    values.append(data_matrix[key])
        if values:
            operator_means[op_id] = sum(values) / len(values)
    
    cell_means = {}
    for part in parts:
        for op in operators:
            part_id = part['id']
            op_id = op['id']
            values = []
            for r in range(1, n + 1):
                key = (part_id, op_id, r)
                if key in data_matrix:
                    values.append(data_matrix[key])
            if values:
                cell_means[(part_id, op_id)] = sum(values) / len(values)
    
    SS_total = sum((x - grand_mean) ** 2 for x in all_measurements)
    
    SS_parts = n * o * sum((part_means.get(p['id'], grand_mean) - grand_mean) ** 2 for p in parts)
    
    SS_operators = n * p * sum((operator_means.get(o['id'], grand_mean) - grand_mean) ** 2 for o in operators)
    
    SS_part_operator = n * sum((cell_means.get((p['id'], o['id']), grand_mean) - part_means.get(p['id'], grand_mean) - operator_means.get(o['id'], grand_mean) + grand_mean) ** 2 
                               for p in parts for o in operators if (p['id'], o['id']) in cell_means)
    
    SS_repeatability = SS_total - SS_parts - SS_operators - SS_part_operator
    
    df_parts = p - 1
    df_operators = o - 1
    df_part_operator = (p - 1) * (o - 1)
    df_repeatability = N - p * o
    
    MS_parts = SS_parts / df_parts if df_parts > 0 else 0
    MS_operators = SS_operators / df_operators if df_operators > 0 else 0
    MS_part_operator = SS_part_operator / df_part_operator if df_part_operator > 0 else 0
    MS_repeatability = SS_repeatability / df_repeatability if df_repeatability > 0 else 0
    
    sigma_repeatability_sq = max(0, MS_repeatability)
    
    if n > 1:
        sigma_operator_sq = max(0, (MS_operators - MS_part_operator) / (n * p))
    else:
        sigma_operator_sq = max(0, MS_operators - MS_part_operator)
    
    if n > 1:
        sigma_part_operator_sq = max(0, (MS_part_operator - MS_repeatability) / n)
    else:
        sigma_part_operator_sq = max(0, MS_part_operator)
    
    sigma_part_sq = max(0, (MS_parts - MS_part_operator) / (n * o))
    
    sigma_grr_sq = sigma_repeatability_sq + sigma_operator_sq + sigma_part_operator_sq
    sigma_total_sq = sigma_grr_sq + sigma_part_sq
    
    sigma_e = math.sqrt(sigma_repeatability_sq) if sigma_repeatability_sq > 0 else 0
    sigma_o = math.sqrt(sigma_operator_sq) if sigma_operator_sq > 0 else 0
    sigma_po = math.sqrt(sigma_part_operator_sq) if sigma_part_operator_sq > 0 else 0
    sigma_p = math.sqrt(sigma_part_sq) if sigma_part_sq > 0 else 0
    sigma_grr = math.sqrt(sigma_grr_sq) if sigma_grr_sq > 0 else 0
    sigma_total = math.sqrt(sigma_total_sq) if sigma_total_sq > 0 else 0
    
    percent_grr = (sigma_grr / sigma_total * 100) if sigma_total > 0 else 0
    
    ndc = 1.41 * (sigma_p / sigma_grr) if sigma_grr > 0 else 0
    
    tolerance = study_data.get('tolerance')
    percent_tolerance = None
    if tolerance:
        try:
            tol = float(tolerance)
            if tol > 0:
                percent_tolerance = (6 * sigma_grr / tol) * 100
        except (ValueError, TypeError):
            pass
    
    if percent_grr < 10:
        grr_acceptance = 'acceptable'
    elif percent_grr < 30:
        grr_acceptance = 'conditional'
    else:
        grr_acceptance = 'unacceptable'
    
    ndc_acceptance = 'acceptable' if ndc >= 5 else 'unacceptable'
    
    if grr_acceptance == 'acceptable' and ndc_acceptance == 'acceptable':
        overall_acceptance = 'acceptable'
    elif grr_acceptance == 'unacceptable' or ndc_acceptance == 'unacceptable':
        overall_acceptance = 'unacceptable'
    else:
        overall_acceptance = 'conditional'
    
    detailed_results = {
        'data_summary': {
            'number_of_parts': num_parts,
            'number_of_operators': num_operators,
            'number_of_replicates': num_replicates,
            'total_measurements': len(all_measurements)
        },
        'anova_table': {
            'source': ['零件', '操作员', '零件x操作员', '重复性', '总计'],
            'SS': [round(SS_parts, 6), round(SS_operators, 6), round(SS_part_operator, 6), round(SS_repeatability, 6), round(SS_total, 6)],
            'df': [df_parts, df_operators, df_part_operator, df_repeatability, N - 1],
            'MS': [round(MS_parts, 6), round(MS_operators, 6), round(MS_part_operator, 6), round(MS_repeatability, 6), None]
        },
        'variance_components': {
            'repeatability': round(sigma_repeatability_sq, 6),
            'reproducibility_operator': round(sigma_operator_sq, 6),
            'reproducibility_interaction': round(sigma_part_operator_sq, 6),
            'total_reproducibility': round(sigma_operator_sq + sigma_part_operator_sq, 6),
            'grr': round(sigma_grr_sq, 6),
            'part_to_part': round(sigma_part_sq, 6),
            'total': round(sigma_total_sq, 6)
        },
        'standard_deviations': {
            'repeatability': round(sigma_e, 6),
            'reproducibility_operator': round(sigma_o, 6),
            'reproducibility_interaction': round(sigma_po, 6),
            'total_reproducibility': round(math.sqrt(sigma_operator_sq + sigma_part_operator_sq), 6),
            'grr': round(sigma_grr, 6),
            'part_to_part': round(sigma_p, 6),
            'total': round(sigma_total, 6)
        },
        'acceptance_criteria': {
            'grr_acceptance_threshold': {
                'acceptable': '< 10%',
                'conditional': '10% - 30%',
                'unacceptable': '>= 30%'
            },
            'ndc_acceptance_threshold': {
                'acceptable': '>= 5',
                'unacceptable': '< 5'
            }
        }
    }
    
    return {
        'valid': True,
        'study_type': 'grr',
        'calculation_method': 'anova',
        'variance_repeatability': str(round(sigma_repeatability_sq, 6)),
        'variance_reproducibility': str(round(sigma_operator_sq + sigma_part_operator_sq, 6)),
        'variance_grr': str(round(sigma_grr_sq, 6)),
        'variance_part': str(round(sigma_part_sq, 6)),
        'variance_total': str(round(sigma_total_sq, 6)),
        'stddev_repeatability': str(round(sigma_e, 6)),
        'stddev_reproducibility': str(round(math.sqrt(sigma_operator_sq + sigma_part_operator_sq), 6)),
        'stddev_grr': str(round(sigma_grr, 6)),
        'stddev_part': str(round(sigma_p, 6)),
        'stddev_total': str(round(sigma_total, 6)),
        'percent_grr': str(round(percent_grr, 2)),
        'percent_tolerance': str(round(percent_tolerance, 2)) if percent_tolerance else None,
        'ndc': str(round(ndc, 2)),
        'grr_acceptance': grr_acceptance,
        'ndc_acceptance': ndc_acceptance,
        'overall_acceptance': overall_acceptance,
        'detailed_results': detailed_results
    }
