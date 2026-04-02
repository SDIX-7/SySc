"""
批量注释掉 HTML 模板中的 circle-number span 元素
"""

import os
import re

def comment_out_circle_numbers(file_path):
    """注释掉指定文件中所有的 circle-number span"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 <span class="circle-number">数字</span> 模式并注释掉
    pattern = r'<span class="circle-number">([^<]+)</span>'
    
    def comment_match(match):
        original = match.group(0)
        return f'<!-- {original} -->'
    
    new_content = re.sub(pattern, comment_match, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 统计修改数量
    count = len(re.findall(pattern, content))
    return count

# 要处理的文件
files = [
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_normal_distribution.html',
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_skewed_distribution.html',
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\spc_mixed_distribution.html',
    r'D:\py\质量信息系统\flask+vue\back_end\templates\reports\ocap_response_report.html',
]

print("=" * 60)
print("批量注释 circle-number span 元素")
print("=" * 60)

total = 0
for file_path in files:
    if os.path.exists(file_path):
        count = comment_out_circle_numbers(file_path)
        total += count
        filename = os.path.basename(file_path)
        print(f"✓ {filename}: 注释了 {count} 处")
    else:
        print(f"✗ 文件不存在: {file_path}")

print("=" * 60)
print(f"总计: 注释了 {total} 处 circle-number 元素")
print("=" * 60)
