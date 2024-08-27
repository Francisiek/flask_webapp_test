from webapp.auth import bp
from webapp import db
import sqlalchemy as sqa

from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from urllib.parse import urlsplit

from webapp.auth.forms import *
from webapp.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(form.username.data == User.username))

        if user is None or user.check_password(form.password.data) == False:
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login_page'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')

            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index_page')

            return redirect(next_page)

    return render_template('auth/login_page.html', title='Login', form=form)

@bp.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('index_page'))

from webapp.auth.email import send_password_reset_email
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request_page():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sqa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)

        flash(_('Password request send to that email address.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/reset_password_request_page.html', title='Reset password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_page(token):
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    user = User.verify_password_reset_token(token)

    if not user:
        return redirect(url_for('index_page'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been successfully reset.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/reset_password_page.html', title='Reset password', form=form)


@bp.route('/registration', methods=['GET', 'POST'])
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash(_('Congrats! You can now log in.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/registration_page.html', title='Register', form=form)

