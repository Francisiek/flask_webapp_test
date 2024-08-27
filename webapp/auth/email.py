from flask import render_template, current_app
from webapp.email import send_email

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    plain_body = render_template('email/reset_password.txt', user=user, token=token)
    html_body = render_template('email/reset_password.html', user=user, token=token)

    send_email('Blog: Password Reset', 'password_reset'+current_app.config['MAIL_SERVER'],
               [user.email], plain_body, html_body)