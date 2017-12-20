# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header

from email import encoders
from django.conf import settings
import os


def send_email(to_list, subject, content, sender='noreply', attachments=[]):
    username = settings.CONST['email']['sender'][sender]['username']
    password = settings.CONST['email']['sender'][sender]['password']
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = username
    msg['To'] = ';'.join(to_list)
    msg.attach(MIMEText(content, "html", "utf-8"))
    for file in attachments:
        part = MIMEBase('application', 'octet-stream')  # 'octet-stream': binary data
        part.set_payload(open(file, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP()
    smtp.connect(settings.CONST['email']['smtp'])
    smtp.login(username, password)
    smtp.sendmail(username, to_list, msg.as_string())
    smtp.quit()
