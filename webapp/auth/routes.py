from webapp.auth import bp

from flask import render_template, url_for, flash, redirect, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from urllib.parse import urlsplit

from webapp.auth.forms import *
from webapp.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(form.username.data == User.username))

        if user is None or user.check_password(form.password.data) == False:
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login_page'))
        elif user.activated == False:
            flash(_('First activate your account.'))
            return redirect(url_for('auth.login_page'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')

            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index_page')

        return redirect(next_page)

    return render_template('auth/login_page.html', title='Login', form=form)

@bp.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('main.index_page'))

from webapp.auth.email import send_password_reset_email
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index_page'))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sqa.select(User).where(User.email == form.email.data)
        )
        if user.activated == True:
            send_password_reset_email(user)
        else:
            flash(_('First activate your account.'))
            return redirect(url_for('auth.login_page'))

        flash(_('Password request send to that email address.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/reset_password_request_page.html', title='Reset password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_page(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index_page'))

    user = User.verify_password_reset_token(token)

    if not user:
        return redirect(url_for('main.index_page'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been successfully reset.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/reset_password_page.html', title='Reset password', form=form)

from webapp.auth.email import send_activate_account_email
@bp.route('/registration', methods=['GET', 'POST'])
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index_page'))

    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, activated=False)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        send_activate_account_email(new_user)
        flash(_('Congrats! Please check your email and activate your account.'))
        return redirect(url_for('auth.login_page'))

    return render_template('auth/registration_page.html', title='Register', form=form)

@bp.route('/activate_account/<token>', methods=['GET', 'POST'])
def activate_account(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index_page'))

    if not token:
        return redirect(url_for('main.index_page'))

    user = User.verify_password_reset_token(token)

    if not user:
        flash(_('Invalid activation token'))
        return redirect(url_for('main.index_page'))

    user.activated = True
    flash(_('You can now log in.'))
    return redirect(url_for('auth.login_page'))


@bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account_page():
    if not current_user.is_authenticated:
        return redirect('main.index_page')

    form = DeleteAccountForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash(_('Wrong password!'))
            return redirect(url_for('auth.delete_account_page'))

        if form.sure.data == False:
            flash(_('You are not sure!?'))
            return redirect(url_for('auth.delete_account_page'))

        current_user.remove_user()
        db.session.commit()
        flash(_('Account successfully deleted.'))
        return redirect(url_for('main.index_page'))

    return render_template('auth/delete_account_page.html', title='Delete account', form=form)
