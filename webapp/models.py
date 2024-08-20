from typing import Optional
from datetime import datetime, timezone
import sqlalchemy as SA
import sqlalchemy.orm as SO
from webapp import db, login


from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
class User(UserMixin, db.Model):
    id:         SO.Mapped[int] = SO.mapped_column(primary_key=True)
    username:   SO.Mapped[str] = SO.mapped_column(SA.String(64), index=True, unique=True)
    email:      SO.Mapped[str] = SO.mapped_column(SA.String(128), index=True, unique=True)
    hashed_pass:SO.Mapped[Optional[str]] = SO.mapped_column(SA.String(256))

    posts:      SO.WriteOnlyMapped['Post'] = SO.relationship(back_populates='author')


    def set_password(self, password):
        self.hashed_pass = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_pass, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Post(db.Model):
    id:         SO.Mapped[int] = SO.mapped_column(primary_key=True)
    user_id:    SO.Mapped[int] = SO.mapped_column(SA.ForeignKey(User.id), index=True)
    timestamp:  SO.Mapped[datetime] = SO.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    title:      SO.Mapped[str] = SO.mapped_column(SA.String(64), index=True)
    body:       SO.Mapped[str] = SO.mapped_column(SA.String(4096))

    author:     SO.Mapped[User] = SO.relationship(back_populates='posts')

    def __repr__(self):
        return f'<Post {self.title} by {self.user_id}'
    