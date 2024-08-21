from webapp import app, db
from flask import render_template, url_for
from webapp.forms import LoginForm, RegistrationForm, SearchUserForm, EditProfileForm, EmptyForm, PostForm
from flask import flash, redirect, request
from urllib.parse import urlsplit

from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sqa
from webapp.models import User, Post


from datetime import datetime, timezone
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index_page():
    
    # search_user_form = SearchUserForm()
    """ 
    if search_user_form.validate_on_submit():
        return redirect(url_for('user_page', username=search_user_form.username.data))
    """
    
    page = request.args.get('page', 1, type=int)
    query = None
    post_form = None

    if current_user.is_authenticated:
        post_form = PostForm()

        if post_form.validate_on_submit():
            new_post = Post(title=post_form.title.data, body=post_form.text.data, author=current_user)
            db.session.add(new_post)
            db.session.commit()
            flash('Uploaded your post.')
            return redirect(url_for('index_page'))
        
        query = current_user.get_my_and_followers_posts_query()
    else:
        query = sqa.select(Post).order_by(Post.timestamp.desc())

    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('index_page', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index_page', page=posts.prev_num) if posts.has_prev else None


    return render_template('index_page.html', title='Home page', 
                    posts=posts, post_form=post_form, next_url=next_url, prev_url=prev_url)

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
@login_required
def user_page(username):
    user = db.first_or_404(sqa.select(User).where(username == User.username))

    form = EmptyForm()

    page = request.args.get('page', 1, type=int)
    
    query = user.get_posts_query()
    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('user_page', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user_page', username=username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user_page.html', title=f'User {username}', 
                           user=user, form=form, posts=posts, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
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

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(User.username == username))

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index_page'))
        elif user == current_user:
            flash(f'You can\'t follow yourself!')
            return redirect(url_for('index_page'))
        
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}.')
        return redirect(url_for('user_page', username=username))
    else:
        return redirect(url_for('index_page'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow_user(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(User.username == username))

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index_page'))
        elif user == current_user:
            flash(f'You can\'t unfollow yourself!')
            return redirect(url_for('index_page'))
        
        if current_user.is_following(user):
            current_user.unfollow(user)
            db.session.commit()
            flash(f'You stopped following {username}.')
            return redirect(url_for('user_page', username=username))
        else:
            flash(f'You are not following {username}.')
            return redirect(url_for('user_page', username=username))
    else:
        return redirect(url_for('index_page'))