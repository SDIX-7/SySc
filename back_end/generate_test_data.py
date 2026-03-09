import requests
import random
import numpy as np
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api'

def delete_lines():
    r = requests.get(f'{BASE_URL}/production-lines')
    lines = r.json()
    
    lines_to_delete = [l for l in lines if l['id'] > 1]
    
    for line in lines_to_delete:
        r = requests.delete(f"{BASE_URL}/production-lines/{line['id']}")
        print(f"Deleted: {line['line_name']} (ID: {line['id']})")
    
    print(f"\nDeleted {len(lines_to_delete)} production lines")

def generate_measurement_data(line_id, num_records=100, subgroup_size=5, mean=100, std=0.1):
    for i in range(num_records):
        values = [round(random.gauss(mean, std), 4) for _ in range(subgroup_size)]
        data = {
            'line_id': line_id,
            'measurement_values': values,
            'measurement_time': (datetime.now() - timedelta(hours=num_records-i)).isoformat()
        }
        requests.post(f'{BASE_URL}/measurement-data', json=data)
    print(f"Generated {num_records} measurement records for line {line_id}")

def generate_attribute_data(line_id, num_records=100, sample_size=50, defect_rate=0.02):
    for i in range(num_records):
        defect_count = sum(random.random() < defect_rate for _ in range(sample_size))
        data = {
            'line_id': line_id,
            'defect_count': defect_count,
            'sample_size': sample_size,
            'inspection_time': (datetime.now() - timedelta(hours=num_records-i)).isoformat()
        }
        requests.post(f'{BASE_URL}/attribute-data', json=data)
    print(f"Generated {num_records} attribute records for line {line_id}")

def create_test_lines():
    lines = [
        {'line_name': '精密加工线A', 'line_code': 'LINE-A', 'data_type': 'measurement', 'description': '高精度零件加工'},
        {'line_name': '装配线B', 'line_code': 'LINE-B', 'data_type': 'attribute', 'description': '产品装配质检'},
        {'line_name': '注塑线C', 'line_code': 'LINE-C', 'data_type': 'measurement', 'description': '注塑件尺寸检测'},
        {'line_name': '包装线D', 'line_code': 'LINE-D', 'data_type': 'attribute', 'description': '包装外观检验'},
    ]
    
    created_lines = []
    for line_data in lines:
        r = requests.post(f'{BASE_URL}/production-lines', json=line_data)
        if r.status_code == 200:
            line = r.json()
            created_lines.append(line)
            print(f"Created: {line['line_name']} (ID: {line['id']}, Type: {line['data_type']})")
    
    return created_lines

if __name__ == '__main__':
    print("=" * 50)
    print("Deleting existing production lines...")
    print("=" * 50)
    delete_lines()
    
    print("\n" + "=" * 50)
    print("Creating new production lines...")
    print("=" * 50)
    new_lines = create_test_lines()
    
    print("\n" + "=" * 50)
    print("Generating test data...")
    print("=" * 50)
    
    for line in new_lines:
        if line['data_type'] == 'measurement':
            mean = random.uniform(99.5, 100.5)
            std = random.uniform(0.05, 0.15)
            generate_measurement_data(line['id'], num_records=100, subgroup_size=5, mean=mean, std=std)
        else:
            sample_size = random.choice([50, 100, 200])
            defect_rate = random.uniform(0.01, 0.05)
            generate_attribute_data(line['id'], num_records=100, sample_size=sample_size, defect_rate=defect_rate)
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)
