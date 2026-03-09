"""
控制图计算服务 - 使用 ccharts 库
"""

import math
import numpy as np
from typing import List, Dict, Optional, Tuple
import sys
import os

flask_vue_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if flask_vue_path not in sys.path:
    sys.path.insert(0, flask_vue_path)

import ccharts
from ccharts.xbar_rbar import xbar_rbar, rbar
from ccharts.xbar_sbar import xbar_sbar, sbar
from ccharts.mr import mr, xmr
from ccharts.median_rbar import median_rbar, rbar_median
from ccharts.p import p
from ccharts.np import np as np_chart
from ccharts.c import c
from ccharts.u import u


def calculate_xbar_r_chart(data_groups: List[List[float]], subgroup_size: Optional[int] = None) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    valid_groups = [g for g in data_groups if g and len(g) >= 2]
    if not valid_groups:
        raise ValueError("没有有效的数据组")
    
    n = len(valid_groups[0]) if valid_groups else 5
    
    valid_groups = valid_groups[-25:]
    
    data = np.array([g + [g[-1]] * (n - len(g)) if len(g) < n else g[:n] for g in valid_groups])
    
    xbar_chart = xbar_rbar()
    X, Xbar, lcl_xbar, ucl_xbar, title_xbar = xbar_chart.plot(data, n)
    
    r_chart = rbar()
    R, Rbar, lcl_r, ucl_r, title_r = r_chart.plot(data, n)
    
    xbar_abnormal = check_abnormal_points(X, Xbar, ucl_xbar, lcl_xbar)
    r_abnormal = check_abnormal_points(R, Rbar, ucl_r, lcl_r)
    
    return {
        'chart_type': 'X-R',
        'xbar_chart': {
            'data_points': X.tolist() if hasattr(X, 'tolist') else list(X),
            'center_line': float(Xbar),
            'ucl': float(ucl_xbar),
            'lcl': float(lcl_xbar),
            'abnormal_points': xbar_abnormal,
            'title': title_xbar
        },
        'r_chart': {
            'data_points': R.tolist() if hasattr(R, 'tolist') else list(R),
            'center_line': float(Rbar),
            'ucl': float(ucl_r),
            'lcl': float(lcl_r),
            'abnormal_points': r_abnormal,
            'title': title_r
        },
        'statistics': {
            'total_groups': len(valid_groups),
            'subgroup_size': n,
            'grand_mean': float(Xbar),
            'avg_range': float(Rbar)
        },
        'message': 'X-R控制图数据生成成功'
    }


def calculate_xbar_s_chart(data_groups: List[List[float]], subgroup_size: Optional[int] = None) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    valid_groups = [g for g in data_groups if g and len(g) >= 2]
    if not valid_groups:
        raise ValueError("没有有效的数据组")
    
    n = len(valid_groups[0]) if valid_groups else 10
    
    valid_groups = valid_groups[-25:]
    
    data = np.array([g + [g[-1]] * (n - len(g)) if len(g) < n else g[:n] for g in valid_groups])
    
    xbar_chart = xbar_sbar()
    X, Xbar, lcl_xbar, ucl_xbar, title_xbar = xbar_chart.plot(data, n)
    
    s_chart = sbar()
    S, Sbar, lcl_s, ucl_s, title_s = s_chart.plot(data, n)
    
    xbar_abnormal = check_abnormal_points(X, Xbar, ucl_xbar, lcl_xbar)
    s_abnormal = check_abnormal_points(S, Sbar, ucl_s, lcl_s)
    
    return {
        'chart_type': 'X-s',
        'xbar_chart': {
            'data_points': X.tolist() if hasattr(X, 'tolist') else list(X),
            'center_line': float(Xbar),
            'ucl': float(ucl_xbar),
            'lcl': float(lcl_xbar),
            'abnormal_points': xbar_abnormal,
            'title': title_xbar
        },
        's_chart': {
            'data_points': S.tolist() if hasattr(S, 'tolist') else list(S),
            'center_line': float(Sbar),
            'ucl': float(ucl_s),
            'lcl': float(lcl_s),
            'abnormal_points': s_abnormal,
            'title': title_s
        },
        'statistics': {
            'total_groups': len(valid_groups),
            'subgroup_size': n,
            'grand_mean': float(Xbar),
            'avg_std_dev': float(Sbar)
        },
        'message': 'X-s控制图数据生成成功'
    }


