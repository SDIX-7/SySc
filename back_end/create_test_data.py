import requests
import numpy as np
from datetime import datetime, timedelta

base_url = 'http://localhost:5000/api'

print("=" * 60)
print("创建测试数据 - 能力分析模块")
print("=" * 60)

# 1. 创建计量型产线（用于能力分析）
print("\n[1] 创建计量型产线...")

# 产线1: 正态分布数据，Cpk ≈ 1.5（能力充足）
line1 = {
    'line_code': 'MEAS-001',
    'line_name': '高精度加工线',
    'line_description': '计量型数据，Cpk约1.5，能力充足',
    'data_type': 'measurement',  # 计量型
    'status': 'active'
}
r1 = requests.post(f'{base_url}/production-lines', json=line1)
print(f"   创建产线1 (计量型): {r1.status_code}")
line1_id = r1.json().get('id') if r1.status_code == 200 else None

# 产线2: 正态分布数据，Cpk ≈ 0.8（能力不足）
line2 = {
    'line_code': 'MEAS-002',
    'line_name': '普通加工线',
    'line_description': '计量型数据，Cpk约0.8，能力不足',
    'data_type': 'measurement',  # 计量型
    'status': 'active'
}
r2 = requests.post(f'{base_url}/production-lines', json=line2)
print(f"   创建产线2 (计量型): {r2.status_code}")
line2_id = r2.json().get('id') if r2.status_code == 200 else None

# 产线3: 非正态分布数据
line3 = {
    'line_code': 'MEAS-003',
    'line_name': '特殊工艺线',
    'line_description': '计量型数据，非正态分布',
    'data_type': 'measurement',  # 计量型
    'status': 'active'
}
r3 = requests.post(f'{base_url}/production-lines', json=line3)
print(f"   创建产线3 (计量型): {r3.status_code}")
line3_id = r3.json().get('id') if r3.status_code == 200 else None

# 创建一个计数型产线（用于验证能力分析入口被禁用）
line4 = {
    'line_code': 'ATTR-001',
    'line_name': '外观检测线',
    'line_description': '计数型数据，用于验证能力分析入口禁用',
    'data_type': 'attribute',  # 计数型
    'status': 'active'
}
r4 = requests.post(f'{base_url}/production-lines', json=line4)
print(f"   创建产线4 (计数型): {r4.status_code}")
line4_id = r4.json().get('id') if r4.status_code == 200 else None

# 2. 为计量型产线创建测量数据
print("\n[2] 创建测量数据...")

np.random.seed(42)

# 产线1: 正态分布，目标值100，标准差0.5
# USL=103, LSL=97, Target=100 → Cpk ≈ (100-97)/(3*0.5) = 2.0 或 (103-100)/(3*0.5) = 2.0
# 但我们让均值稍微偏移一点，使Cpk ≈ 1.5
if line1_id:
    print(f"   为产线1创建数据...")
    mean, std = 100.0, 0.67  # 标准差0.67，使Cpk ≈ 1.5
    values_list = np.random.normal(mean, std, 100)
    
    base_time = datetime.now() - timedelta(days=7)
    for i, val in enumerate(values_list):
        sample_values = [float(val + np.random.normal(0, 0.05)) for _ in range(5)]
        data = {
            'line_id': line1_id,
            'sample_id': f'S{str(i+1).zfill(3)}',
            'measurement_values': sample_values,
            'measurement_time': (base_time + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S'),
            'operator': '测试员A'
        }
        requests.post(f'{base_url}/measurement-data', json=data)
    print(f"   创建了 100 条测量数据")

# 产线2: 正态分布，目标值100，标准差1.2，均值偏移
# USL=103, LSL=97, Target=100
if line2_id:
    print(f"   为产线2创建数据...")
    mean, std = 100.8, 1.0  # 均值偏移+0.8，标准差1.0
    values_list = np.random.normal(mean, std, 100)
    
    base_time = datetime.now() - timedelta(days=7)
    for i, val in enumerate(values_list):
        sample_values = [float(val + np.random.normal(0, 0.1)) for _ in range(5)]
        data = {
            'line_id': line2_id,
            'sample_id': f'S{str(i+1).zfill(3)}',
            'measurement_values': sample_values,
            'measurement_time': (base_time + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S'),
            'operator': '测试员B'
        }
        requests.post(f'{base_url}/measurement-data', json=data)
    print(f"   创建了 100 条测量数据")

# 产线3: 非正态分布（指数分布）
if line3_id:
    print(f"   为产线3创建数据...")
    values_list = np.random.exponential(1.0, 100) + 99  # 偏态分布
    
    base_time = datetime.now() - timedelta(days=7)
    for i, val in enumerate(values_list):
        sample_values = [float(val + np.random.normal(0, 0.1)) for _ in range(5)]
        data = {
            'line_id': line3_id,
            'sample_id': f'S{str(i+1).zfill(3)}',
            'measurement_values': sample_values,
            'measurement_time': (base_time + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S'),
            'operator': '测试员C'
        }
        requests.post(f'{base_url}/measurement-data', json=data)
    print(f"   创建了 100 条测量数据")

# 产线4: 计数型数据（缺陷数据）
if line4_id:
    print(f"   为产线4创建计数型数据...")
    base_time = datetime.now() - timedelta(days=7)
    for i in range(50):
        data = {
            'line_id': line4_id,
            'sample_id': f'A{str(i+1).zfill(3)}',
            'sample_size': 100,
            'defect_count': np.random.randint(0, 5),
            'inspector': '检验员D'
        }
        requests.post(f'{base_url}/attribute-data', json=data)
    print(f"   创建了 50 条计数型数据")

print("\n" + "=" * 60)
print("测试数据创建完成!")
print("=" * 60)

# 验证数据类型检查
print("\n[验证] 测试计数型产线能力分析...")
if line4_id:
    test_data = {
        'line_id': line4_id,
        'usl': 105,
        'lsl': 95,
        'data_values': [100, 101, 99, 100.5, 99.5]
    }
    r = requests.post(f'{base_url}/capability-analysis', json=test_data)
    if r.status_code == 400 and '计数型数据不支持' in r.json().get('detail', ''):
        print("   ✓ 正确: 后端拒绝了计数型数据的能力分析请求")
    else:
        print(f"   ✗ 错误: 后端应拒绝计数型数据，实际返回 {r.status_code}")
