#coding=utf-8
'''
Created on 11-9-20

@author: qiaoshun8888
'''
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib
import sys
import os
from django.template.context import Context
from settings import PROJECT_DIR
from django.template.loader import get_template

reload(sys)
sys.setdefaultencoding('utf-8');

class AuthInfo:
    SERVER = 'smtp.gmail.com'#'smtp.webfaction.com'
    USER = 'admin@woosuko.com'
    PASSWORD = 'sacn08311640'
    AUTHINFO = {'server':SERVER,'user':USER,'password':PASSWORD}
    FROM = 'admin@woosuko.com'

class TemplatePath:
    _base_path = os.path.join(PROJECT_DIR,'templates/mail/')
    REGISTER = os.path.join(_base_path, 'register.html')
    RESET_PASSWORD = os.path.join(_base_path, 'reset_password.html')

def send_register_email(email, account, password):
    # 读取邮件模版
    template_values = {}
    template_values['account'] = account
    template_values['password'] = password
    htmlText = get_template(TemplatePath.REGISTER).render(Context(template_values))
    subject =  'Welcome to Woosuko.com'
    sendEmail(email, subject, htmlText)
    return

def sendEmail(to, subject, htmlText):
    server = AuthInfo.SERVER
    user = AuthInfo.USER
    passwd = AuthInfo.PASSWORD
    if not (server and user and passwd) :
        print 'incomplete login info, exit now'
        return
    # 设定root信息
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = AuthInfo.FROM
    msgRoot['To'] = to
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    # Encapsulate the plain and HTML versions of the message body in an
    # ‘alternative’ part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    #设定纯文本信息
#    msgText = MIMEText(plainText, 'plain', 'utf-8')
#    msgAlternative.attach(msgText)

    #设定HTML信息
    msgText = MIMEText(htmlText, 'html', 'utf-8')
    msgAlternative.attach(msgText)

    #设定内置图片信息
#    fp = open('test.jpg', 'rb')
#    msgImage = MIMEImage(fp.read())
#    fp.close()
#    msgImage.add_header('Content-ID', '<image1>')
#    msgRoot.attach(msgImage)

    #发送邮件
    smtp = smtplib.SMTP()
    #设定调试级别，依情况而定
    smtp.set_debuglevel(1)
    smtp.connect(server)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(user, passwd)
    smtp.sendmail(AuthInfo.FROM, to, msgRoot.as_string())
    smtp.quit()

    return