def calculate_imr_chart(data: List[float]) -> Dict:
    if not data:
        raise ValueError("数据不能为空")
    
    data = data[-25:]
    
    data_array = np.array(data)
    
    x_chart = xmr()
    X, Xbar, lcl_x, ucl_x, title_x = x_chart.plot(data_array, 1)
    
    mr_chart = mr()
    MR, MRbar, lcl_mr, ucl_mr, title_mr = mr_chart.plot(data_array, 1)
    
    x_abnormal = check_abnormal_points(X, Xbar, ucl_x, lcl_x)
    
    mr_data_points = MR.tolist() if hasattr(MR, 'tolist') else list(MR)
    mr_data_points = [None if (isinstance(v, float) and (np.isnan(v) or v != v)) else v for v in mr_data_points]
    
    mr_values_for_check = [v for v in MR if not np.isnan(v)]
    mr_abnormal = check_abnormal_points(mr_values_for_check, MRbar, ucl_mr, lcl_mr)
    
    return {
        'chart_type': 'I-MR',
        'x_chart': {
            'data_points': X.tolist() if hasattr(X, 'tolist') else list(X),
            'center_line': float(Xbar),
            'ucl': float(ucl_x),
            'lcl': float(lcl_x),
            'abnormal_points': x_abnormal,
            'title': 'X图 (单值控制图)'
        },
        'mr_chart': {
            'data_points': mr_data_points,
            'center_line': float(MRbar),
            'ucl': float(ucl_mr),
            'lcl': float(lcl_mr),
            'abnormal_points': mr_abnormal,
            'title': title_mr
        },
        'statistics': {
            'total_points': len(data),
            'mean': float(Xbar),
            'avg_moving_range': float(MRbar)
        },
        'message': 'I-MR控制图数据生成成功'
    }


def calculate_median_r_chart(data_groups: List[List[float]], subgroup_size: Optional[int] = None) -> Dict:
    if not data_groups:
        raise ValueError("数据组不能为空")
    
    valid_groups = [g for g in data_groups if g and len(g) >= 2]
    if not valid_groups:
        raise ValueError("没有有效的数据组")
    
    n = len(valid_groups[0]) if valid_groups else 5
    
    valid_groups = valid_groups[-25:]
    
    data = np.array([g + [g[-1]] * (n - len(g)) if len(g) < n else g[:n] for g in valid_groups])
    
    median_chart = median_rbar()
    Medians, MedianBar, lcl_median, ucl_median, title_median = median_chart.plot(data, n)
    
    r_chart = rbar_median()
    R, Rbar, lcl_r, ucl_r, title_r = r_chart.plot(data, n)
    
    median_abnormal = check_abnormal_points(Medians, MedianBar, ucl_median, lcl_median)
    r_abnormal = check_abnormal_points(R, Rbar, ucl_r, lcl_r)
    
    return {
        'chart_type': 'Median-R',
        'median_chart': {
            'data_points': Medians.tolist() if hasattr(Medians, 'tolist') else list(Medians),
            'center_line': float(MedianBar),
            'ucl': float(ucl_median),
            'lcl': float(lcl_median),
            'abnormal_points': median_abnormal,
            'title': '中位数控制图'
        },
        'r_chart': {
            'data_points': R.tolist() if hasattr(R, 'tolist') else list(R),
            'center_line': float(Rbar),
            'ucl': float(ucl_r),
            'lcl': float(lcl_r),
            'abnormal_points': r_abnormal,
            'title': title_r
        },
        'statistics': {
            'total_groups': len(valid_groups),
            'subgroup_size': n,
            'grand_median': float(MedianBar),
            'avg_range': float(Rbar)
        },
        'message': '中位数-极差控制图数据生成成功'
    }


def calculate_p_chart(defects: List[int], sample_sizes: List[int]) -> Dict:
    if not defects or not sample_sizes:
        raise ValueError("数据不能为空")
    
    data = np.column_stack((sample_sizes, defects))
    
    p_chart = p()
    data_points, pbar, lcl, ucl, title = p_chart.plot(data, len(defects))
    
    abnormal = check_abnormal_points(data_points, pbar, ucl, lcl)
    
    return {
        'chart_type': 'P',
        'data_points': data_points.tolist() if hasattr(data_points, 'tolist') else list(data_points),
        'center_line': float(pbar),
        'ucl': float(ucl) if not isinstance(ucl, list) else ucl,
        'lcl': float(lcl) if not isinstance(lcl, list) else lcl,
        'abnormal_points': abnormal,
        'title': title,
        'statistics': {
            'total_samples': len(defects),
            'total_defects': sum(defects),
            'total_inspected': sum(sample_sizes),
            'avg_defect_rate': float(pbar)
        },
        'message': 'P控制图数据生成成功'
    }


def calculate_np_chart(defects: List[int], sample_size: int) -> Dict:
    if not defects:
        raise ValueError("数据不能为空")
    
    sizes = [sample_size] * len(defects)
    data = np.column_stack((sizes, defects))
    
    np_c = np_chart()
    data_points, npbar, lcl, ucl, title = np_c.plot(data, len(defects))
    
    abnormal = check_abnormal_points(data_points, npbar, ucl, lcl)
    
    return {
        'chart_type': 'NP',
        'data_points': data_points.tolist() if hasattr(data_points, 'tolist') else list(data_points),
        'center_line': float(npbar),
        'ucl': float(ucl),
        'lcl': float(lcl),
        'abnormal_points': abnormal,
        'title': title,
        'statistics': {
            'total_samples': len(defects),
            'sample_size': sample_size,
            'total_defects': sum(defects),
            'avg_defects': float(npbar)
        },
        'message': 'NP控制图数据生成成功'
    }


