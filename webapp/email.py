from ctypes.wintypes import tagMSG

from flask import render_template
from flask_mail import Message
from webapp import mail, app

from threading import Thread

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, plain_body, html_body=None):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = plain_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(app, msg)).start()

from webapp.models import User
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    plain_body = render_template('email/reset_password.txt', user=user, token=token)
    html_body = render_template('email/reset_password.html', user=user, token=token)

    send_email('Blog: Password Reset', 'password_reset'+app.config['MAIL_SERVER'],
               [user.email], plain_body, html_body)