from webapp import app, db
from flask import render_template, url_for
from webapp.forms import LoginForm, RegistrationForm, SearchUserForm, EditProfileForm
from flask import flash, redirect, request
from urllib.parse import urlsplit

from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sqa
from webapp.models import User


from datetime import datetime, timezone
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
#@login_required
def index_page():
    mock_user = {'username': 'Garry'}
    mock_posts = [
        {
            'author': {'username': 'David'},
            'body': 'What a shit?'
        },
        {
            'author': {'username': 'David'},
            'body': 'Ojjjj taaak!'
        },
        {
            'author': {'username': 'Garry'},
            'body': 'No way this could work'
        }
    ]
    search_user_form = SearchUserForm()

    if search_user_form.validate_on_submit():
        #flash('Yey')
        return redirect(url_for('user_page', username=search_user_form.username.data))

    return render_template('index_page.html', title='Test page', posts=mock_posts, search_user_form=search_user_form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(form.username.data == User.username))

        if user == None or user.check_password(form.password.data) == False:
            flash('Invalid username or password')
            return redirect(url_for('login_page'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')

            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index_page')

            return redirect(next_page)

    return render_template('login_page.html', title='Login', form=form)
    
@app.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('index_page'))

@app.route('/registration', methods=['GET', 'POST'])
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for('index_page'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit() 

        flash('Congrats! You can now log in.')
        return redirect(url_for('login_page'))

    return render_template('registration_page.html', title='Register', form=form)

@app.route('/user/<username>')
#@login_required
def user_page(username):
    user = db.first_or_404(sqa.select(User).where(username == User.username))

    posts = [
        {'author': user, 'title': 'My ugly day', 'body': 'My post heeeee'},
        {'author': user, 'title': 'Oh my duck', 'body': 'My post niuuuuuu'},
    ]

    return render_template('user_page.html', title=f'User {username}', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile_page():
    if current_user.is_anonymous:
        return redirect(url_for('index_page'))

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about = form.about.data
        db.session.commit()
        flash('Succesfully updated profile.')
        return redirect(url_for('user_page', username=current_user.username))
    elif request.method == 'GET':
        form.about.data = current_user.about
    
    return render_template('edit_profile_page.html', title='Edit profile', form=form)
