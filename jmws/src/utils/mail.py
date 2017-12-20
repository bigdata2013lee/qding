# coding=utf-8

import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders

from conf.qd_conf import CONF

mail_from = CONF.get("mail_from")

def send_email(to_list, subject, content, attachments=[]):
    """
    发送邮件
    :param to_list: T-list, 收件人列表
    :param subject: T-str, 主题
    :param content: T-str, 内容
    :param attachments: T-list[(name#str, data#bytes),...], 附件名称及数据
    :return:
    """
    username = mail_from.get("user")
    password = mail_from.get("password")
    smtp_server = mail_from.get("smtp_server")

    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = username
    msg['To'] = ';'.join(to_list)
    msg.attach(MIMEText(content, "html", "utf-8"))

    for attachment in attachments:
        part = MIMEBase('application', 'octet-stream')  # 'octet-stream': binary data
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % attachment[0])
        part.set_payload(attachment[1])
        encoders.encode_base64(part)
        msg.attach(part)

    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
    smtp.login(username, password)
    smtp.sendmail(username, to_list, msg.as_string())
    smtp.quit()


