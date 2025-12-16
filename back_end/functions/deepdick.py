# Please install OpenAI SDK first: `pip3 install openai`
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any

# 加载.env文件
load_dotenv()


def analyze_control_chart(chart_data: Dict[str, Any]) -> str:
    """
    分析控制图异常数据
    
    Args:
        chart_data: 控制图数据字典，包含异常信息
    
    Returns:
        str: DeepSeek分析结果
    """
    try:
        # 提取关键信息用于分析
        abnormal_points = chart_data.get('abnormal_points', [])
        abnormal_rules = chart_data.get('abnormal_rules', {})
        statistics = chart_data.get('statistics', {})
        
        # 确定违反的规则
        violated_rules = [rule for rule, points in abnormal_rules.items() if points]
        
        # 构建prompt
        prompt = f"""
        请分析以下控制图异常数据，提供800字以内的分析结果：
        
        1. 异常点数量：{len(abnormal_points)}个
        2. 违反的异常规则：{violated_rules}
        3. 总样本数：{statistics.get('total_samples', 0)}
        4. 总缺陷数：{statistics.get('total_defects', 0)}
        5. 平均单位缺陷数：{chart_data.get('center_line', 0):.4f}
        
        请分析可能的原因、严重程度，并提供改进建议。
        """
        
        # 在函数内部初始化OpenAI客户端，避免模块导入时出错
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return "DeepSeek分析失败：未设置DEEPSEEK_API_KEY环境变量"
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一位质量控制专家，擅长分析控制图异常数据。"},
                {"role": "user", "content": prompt.strip()},
            ],
            stream=False,
            max_tokens=1000  # 控制输出长度
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # 错误处理，确保即使API调用失败也能正常返回
        return f"DeepSeek分析失败：{str(e)}"