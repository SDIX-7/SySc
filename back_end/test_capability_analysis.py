import requests
import json
import time

base_url = 'http://localhost:5000/api'

TOTAL_START = time.time()

print("=" * 60)
print("端到端测试：能力分析模块")
print("=" * 60)

# 1. 获取产线列表
print("\n[1] 获取产线列表...")
response = requests.get(f'{base_url}/production-lines')
lines = response.json()
print(f"   找到 {len(lines)} 条产线")

measurement_lines = [l for l in lines if l['data_type'] == 'measurement']
attribute_lines = [l for l in lines if l['data_type'] == 'attribute']
print(f"   计量型产线: {len(measurement_lines)} 条")
print(f"   计数型产线: {len(attribute_lines)} 条")

if len(measurement_lines) == 0:
    print("   错误: 没有计量型产线数据")
    exit(1)

line_id = measurement_lines[0]['id']
print(f"   选择计量型产线: ID={line_id}, 名称={measurement_lines[0]['line_name']}")

# 2. 获取测量数据
print(f"\n[2] 获取产线 {line_id} 的测量数据...")
response = requests.get(f'{base_url}/measurement-data?line_id={line_id}')
measurements = response.json()
print(f"   找到 {len(measurements)} 条测量记录")

if len(measurements) == 0:
    print("   错误: 没有测量数据")
    exit(1)

# 3. 准备分析数据
print("\n[3] 准备分析数据...")
data_values = []
for m in measurements[:50]:
    data_values.extend(m['measurement_values'])
print(f"   准备了 {len(data_values)} 个数据点")

data_min = min(data_values)
data_max = max(data_values)
data_mean = sum(data_values) / len(data_values)
margin = (data_max - data_min) * 0.5

# 4. 创建能力分析
print("\n[4] 创建能力分析...")
analysis_data = {
    'line_id': line_id,
    'analysis_name': '端到端测试分析',
    'usl': data_max + margin,
    'lsl': data_min - margin,
    'target': data_mean,
    'data_values': data_values,
    'analysis_type': 'process'
}
response = requests.post(f'{base_url}/capability-analysis', json=analysis_data)

if response.status_code != 200:
    print(f"   错误: 创建失败 - {response.status_code}")
    print(f"   详情: {response.text}")
    exit(1)

result = response.json()
analysis_id = result['id']
print(f"   创建成功! 分析ID: {analysis_id}")
print(f"   Cpk: {result['indices']['cpk']['value']:.4f}")
print(f"   Cp: {result['indices']['cp']['value']:.4f}")
print(f"   Ppk: {result['indices']['ppk']['value']:.4f}")
print(f"   Pp: {result['indices']['pp']['value']:.4f}")

# 5. 获取分析详情
print(f"\n[5] 获取分析详情 (ID={analysis_id})...")
response = requests.get(f'{base_url}/capability-analysis/{analysis_id}')
if response.status_code != 200:
    print(f"   错误: 获取失败 - {response.status_code}")
    exit(1)

detail = response.json()
print(f"   分析名称: {detail.get('analysis_name', 'N/A')}")
print(f"   样本数: {detail.get('sample_count', detail.get('data_statistics', {}).get('total_samples', 'N/A'))}")
print(f"   均值: {float(detail.get('mean', 0)):.4f}")
print(f"   USL: {detail.get('usl')}, LSL: {detail.get('lsl')}")
normality_test = detail.get('normality_test', {})
print(f"   正态性检验: {'通过' if normality_test.get('is_normal', False) else '未通过'}")

# 6. 获取分析历史列表
print(f"\n[6] 获取分析历史列表...")
response = requests.get(f'{base_url}/capability-analysis?line_id={line_id}')
analyses = response.json()
print(f"   找到 {len(analyses)} 条分析记录")

# 7. 测试边界情况
print("\n[7] 测试边界情况...")

# 7.1 USL <= LSL
print("   7.1 测试 USL <= LSL...")
bad_data = {
    'line_id': line_id,
    'usl': 97.0,
    'lsl': 103.0,
    'data_values': data_values[:10]
}
response = requests.post(f'{base_url}/capability-analysis', json=bad_data)
if response.status_code == 400:
    print("      正确: 返回400错误")
else:
    print(f"      警告: 应该返回400错误，实际返回 {response.status_code}")

# 7.2 数据少于2个
print("   7.2 测试数据少于2个...")
bad_data = {
    'line_id': line_id,
    'usl': data_max + margin,
    'lsl': data_min - margin,
    'data_values': [100.0]
}
response = requests.post(f'{base_url}/capability-analysis', json=bad_data)
if response.status_code == 400:
    print("      正确: 返回400错误")
else:
    print(f"      警告: 应该返回400错误，实际返回 {response.status_code}")

# 7.3 计数型产线
print("   7.3 测试计数型产线...")
if attribute_lines:
    attr_line_id = attribute_lines[0]['id']
    bad_data = {
        'line_id': attr_line_id,
        'usl': 105,
        'lsl': 95,
        'data_values': [100, 101, 99]
    }
    response = requests.post(f'{base_url}/capability-analysis', json=bad_data)
    if response.status_code == 400 and '计数型数据不支持' in response.json().get('detail', ''):
        print("      正确: 拒绝计数型数据的能力分析")
    else:
        print(f"      警告: 应该拒绝计数型数据，实际返回 {response.status_code}")
else:
    print("      跳过: 没有计数型产线")

# 8. 测试删除功能
print(f"\n[8] 测试删除功能...")
response = requests.delete(f'{base_url}/capability-analysis/{analysis_id}')
if response.status_code == 200:
    print("   删除成功")
else:
    print(f"   删除失败: {response.status_code}")

# 验证删除
response = requests.get(f'{base_url}/capability-analysis/{analysis_id}')
if response.status_code == 404:
    print("   验证: 记录已删除 (404)")
else:
    print(f"   警告: 记录可能未删除 ({response.status_code})")

print("\n" + "=" * 60)
print("端到端测试完成!")
print(f"总耗时: {time.time() - TOTAL_START:.2f} 秒")
print("=" * 60)
