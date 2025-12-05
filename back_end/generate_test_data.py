#!/usr/bin/env python3
"""
测试数据生成程序
遍历dataset_split/val/images/目录中的所有图片，调用检测服务，将结果写入历史数据
"""

import os
import requests
import time
from datetime import datetime
from pathlib import Path

def generate_test_data():
    """生成测试数据的主函数"""
    
    # 配置路径和URL
    images_dir = "dataset_split/val/images"
    api_url = "http://localhost:5000/detectByImg"
    
    # 检查图片目录是否存在
    if not os.path.exists(images_dir):
        print(f"错误：图片目录 {images_dir} 不存在")
        return
    
    # 获取所有图片文件
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(Path(images_dir).glob(ext))
    
    if not image_files:
        print(f"警告：在 {images_dir} 中没有找到图片文件")
        return
    
    # 只处理前86张图片
    image_files = image_files[:86]
    print(f"找到 {len(image_files)} 张图片，开始生成测试数据...")
    
    # 统计信息
    success_count = 0
    fail_count = 0
    total_defects = 0
    
    # 遍历所有图片
    for i, image_path in enumerate(image_files, 1):
        filename = "test_"+datetime.now().strftime('%Y%m%d%H%M%S')+image_path.name
        print(f"\n[{i}/{len(image_files)}] 处理图片：{filename}")
        
        try:
            # 调用检测API
            with open(image_path, 'rb') as f:
                files = {'file': (filename, f, 'image/jpeg')}
                
                response = requests.post(api_url, files=files, timeout=30)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  ✓ 检测成功")
                    '''
                    # 获取JSON结果文件路径
                    json_filename = f"{Path(filename).stem}.json"
                    json_url = f"http://localhost:5000/results/jsons/{datetime.now().strftime('%Y-%m-%d')}/{json_filename}"
                    
                    # 尝试获取检测结果详情
                    try:
                        json_response = requests.get(json_url)
                        if json_response.status_code == 200:
                            result_data = json_response.json()
                            defect_count = result_data.get('detection_total_cnts', 0)
                            total_defects += defect_count
                            print(f"  - 缺陷数量：{defect_count}")
                            if defect_count > 0:
                                print(f"  - 缺陷类型：{result_data.get('detection_classes', [])}")
                        else:
                            print(f"  - 无法获取详细结果")
                    except Exception as e:
                        print(f"  - 获取详细结果失败：{str(e)}")
                        
                else:
                    fail_count += 1
                    print(f"  ✗ 检测失败：HTTP {response.status_code}")
                    try:
                        error_msg = response.json().get('error', '未知错误')
                        print(f"  - 错误信息：{error_msg}")
                    except:
                        print(f"  - 错误信息：{response.text}")
                       ''' 
        except requests.exceptions.RequestException as e:
            fail_count += 1
            print(f"  ✗ 网络请求失败：{str(e)}")
        except Exception as e:
            fail_count += 1
            print(f"  ✗ 处理失败：{str(e)}")
        
        # 短暂延迟，避免过快请求
        time.sleep(0.3)
    
    # 输出统计信息
    print(f"\n{'='*50}")
    print(f"测试数据生成完成！")
    print(f"总图片数：{len(image_files)}")
    print(f"成功：{success_count}")
    print(f"失败：{fail_count}")
    print(f"总缺陷数：{total_defects}")
    print(f"{'='*50}")

def check_services():
    """检查后端服务是否正常运行"""
    try:
        response = requests.get("http://localhost:5000/images", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务正常运行")
            return True
        else:
            print(f"✗ 后端服务异常：HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ 无法连接后端服务：{str(e)}")
        print("请确保后端服务已启动：cd back_end && python app.py")
        return False

if __name__ == "__main__":
    print("测试数据生成程序")
    print("="*50)
    
    # 检查服务状态
    if not check_services():
        exit(1)
    
    # 生成测试数据
    generate_test_data()
    
    print("\n程序执行完成！")