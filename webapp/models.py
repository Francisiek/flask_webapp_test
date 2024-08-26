from typing import Optional
from datetime import datetime, timezone
import sqlalchemy as sqa
import sqlalchemy.orm as sqo
from webapp import db, login, app

followers_table = sqa.Table('followers', db.metadata, 
                    sqa.Column('follower_id', sqa.Integer, sqa.ForeignKey('user.id'), primary_key=True), 
                    sqa.Column('followed_id', sqa.Integer, sqa.ForeignKey('user.id'), primary_key=True)
            )


from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

from time import time
import jwt

class User(UserMixin, db.Model):
    id:         sqo.Mapped[int] = sqo.mapped_column(primary_key=True)
    username:   sqo.Mapped[str] = sqo.mapped_column(sqa.String(64), index=True, unique=True)
    email:      sqo.Mapped[str] = sqo.mapped_column(sqa.String(128), index=True, unique=True)
    hashed_pass:sqo.Mapped[Optional[str]] = sqo.mapped_column(sqa.String(256))
    about:      sqo.Mapped[Optional[str]] = sqo.mapped_column(sqa.String(4096))
    last_seen:  sqo.Mapped[Optional[datetime]] = sqo.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    posts:      sqo.WriteOnlyMapped['Post'] = sqo.relationship(back_populates='author')

    followers:  sqo.WriteOnlyMapped['User'] = sqo.relationship(
        secondary=followers_table, primaryjoin=(followers_table.c.followed_id == id),
        secondaryjoin=(followers_table.c.follower_id == id), back_populates='following' 
    )

    following:   sqo.WriteOnlyMapped['User'] = sqo.relationship(
        secondary=followers_table, primaryjoin=(followers_table.c.follower_id == id),
        secondaryjoin=(followers_table.c.followed_id == id), back_populates='followers'
    )

    def set_password(self, password):
        self.hashed_pass = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_pass, password)

    def get_reset_password_token(self, expires_in=app.config['PASSWORD_RESET_EXPIRE_TIME_SECONDS']):
        token = jwt.encode(
            {'user_id': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
        return token

    @staticmethod
    def verify_password_reset_token(token):
        try:
            user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
        except:
            return None

        return db.session.get(User, user_id)


    def avatar(self, size):
        hash = md5((self.username+self.email+str(2384129234)).encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{hash}?d=identicon&s={size}'
    
    def is_following(self, user) -> bool:
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def followers_counter(self):
        query = sqa.select(sqa.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)

    def following_counter(self):
        query = sqa.select(sqa.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)

    def get_followers_posts_query(self):
        Author = sqo.aliased(User)
        Follower = sqo.aliased(User)

        query = (
            sqa.select(Post).join(Post.author.of_type(Author)).join(Author.followers.of_type(Follower))
            .where(Follower.id == self.id)
            .order_by(Post.timestamp.desc())
        )

        return query
    
    def get_followers_posts(self):
        return db.session.scalars(self.get_followers_posts_query()).all()
    
    def get_my_and_followers_posts_query(self):
        Author = sqo.aliased(User)
        Follower = sqo.aliased(User)

        query = (
            sqa.select(Post).join(Post.author.of_type(Author)).join(Author.followers.of_type(Follower), isouter=True)
            .where(sqa.or_(
                Author.id == self.id,
                Follower.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

        return query
    
    def get_my_and_followers_posts(self):
        return db.session.scalars(self.get_my_and_followers_posts_query()).all()

    def get_posts_query(self):
        return self.posts.select().order_by(Post.timestamp.desc())

    def get_posts(self):
        return db.session.scalars(self.get_posts_query()).all()

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Post(db.Model):
    id:         sqo.Mapped[int] = sqo.mapped_column(primary_key=True)
    user_id:    sqo.Mapped[int] = sqo.mapped_column(sqa.ForeignKey(User.id), index=True)
    timestamp:  sqo.Mapped[datetime] = sqo.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    title:      sqo.Mapped[str] = sqo.mapped_column(sqa.String(64), index=True)
    body:       sqo.Mapped[str] = sqo.mapped_column(sqa.String(4096))
    language:   sqo.Mapped[Optional[str]] = sqo.mapped_column(sqa.String(8))

    author:     sqo.Mapped[User] = sqo.relationship(back_populates='posts')

    def __repr__(self):
        return f'<Post {self.title} by {self.user_id}'
    