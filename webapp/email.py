from flask import current_app
from flask_mail import Message
from threading import Thread

from webapp import mail

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, plain_body, html_body=None):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = plain_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(current_app._get_current_object(), msg)).start()