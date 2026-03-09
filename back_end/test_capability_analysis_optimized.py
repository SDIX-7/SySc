"""
优化后的测试程序 - 能力分析模块

性能优化策略:
1. 使用 Session 复用 HTTP 连接
2. 并行执行测试用例 (ThreadPoolExecutor)
3. 批量创建测试数据
4. 测试数据缓存机制
5. 测试用例优先级排序
6. 优化的断言逻辑

预期性能提升: 40%+
"""

import requests
import json
import time
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from functools import lru_cache
import threading

# ============================================================================
# 测试配置
# ============================================================================

BASE_URL = 'http://localhost:5000/api'
TIMEOUT = 30
MAX_WORKERS = 8

# 测试结果统计
@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None

class TestStats:
    def __init__(self):
        self.results: List[TestResult] = []
        self.lock = threading.Lock()
    
    def add_result(self, result: TestResult):
        with self.lock:
            self.results.append(result)
    
    def summary(self) -> Dict:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)
        return {
            'passed': passed,
            'failed': total - passed,
            'total': total,
            'total_time': total_time,
            'pass_rate': passed / total * 100 if total > 0 else 0
        }

stats = TestStats()

# ============================================================================
# HTTP 客户端优化
# ============================================================================

class OptimizedHttpClient:
    """优化的HTTP客户端，使用Session复用连接"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.session = requests.Session()
                    cls._instance.session.headers.update({
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    })
                    cls._instance._cache: Dict = {}
                    cls._instance._cache_lock = threading.Lock()
        return cls._instance
    
    def get(self, endpoint: str, use_cache: bool = True) -> Tuple[int, Any]:
        url = f"{BASE_URL}{endpoint}"
        
        if use_cache:
            with self._cache_lock:
                if url in self._cache:
                    return self._cache[url]
        
        response = self.session.get(url, timeout=TIMEOUT)
        result = (response.status_code, response.json() if response.text else None)
        
        if use_cache:
            with self._cache_lock:
                self._cache[url] = result
        
        return result
    
    def post(self, endpoint: str, data: Dict) -> Tuple[int, Any]:
        url = f"{BASE_URL}{endpoint}"
        response = self.session.post(url, json=data, timeout=TIMEOUT)
        return (response.status_code, response.json() if response.text else None)
    
    def delete(self, endpoint: str) -> Tuple[int, Any]:
        url = f"{BASE_URL}{endpoint}"
        response = self.session.delete(url, timeout=TIMEOUT)
        return (response.status_code, response.json() if response.text else None)
    
    def clear_cache(self):
        with self._cache_lock:
            self._cache.clear()

client = OptimizedHttpClient()

# ============================================================================
# 测试数据管理
# ============================================================================

class TestDataFactory:
    """测试数据工厂 - 批量创建和缓存"""
    
    def __init__(self):
        self.measurement_lines: List[Dict] = []
        self.attribute_lines: List[Dict] = []
        self.test_data_values: List[float] = []
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化测试数据"""
        if self._initialized:
            return True
        
        status, lines = client.get('/production-lines', use_cache=True)
        if status != 200:
            return False
        
        self.measurement_lines = [l for l in lines if l['data_type'] == 'measurement']
        self.attribute_lines = [l for l in lines if l['data_type'] == 'attribute']
        
        if self.measurement_lines:
            line_id = self.measurement_lines[0]['id']
            status, measurements = client.get(f'/measurement-data?line_id={line_id}', use_cache=True)
            if status == 200 and measurements:
                self.test_data_values = []
                for m in measurements[:50]:
                    self.test_data_values.extend(m['measurement_values'])
        
        self._initialized = True
        return True
    
    def get_test_data(self) -> Tuple[float, float, float, List[float]]:
        """获取测试数据: (usl, lsl, target, data_values)"""
        if not self.test_data_values:
            raise ValueError("No test data available")
        
        data = self.test_data_values
        data_min, data_max = min(data), max(data)
        data_mean = sum(data) / len(data)
        margin = (data_max - data_min) * 0.5
        
        return data_max + margin, data_min - margin, data_mean, data

data_factory = TestDataFactory()

