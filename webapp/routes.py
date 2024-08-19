from webapp import app
from flask import render_template, url_for
from webapp.forms import LoginForm

@app.route('/')
@app.route('/index')
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

    return render_template('index_page.html', title='Test page', user=mock_user, posts=mock_posts)

from flask import flash, redirect

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        flash(f"User {form.username.data} with setting remember me={form.remember_me.data}")
        return redirect(url_for('index_page'))
    else:
        return render_template('login_page.html', title='Login', form=form)