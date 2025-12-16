import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_email(subject, body, to_email='xxxxxxxxxx@qq.com'):
    """
    发送邮件函数
    
    Args:
        subject: 邮件主题
        body: 邮件正文
        to_email: 收件人邮箱，默认为xxxxxxxxxx@qq.com
    
    Returns:
        bool: 邮件发送是否成功
    """
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = 'xxxxxxxxxx@qq.com'
        msg['To'] = to_email

        smtp_server = 'smtp.qq.com'
        smtp_port = 465
        sender_email = 'xxxxxxxxxx@qq.com'
        password = 'xxxxxxxxxxxx'  # 替换为真实授权码

        # 使用SMTP_SSL连接
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, [to_email], msg.as_string())
        print('✅ 邮件发送成功')
        return True
    except Exception as e:
        # 检查是否是连接关闭异常（如 (-1, ...)）
        if "(-1," in str(e):
            print('⚠️ 邮件可能已发送，但连接关闭异常（可忽略）')
            return True
        else:
            print('❌ 邮件发送错误:', e)
            return False

from .deepdick import analyze_control_chart

def send_control_chart_alert(abnormal_data, recipient_email='xxxxxxxxxx@qq.com'):
    """
    发送控制图异常报警邮件
    
    Args:
        abnormal_data: 包含异常信息的字典，格式如下：
        {
            'abnormal_points': [异常点索引列表],
            'abnormal_rules': {规则号: [异常点索引列表]},  # 违反的异常规则
            'sample_defects_details': [样本缺陷详情列表],
            'u_list': [单位缺陷数列表],
            'c_list': [缺陷数列表],
            'n_list': [样本大小列表],
            'center_line': 中心线值,
            'ucl_list': [上控制限列表],
            'lcl_list': [下控制限列表]
        }
        recipient_email: 收件人邮箱，默认为xxxxxxxxxx@qq.com
    
    Returns:
        bool: 邮件发送是否成功
    """
    subject = '控制图异常报警'
    
    # 获取DeepSeek分析结果
    analysis_result = analyze_control_chart(abnormal_data)
    
    # 确定违反的规则
    violated_rules = [rule for rule, points in abnormal_data.get('abnormal_rules', {}).items() if points]
    
    # 规则名称映射
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
    
    # 构建邮件正文
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
    
    # 添加异常点详细信息
    body += '异常点详细信息：\n'
    for i, point_index in enumerate(abnormal_data["abnormal_points"]):
        body += f'\n--- 异常点 {i+1}（索引: {point_index}）---\n'
        
        # 样本缺陷详情
        if point_index < len(abnormal_data["sample_defects_details"]):
            sample = abnormal_data["sample_defects_details"][point_index]
            body += f'样本大小: {sample["sample_size"]} 张PCB\n'
            body += f'总缺陷数: {sample["total_defects"]}\n'
            body += f'每张PCB缺陷数: {sample["defects_per_pcb"]}\n'
            body += f'PCB名称: {sample["pcb_names"]}\n'
            body += f'捕获时间: {sample["capture_times"]}\n'
        
        # 控制图数据
        if point_index < len(abnormal_data["u_list"]):
            body += f'单位缺陷数(u): {abnormal_data["u_list"][point_index]:.4f}\n'
            body += f'缺陷数(c): {abnormal_data["c_list"][point_index]}\n'
            body += f'样本大小(n): {abnormal_data["n_list"][point_index]}\n'
            body += f'中心线(u_bar): {abnormal_data["center_line"]:.4f}\n'
            body += f'上控制限(UCL): {abnormal_data["ucl_list"][point_index]:.4f}\n'
            body += f'下控制限(LCL): {abnormal_data["lcl_list"][point_index]:.4f}\n'
    
    body += '\n请及时检查生产过程！'
    
    # 发送邮件
    return send_email(subject, body, recipient_email)