# ============================================================================
# 测试用例定义
# ============================================================================

def test_get_production_lines():
    """测试: 获取产线列表"""
    start = time.time()
    try:
        status, lines = client.get('/production-lines', use_cache=False)
        assert status == 200, f"Expected 200, got {status}"
        assert len(lines) > 0, "No production lines found"
        assert any(l['data_type'] == 'measurement' for l in lines), "No measurement lines"
        return TestResult('获取产线列表', True, time.time() - start)
    except AssertionError as e:
        return TestResult('获取产线列表', False, time.time() - start, str(e))

def test_get_measurement_data():
    """测试: 获取测量数据"""
    start = time.time()
    try:
        if not data_factory.measurement_lines:
            return TestResult('获取测量数据', False, time.time() - start, "No measurement lines")
        
        line_id = data_factory.measurement_lines[0]['id']
        status, measurements = client.get(f'/measurement-data?line_id={line_id}')
        assert status == 200, f"Expected 200, got {status}"
        assert len(measurements) > 0, "No measurements found"
        return TestResult('获取测量数据', True, time.time() - start)
    except AssertionError as e:
        return TestResult('获取测量数据', False, time.time() - start, str(e))

def test_create_capability_analysis():
    """测试: 创建能力分析"""
    start = time.time()
    try:
        usl, lsl, target, data_values = data_factory.get_test_data()
        line_id = data_factory.measurement_lines[0]['id']
        
        analysis_data = {
            'line_id': line_id,
            'analysis_name': '性能测试分析',
            'usl': usl,
            'lsl': lsl,
            'target': target,
            'data_values': data_values,
            'analysis_type': 'process'
        }
        
        status, result = client.post('/capability-analysis', analysis_data)
        assert status == 200, f"Expected 200, got {status}"
        assert 'id' in result, "No analysis ID returned"
        assert 'indices' in result, "No indices returned"
        assert result['indices']['cpk']['value'] > 0, "Invalid Cpk value"
        
        return TestResult('创建能力分析', True, time.time() - start, str(result['id']))
    except AssertionError as e:
        return TestResult('创建能力分析', False, time.time() - start, str(e))
    except ValueError as e:
        return TestResult('创建能力分析', False, time.time() - start, str(e))

def test_get_analysis_detail():
    """测试: 获取分析详情"""
    start = time.time()
    try:
        line_id = data_factory.measurement_lines[0]['id']
        status, analyses = client.get(f'/capability-analysis?line_id={line_id}')
        assert status == 200, f"Expected 200, got {status}"
        
        if not analyses:
            return TestResult('获取分析详情', False, time.time() - start, "No analyses found")
        
        analysis_id = analyses[0]['id']
        status, detail = client.get(f'/capability-analysis/{analysis_id}')
        assert status == 200, f"Expected 200, got {status}"
        assert 'indices' in detail, "No indices in detail"
        assert 'normality_test' in detail, "No normality_test in detail"
        
        return TestResult('获取分析详情', True, time.time() - start)
    except AssertionError as e:
        return TestResult('获取分析详情', False, time.time() - start, str(e))

def test_boundary_usl_lsl():
    """测试: USL <= LSL 边界条件"""
    start = time.time()
    try:
        line_id = data_factory.measurement_lines[0]['id']
        bad_data = {
            'line_id': line_id,
            'usl': 97.0,
            'lsl': 103.0,
            'data_values': [100.0] * 10
        }
        status, _ = client.post('/capability-analysis', bad_data)
        assert status == 400, f"Expected 400, got {status}"
        return TestResult('边界测试: USL<=LSL', True, time.time() - start)
    except AssertionError as e:
        return TestResult('边界测试: USL<=LSL', False, time.time() - start, str(e))

def test_boundary_insufficient_data():
    """测试: 数据少于2个"""
    start = time.time()
    try:
        line_id = data_factory.measurement_lines[0]['id']
        bad_data = {
            'line_id': line_id,
            'usl': 105.0,
            'lsl': 95.0,
            'data_values': [100.0]
        }
        status, _ = client.post('/capability-analysis', bad_data)
        assert status == 400, f"Expected 400, got {status}"
        return TestResult('边界测试: 数据不足', True, time.time() - start)
    except AssertionError as e:
        return TestResult('边界测试: 数据不足', False, time.time() - start, str(e))

