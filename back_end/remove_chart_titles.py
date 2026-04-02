"""
批量移除图表标题中的文字
"""

import os
import re

def remove_chart_titles(file_path):
    """移除指定文件中所有图表标题的文字"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 <div class="chart-title">...</div> 模式
    # 匹配带有注释的 circle-number span 的情况
    pattern = r'<div class="chart-title">\s*<!--[^>]*-->\s*([^<]*(?:<[^>]*>[^<]*</[^>]*>[^<]*)*)</div>'
    
    # 替换为空 div
    new_content = re.sub(pattern, '<div class="chart-title"></div>', content)
    
    # 也处理没有内容的情况
    pattern2 = r'<div class="chart-title">\s*<!--[^>]*-->\s*</div>'
    new_content = re.sub(pattern2, '<div class="chart-title"></div>', new_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 统计修改数量
    count = len(re.findall(pattern, content))
    return count

# 更简单的方法：直接替换所有 chart-title div 中的内容
def remove_chart_titles_simple(file_path):
    """移除图表标题 div 中的内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配包含 circle-number 注释的 chart-title div
    # 模式: <div class="chart-title"> <!-- <span...--> --> TITLE </div>
    pattern = r'(<div class="chart-title">)\s*<!--.*?-->\s*.*?(</div>)'
    
    def clean_match(match):
        return match.group(1) + match.group(2)
    
    new_content = re.sub(pattern, clean_match, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    count = len(re.findall(pattern, content))
    return count

# 要处理的文件
files = [
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_normal_distribution.html',
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_skewed_distribution.html',
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_mixed_distribution.html',
]

print("=" * 60)
print("批量移除图表标题文字")
print("=" * 60)

total = 0
for file_path in files:
    if os.path.exists(file_path):
        count = remove_chart_titles_simple(file_path)
        total += count
        filename = os.path.basename(file_path)
        print(f"✓ {filename}: 移除了 {count} 处标题")
    else:
        print(f"✗ 文件不存在: {file_path}")

print("=" * 60)
print(f"总计: 移除了 {total} 处图表标题文字")
print("=" * 60)
