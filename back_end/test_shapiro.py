import numpy as np
from scipy import stats

np.random.seed(42)
data = np.random.normal(100, 0.1, 500).tolist()

print(f'Testing with {len(data)} values')
print(f'Mean: {np.mean(data):.4f}')
print(f'Std: {np.std(data):.4f}')

# SciPy 结果
stat, p = stats.shapiro(data)
print(f'\nSciPy Shapiro-Wilk:')
print(f'  W statistic: {stat:.6f}')
print(f'  p-value: {p:.6f}')

# 测试前端的算法
n = len(data)
sorted_data = sorted(data)
mean = np.mean(data)

s2 = sum((x - mean) ** 2 for x in sorted_data)

m = n // 2
a = [sorted_data[n - 1 - i] - sorted_data[i] for i in range(m)]

b2 = sum(ai ** 2 for ai in a)

from math import sqrt, log, exp

def normal_cdf(x):
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    sign = -1 if x < 0 else 1
    x = abs(x) / sqrt(2)
    
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * exp(-x * x)
    
    return 0.5 * (1.0 + sign * y)

a_coeffs = []
for i in range(m):
    expected_normal = normal_cdf((i + 1 - 0.375) / (n + 0.25))
    a_coeffs.append(expected_normal)

sum_a_coeffs2 = sum(ai ** 2 for ai in a_coeffs)
c = 1 / sqrt(sum_a_coeffs2)
a_star = [c * ai for ai in a_coeffs]

numerator = sum(a_star[i] * a[i] for i in range(m))
w = (numerator ** 2) / s2

log_w = log(1 - w)
mu = -1.2725 + 1.0521 * log(n)
sigma = 1.0308 - 0.26758 * log(n)
z = (log_w - mu) / sigma
p_value = 1 - normal_cdf(z)

print(f'\nFrontend algorithm:')
print(f'  W statistic: {w:.6f}')
print(f'  p-value: {p_value:.6f}')
print(f'  is_normal: {p_value >= 0.05}')

# 检查 w 值
print(f'\nW value check: {w:.6f}')
print(f'1 - W: {1 - w:.6f}')
print(f'log(1-W): {log(1-w):.6f}')