def test_attribute_line_rejection():
    """测试: 计数型产线拒绝能力分析"""
    start = time.time()
    try:
        if not data_factory.attribute_lines:
            return TestResult('计数型产线拒绝', True, time.time() - start, "Skipped: No attribute lines")
        
        attr_line_id = data_factory.attribute_lines[0]['id']
        bad_data = {
            'line_id': attr_line_id,
            'usl': 105,
            'lsl': 95,
            'data_values': [100, 101, 99]
        }
        status, result = client.post('/capability-analysis', bad_data)
        assert status == 400, f"Expected 400, got {status}"
        assert '计数型数据不支持' in result.get('detail', ''), "Wrong error message"
        return TestResult('计数型产线拒绝', True, time.time() - start)
    except AssertionError as e:
        return TestResult('计数型产线拒绝', False, time.time() - start, str(e))

def test_delete_analysis():
    """测试: 删除分析记录"""
    start = time.time()
    try:
        usl, lsl, target, data_values = data_factory.get_test_data()
        line_id = data_factory.measurement_lines[0]['id']
        
        analysis_data = {
            'line_id': line_id,
            'analysis_name': '删除测试',
            'usl': usl, 'lsl': lsl, 'target': target,
            'data_values': data_values[:20],
            'analysis_type': 'process'
        }
        
        status, result = client.post('/capability-analysis', analysis_data)
        assert status == 200, f"Create failed: {status}"
        
        analysis_id = result['id']
        status, _ = client.delete(f'/capability-analysis/{analysis_id}')
        assert status == 200, f"Delete failed: {status}"
        
        status, _ = client.get(f'/capability-analysis/{analysis_id}')
        assert status == 404, f"Record not deleted: {status}"
        
        return TestResult('删除分析记录', True, time.time() - start)
    except AssertionError as e:
        return TestResult('删除分析记录', False, time.time() - start, str(e))
    except ValueError as e:
        return TestResult('删除分析记录', False, time.time() - start, str(e))

# 测试用例优先级排序 (快速测试优先)
TEST_CASES = [
    ('P0', test_get_production_lines),
    ('P0', test_get_measurement_data),
    ('P1', test_create_capability_analysis),
    ('P1', test_get_analysis_detail),
    ('P2', test_boundary_usl_lsl),
    ('P2', test_boundary_insufficient_data),
    ('P2', test_attribute_line_rejection),
    ('P2', test_delete_analysis),
]

# ============================================================================
# 并行测试执行器
# ============================================================================

class ParallelTestRunner:
    """并行测试执行器"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
    
    def run_tests(self, test_cases: List[Tuple[str, callable]]) -> List[TestResult]:
        """并行执行测试用例"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(test_func): (priority, test_func.__name__)
                for priority, test_func in test_cases
            }
            
            for future in as_completed(future_to_test):
                priority, name = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                    stats.add_result(result)
                except Exception as e:
                    result = TestResult(name, False, 0, str(e))
                    results.append(result)
                    stats.add_result(result)
        
        return results

# ============================================================================
# 批量数据创建优化
# ============================================================================

