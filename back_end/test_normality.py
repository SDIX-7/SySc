import sys
sys.path.insert(0, 'd:/质量信息系统/flask+vue/back_end')
from app.services.capability_service import test_normality, _shapiro_wilk_statistic, _approximate_shapiro_wilk
import numpy as np

# 生成正态数据
np.random.seed(42)
values = np.random.normal(100, 0.1, 500).tolist()

print(f'Testing with {len(values)} values')
print(f'Mean: {np.mean(values):.4f}')
print(f'Std: {np.std(values):.4f}')

# 测试正态性
result = test_normality(values)
print(f'W statistic: {result["statistic"]}')
print(f'P-value: {result["p_value"]}')
print(f'Is normal: {result["is_normal"]}')
print(f'Interpretation: {result["interpretation"]}')

# 测试 _shapiro_wilk_statistic
w = _shapiro_wilk_statistic(values)
print(f'\nDirect W calculation: {w}')

# 测试 _approximate_shapiro_wilk
mean = np.mean(values)
std = np.std(values)
w2 = _approximate_shapiro_wilk(values, mean, std)
print(f'Approximate W: {w2}')