def calculate_c_chart(defects: List[int]) -> Dict:
    if not defects:
        raise ValueError("数据不能为空")
    
    sizes = [1] * len(defects)
    data = np.column_stack((sizes, defects))
    
    c_chart = c()
    data_points, cbar, lcl, ucl, title = c_chart.plot(data, len(defects))
    
    abnormal = check_abnormal_points(data_points, cbar, ucl, lcl)
    
    return {
        'chart_type': 'C',
        'data_points': data_points.tolist() if hasattr(data_points, 'tolist') else list(data_points),
        'center_line': float(cbar),
        'ucl': float(ucl),
        'lcl': max(0, float(lcl)),
        'abnormal_points': abnormal,
        'title': title,
        'statistics': {
            'total_samples': len(defects),
            'total_defects': sum(defects),
            'avg_defects': float(cbar)
        },
        'message': 'C控制图数据生成成功'
    }


def calculate_u_chart(defects: List[int], sample_sizes: List[int]) -> Dict:
    if not defects or not sample_sizes:
        raise ValueError("数据不能为空")
    
    data = np.column_stack((defects, sample_sizes))
    
    u_chart = u()
    data_points, ubar, lcl, ucl, title = u_chart.plot(data, len(defects))
    
    abnormal = check_abnormal_points(data_points, ubar, ucl, lcl)
    
    return {
        'chart_type': 'U',
        'data_points': data_points.tolist() if hasattr(data_points, 'tolist') else list(data_points),
        'center_line': float(ubar),
        'ucl': ucl if isinstance(ucl, list) else float(ucl),
        'lcl': lcl if isinstance(lcl, list) else float(lcl),
        'abnormal_points': abnormal,
        'title': title,
        'statistics': {
            'total_samples': len(defects),
            'total_defects': sum(defects),
            'total_inspected': sum(sample_sizes),
            'avg_defects_per_unit': float(ubar)
        },
        'message': 'U控制图数据生成成功'
    }


def check_abnormal_points(data_points, center, ucl, lcl) -> List[int]:
    abnormal = []
    
    if isinstance(ucl, list):
        ucl_max = max(ucl)
    else:
        ucl_max = ucl
        
    if isinstance(lcl, list):
        lcl_min = min(lcl)
    else:
        lcl_min = lcl
    
    for i, point in enumerate(data_points):
        if np.isnan(point):
            continue
        if point > ucl_max or point < lcl_min:
            abnormal.append(i + 1)
    
    return abnormal


def generate_control_chart_data(c_list: List[int], n_list: List[int], chart_type: str = 'U') -> Dict:
    if chart_type.upper() == 'P':
        return calculate_p_chart(c_list, n_list)
    elif chart_type.upper() == 'NP':
        if len(set(n_list)) == 1:
            return calculate_np_chart(c_list, n_list[0])
        else:
            raise ValueError("NP图要求样本量固定")
    elif chart_type.upper() == 'C':
        return calculate_c_chart(c_list)
    elif chart_type.upper() == 'U':
        return calculate_u_chart(c_list, n_list)
    else:
        return calculate_u_chart(c_list, n_list)


def recommend_chart_type(line_id: int, db) -> Dict:
    from ..models.models import ProductionLine, MeasurementData, AttributeData
    
    line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
    if not line:
        return {'recommended': 'U', 'reason': '产线不存在'}
    
    if line.data_type == 'attribute':
        attr_data = db.query(AttributeData).filter(
            AttributeData.line_id == line_id
        ).limit(30).all()
        
        if not attr_data:
            return {'recommended': 'U', 'reason': '没有属性数据，默认推荐U图'}
        
        sample_sizes = [d.sample_size for d in attr_data]
        
        if len(set(sample_sizes)) == 1:
            return {
                'recommended': 'NP',
                'reason': '样本量固定，推荐NP图',
                'alternatives': ['P', 'C', 'U']
            }
        else:
            return {
                'recommended': 'U',
                'reason': '样本量变化，推荐U图',
                'alternatives': ['P', 'C']
            }
    
    else:
        measurement_data = db.query(MeasurementData).filter(
            MeasurementData.line_id == line_id
        ).limit(50).all()
        
        if not measurement_data:
            return {'recommended': 'XR', 'reason': '没有量值数据，默认推荐X-R图'}
        
        subgroup_sizes = []
        for m in measurement_data:
            values = m.get_measurement_values()
            if values:
                subgroup_sizes.append(len(values))
        
        if not subgroup_sizes:
            return {'recommended': 'XR', 'reason': '没有有效数据'}
        
        avg_size = sum(subgroup_sizes) / len(subgroup_sizes)
        
        if avg_size >= 10:
            return {
                'recommended': 'XS',
                'reason': f'平均子组大小{avg_size:.1f}>=10，推荐X-s图',
                'alternatives': ['XR', 'IMR']
            }
        elif avg_size >= 2:
            return {
                'recommended': 'XR',
                'reason': f'平均子组大小{avg_size:.1f}在2-9之间，推荐X-R图',
                'alternatives': ['XS', 'IMR']
            }
        else:
            return {
                'recommended': 'IMR',
                'reason': '单值数据，推荐I-MR图',
                'alternatives': ['XR', 'XS']
            }