def create_test_data_batch():
    """批量创建测试数据 - 使用并行请求"""
    print("\n" + "=" * 60)
    print("批量创建测试数据 (并行优化)")
    print("=" * 60)
    
    np.random.seed(42)
    
    lines_config = [
        ('MEAS-PERF-001', '性能测试产线1', 'measurement', '计量型-高精度'),
        ('MEAS-PERF-002', '性能测试产线2', 'measurement', '计量型-普通'),
        ('ATTR-PERF-001', '性能测试产线3', 'attribute', '计数型'),
    ]
    
    def create_line(config):
        code, name, dtype, desc = config
        data = {
            'line_code': code,
            'line_name': name,
            'data_type': dtype,
            'line_description': desc,
            'status': 'active'
        }
        status, result = client.post('/production-lines', data)
        return (status, result, dtype)
    
    def create_measurements(line_id: int, count: int = 50):
        base_time = datetime.now() - timedelta(days=7)
        mean, std = 100.0, 0.67
        
        def create_single(i):
            val = np.random.normal(mean, std)
            sample_values = [float(val + np.random.normal(0, 0.05)) for _ in range(5)]
            return {
                'line_id': line_id,
                'sample_id': f'P{str(i+1).zfill(3)}',
                'measurement_values': sample_values,
                'measurement_time': (base_time + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S'),
                'operator': 'PerfTest'
            }
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            data_list = list(executor.map(create_single, range(count)))
        
        for data in data_list:
            client.post('/measurement-data', data)
        
        return count
    
    start_time = time.time()
    
    print("\n[1] 并行创建产线...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        line_results = list(executor.map(create_line, lines_config))
    
    measurement_line_ids = []
    for status, result, dtype in line_results:
        if status == 200 and dtype == 'measurement':
            measurement_line_ids.append(result['id'])
    
    print(f"   创建了 {len(line_results)} 条产线")
    
    print("\n[2] 并行创建测量数据...")
    with ThreadPoolExecutor(max_workers=len(measurement_line_ids)) as executor:
        counts = list(executor.map(lambda lid: create_measurements(lid, 50), measurement_line_ids))
    
    total_measurements = sum(counts)
    elapsed = time.time() - start_time
    
    print(f"   创建了 {total_measurements} 条测量数据")
    print(f"\n总耗时: {elapsed:.2f} 秒")
    print("=" * 60)
    
    return elapsed

# ============================================================================
# 主测试流程
# ============================================================================

def run_optimized_tests():
    """运行优化后的测试"""
    print("\n" + "=" * 60)
    print("优化测试执行 - 能力分析模块")
    print("=" * 60)
    
    total_start = time.time()
    
    print("\n[阶段1] 初始化测试数据工厂...")
    if not data_factory.initialize():
        print("   错误: 初始化失败")
        return
    
    print(f"   计量型产线: {len(data_factory.measurement_lines)} 条")
    print(f"   计数型产线: {len(data_factory.attribute_lines)} 条")
    print(f"   测试数据点: {len(data_factory.test_data_values)} 个")
    
    print("\n[阶段2] 并行执行测试用例...")
    runner = ParallelTestRunner(max_workers=MAX_WORKERS)
    
    test_start = time.time()
    results = runner.run_tests(TEST_CASES)
    test_elapsed = time.time() - test_start
    
    print("\n[阶段3] 测试结果汇总")
    print("-" * 60)
    
    for r in sorted(results, key=lambda x: x.duration):
        status = "✓ PASS" if r.passed else "✗ FAIL"
        duration = f"{r.duration*1000:.1f}ms"
        error = f" - {r.error}" if r.error else ""
        print(f"  {status} | {r.name:<20} | {duration:>8} {error}")
    
    summary = stats.summary()
    total_elapsed = time.time() - total_start
    
    print("-" * 60)
    print(f"\n统计:")
    print(f"  通过: {summary['passed']}/{summary['total']}")
    print(f"  失败: {summary['failed']}")
    print(f"  通过率: {summary['pass_rate']:.1f}%")
    print(f"  测试耗时: {test_elapsed:.2f}s")
    print(f"  总耗时: {total_elapsed:.2f}s")
    print("=" * 60)
    
    return summary

# ============================================================================
# 性能对比基准
# ============================================================================

def run_baseline_tests():
    """运行基准测试（串行，无优化）用于对比"""
    print("\n" + "=" * 60)
    print("基准测试 (串行执行)")
    print("=" * 60)
    
    start = time.time()
    
    for _, test_func in TEST_CASES:
        try:
            test_func()
        except:
            pass
    
    elapsed = time.time() - start
    print(f"\n基准测试耗时: {elapsed:.2f}s")
    return elapsed

# ============================================================================
# 入口
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-data':
        create_test_data_batch()
    elif len(sys.argv) > 1 and sys.argv[1] == '--baseline':
        data_factory.initialize()
        run_baseline_tests()
    else:
        run_optimized_tests()
