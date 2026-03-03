import smtplib
from email.mime.text import MIMEText
from email.header import Header
from typing import Dict, Any
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or os.getenv('SMTP_PASSWORD')


def analyze_control_chart(chart_data: Dict[str, Any]) -> str:
    try:
        abnormal_points = chart_data.get('abnormal_points', [])
        abnormal_rules = chart_data.get('abnormal_rules', {})
        statistics = chart_data.get('statistics', {})
        
        violated_rules = [rule for rule, points in abnormal_rules.items() if points]
        
        prompt = f"""
        请分析以下控制图异常数据，提供800字以内的分析结果：
        
        1. 异常点数量：{len(abnormal_points)}个
        2. 违反的异常规则：{violated_rules}
        3. 总样本数：{statistics.get('total_samples', 0)}
        4. 总缺陷数：{statistics.get('total_defects', 0)}
        5. 平均单位缺陷数：{chart_data.get('center_line', 0):.4f}
        
        请分析可能的原因、严重程度，并提供改进建议。
        """
        
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return "DeepSeek分析失败：未设置DEEPSEEK_API_KEY环境变量"
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一位质量控制专家，擅长分析控制图异常数据。"},
                {"role": "user", "content": prompt.strip()},
            ],
            stream=False,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek分析失败：{str(e)}"


def send_email(subject: str, body: str, to_email: str = '2395365918@qq.com') -> bool:
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = '3600094151@qq.com'
        msg['To'] = to_email

        smtp_server = 'smtp.qq.com'
        smtp_port = 465
        sender_email = '3600094151@qq.com'
        
        password = SMTP_PASSWORD
        if not password:
            print('❌ 邮件发送失败: SMTP_PASSWORD未配置')
            return False

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, [to_email], msg.as_string())
        print('✅ 邮件发送成功')
        return True
    except Exception as e:
        if "(-1," in str(e):
            print('⚠️ 邮件可能已发送，但连接关闭异常（可忽略）')
            return True
        else:
            print('❌ 邮件发送错误:', e)
            return False


def send_control_chart_alert(abnormal_data: Dict[str, Any], recipient_email: str = '2395365918@qq.com') -> bool:
    subject = '控制图异常报警'
    
    analysis_result = analyze_control_chart(abnormal_data)
    
    violated_rules = [rule for rule, points in abnormal_data.get('abnormal_rules', {}).items() if points]
    
    rule_names = {
        1: "规则1：1点外（点落在A区以外，即超过UCL或低于LCL）",
        2: "规则2：9单侧（连续9个点落在中心线同一侧）",
        3: "规则3：6连串（连续6个点递增或递减）",
        4: "规则4：14交替（连续14个点中相邻点交替上下）",
        5: "规则5：2/3A（连续3个点中有2个点落在中心线同一侧的B区以外）",
        6: "规则6：4/5C（连续5个点中有4个点落在中心线同一侧的C区以外）",
        7: "规则7：15全C（连续15个点落在中心线两侧的C区内）",
        8: "规则8：8缺C（连续8个点落在中心线两侧且无一在C区内）"
    }
    
    body = '控制图检测到异常！\n\n'
    body += '===== DeepSeek AI分析结果 =====\n'
    body += analysis_result + '\n\n'
    body += '===== 违反的异常规则 =====\n'
    if violated_rules:
        for rule in sorted(violated_rules):
            body += f"- {rule_names.get(rule, f'规则{rule}')}\n"
    else:
        body += "未检测到违反的规则\n"
    body += '\n'
    body += '===== 原始异常数据 =====\n'
    body += f'异常点数量: {len(abnormal_data["abnormal_points"]) if "abnormal_points" in abnormal_data else 0}\n'
    body += f'异常点索引: {abnormal_data.get("abnormal_points", [])}\n\n'
    
    body += '异常点详细信息：\n'
    for i, point_index in enumerate(abnormal_data["abnormal_points"]):
        body += f'\n--- 异常点 {i+1}（索引: {point_index}）---\n'
        
        if point_index < len(abnormal_data["sample_defects_details"]):
            sample = abnormal_data["sample_defects_details"][point_index]
            body += f'样本大小: {sample["sample_size"]} 张PCB\n'
            body += f'总缺陷数: {sample["total_defects"]}\n'
            body += f'每张PCB缺陷数: {sample["defects_per_pcb"]}\n'
            body += f'PCB名称: {sample["pcb_names"]}\n'
            body += f'捕获时间: {sample["capture_times"]}\n'
        
        if point_index < len(abnormal_data["u_list"]):
            body += f'单位缺陷数(u): {abnormal_data["u_list"][point_index]:.4f}\n'
            body += f'缺陷数(c): {abnormal_data["c_list"][point_index]}\n'
            body += f'样本大小(n): {abnormal_data["n_list"][point_index]}\n'
            body += f'中心线(u_bar): {abnormal_data["center_line"]:.4f}\n'
            body += f'上控制限(UCL): {abnormal_data["ucl_list"][point_index]:.4f}\n'
            body += f'下控制限(LCL): {abnormal_data["lcl_list"][point_index]:.4f}\n'
    
    body += '\n请及时检查生产过程！'
    
    return send_email(subject, body, recipient_email)
