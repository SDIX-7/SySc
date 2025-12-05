import smtplib
from email.mime.text import MIMEText
from email.header import Header

subject = '邮件主题'
body = '邮件正文'

msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')
msg['From'] = '3600094151@qq.com'
msg['To'] = '2395365918@qq.com'

smtp_server = 'smtp.qq.com'
smtp_port = 465  # 改为 465
sender_email = '3600094151@qq.com'
password = 'rcuinubewmifdbgj'  # 替换为真实授权码

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, [msg['To']], msg.as_string())
        print('✅ 邮件发送成功')
except smtplib.SMTPException as e:
    print('❌ SMTP 错误:', e)
except Exception as e:
    # 检查是否是连接关闭异常（如 (-1, ...)）
    if "(-1," in str(e):
        print('⚠️ 邮件可能已发送，但连接关闭异常（可忽略）')
    else:
        print('❌ 其他错误:', e)