
from flask import render_template, url_for, flash, redirect, request, g, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from datetime import datetime, timezone
import sqlalchemy as sqa

from webapp import db
from webapp.main.forms import EmptyForm, PostForm, EditProfileForm, SearchForm
from webapp.models import User, Post
from webapp.main import bp

@bp.before_request
def before_request():
    g.locale = str(get_locale())

    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()

from langdetect import detect, LangDetectException

@bp.route('/search')
@login_required
def search_page():
    if not g.search_form.validate():
        return redirect(url_for('main.index_page'))
    posts_per_page = current_app.config['POSTS_PER_PAGE']

    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.query.data, page, posts_per_page)

    next_url = url_for('main.search', q=g.search_form.query.data, page=page + 1) \
        if total > page * posts_per_page else None
    prev_url = url_for('main.search', q=g.search_form.query.data, page=page - 1) \
        if page > 1 else None

    return render_template('search.html', title=_('Search'), posts=posts,
                           prev_url=prev_url, next_url=next_url)

@bp.route('/', methods=['POST', 'GET'])
@bp.route('/index', methods=['POST', 'GET'])
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
            try:
                language = detect(post_form.text.data)
            except LangDetectException:
                language = ''

            new_post = Post(title=post_form.title.data, body=post_form.text.data,
                            author=current_user, language=language)

            db.session.add(new_post)
            db.session.commit()
            flash(_('Uploaded your post.'))
            return redirect(url_for('main.index_page'))
        
        query = current_user.get_my_and_followers_posts_query()
    else:
        query = sqa.select(Post).order_by(Post.timestamp.desc())

    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.index_page', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index_page', page=posts.prev_num) if posts.has_prev else None

    return render_template('index_page.html', title='Home page', 
                    posts=posts, post_form=post_form, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user_page(username):
    user = db.first_or_404(sqa.select(User).where(username == User.username))

    form = EmptyForm()

    page = request.args.get('page', 1, type=int)
    
    query = user.get_posts_query()
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.user_page', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user_page', username=username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user_page.html', title=f'User {username}', 
                           user=user, form=form, posts=posts, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile_page():
    if current_user.is_anonymous:
        return redirect(url_for('main.index_page'))

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about = form.about.data
        db.session.commit()
        flash(_('Succesfully updated profile.'))
        return redirect(url_for('main.user_page', username=current_user.username))
    elif request.method == 'GET':
        form.about.data = current_user.about
    
    return render_template('edit_profile_page.html', title='Edit profile', form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(User.username == username))

        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index_page'))
        elif user == current_user:
            flash(_('You can\'t follow yourself!'))
            return redirect(url_for('main.index_page'))
        
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s.', username=username))
        return redirect(url_for('main.user_page', username=username))
    else:
        return redirect(url_for('main.index_page'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow_user(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sqa.select(User).where(User.username == username))

        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index_page'))
        elif user == current_user:
            flash(_('You can\'t unfollow yourself!'))
            return redirect(url_for('main.index_page'))
        
        if current_user.is_following(user):
            current_user.unfollow(user)
            db.session.commit()
            flash(_('You stopped following %(username)s.', username=username))
            return redirect(url_for('main.user_page', username=username))
        else:
            flash(_('You are not following %(username)s.', username=username))
            return redirect(url_for('main.user_page', username=username))
    else:
        return redirect(url_for('main.index_page'))

from webapp.translate import translate

@bp.route('/translate', methods=['POST'])
def translate_text():
    if current_user.is_authenticated:
        data = request.get_json()
        return {'text': translate(data['text'],
                    data['source_language'],
                    data['destination_language']
                )}
    else:
        return {'text': _('You need to log in in order to translate.')}
