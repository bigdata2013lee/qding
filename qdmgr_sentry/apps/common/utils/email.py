# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from django.conf import settings


def send_email(to_list, subject, content, sender='noreply', attachments=[]):
    username = settings.CONST['email']['sender'][sender]['username']
    password = settings.CONST['email']['sender'][sender]['password']
    msg = MIMEText(content.encode('utf-8'), 'text/html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = username
    msg['To'] = ';'.join(to_list)
    smtp = smtplib.SMTP()
    smtp.connect(settings.CONST['email']['smtp'])
    smtp.login(username, password)
    smtp.sendmail(username, to_list, msg.as_string())
    smtp.quit()
