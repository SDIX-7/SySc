#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试控制图异常报警邮件功能
"""

from functions.email_utils import send_control_chart_alert

def test_control_chart_alert():
    """
    测试控制图异常报警邮件发送
    """
    # 模拟异常数据
    abnormal_data = {
        'abnormal_points': [2, 5, 8],
        'sample_defects_details': [
            {
                'sample_size': 3,
                'total_defects': 5,
                'defects_per_pcb': [2, 1, 2],
                'pcb_names': ['PCB_001', 'PCB_002', 'PCB_003'],
                'capture_times': ['2023-01-01T10:00:00', '2023-01-01T10:05:00', '2023-01-01T10:10:00']
            },
            {
                'sample_size': 3,
                'total_defects': 8,
                'defects_per_pcb': [3, 3, 2],
                'pcb_names': ['PCB_004', 'PCB_005', 'PCB_006'],
                'capture_times': ['2023-01-01T10:15:00', '2023-01-01T10:20:00', '2023-01-01T10:25:00']
            },
            {
                'sample_size': 3,
                'total_defects': 12,
                'defects_per_pcb': [4, 5, 3],
                'pcb_names': ['PCB_007', 'PCB_008', 'PCB_009'],
                'capture_times': ['2023-01-01T10:30:00', '2023-01-01T10:35:00', '2023-01-01T10:40:00']
            }
        ],
        'u_list': [1.6667, 2.0, 4.0, 2.3333, 2.6667, 5.0, 2.0, 2.3333, 6.0, 2.0],
        'c_list': [5, 6, 12, 7, 8, 15, 6, 7, 18, 6],
        'n_list': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
        'center_line': 2.5,
        'ucl_list': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        'lcl_list': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }
    
    print("开始测试控制图异常报警邮件发送...")
    result = send_control_chart_alert(abnormal_data)
    if result:
        print("测试成功：邮件发送成功")
    else:
        print("测试失败：邮件发送失败")

if __name__ == "__main__":
    test_control_chart_alert()
