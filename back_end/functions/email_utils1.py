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

def send_control_chart_alert(abnormal_data):
    """
    发送控制图异常报警邮件
    
    Args:
        abnormal_data: 包含异常信息的字典，格式如下：
        {
            'abnormal_points': [异常点索引列表],
            'sample_defects_details': [样本缺陷详情列表],
            'u_list': [单位缺陷数列表],
            'c_list': [缺陷数列表],
            'n_list': [样本大小列表],
            'center_line': 中心线值,
            'ucl_list': [上控制限列表],
            'lcl_list': [下控制限列表]
        }
    
    Returns:
        bool: 邮件发送是否成功
    """
    subject = '控制图异常报警'
    
    # 构建邮件正文
    body = '控制图检测到异常！\n\n'
    body += f'异常点数量: {len(abnormal_data["abnormal_points"])}\n'
    body += f'异常点索引: {abnormal_data["abnormal_points"]}\n\n'
    
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
    return send_email(subject, body)
