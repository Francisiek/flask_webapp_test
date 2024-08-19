from typing import Optional
from datetime import datetime, timezone
import sqlalchemy as SA
import sqlalchemy.orm as SO
from webapp import db

class User(db.Model):
    id:         SO.Mapped[int] = SO.mapped_column(primary_key=True)
    username:   SO.Mapped[str] = SO.mapped_column(SA.String(64), index=True, unique=True)
    email:      SO.Mapped[str] = SO.mapped_column(SA.String(128), index=True, unique=True)
    hashed_pass:SO.Mapped[Optional[str]] = SO.mapped_column(SA.String(256))

    posts:      SO.WriteOnlyMapped['Post'] = SO.relationship(back_populates='author')

    def __repr__(self):
        return f'<User {self.username}>'
    
class Post(db.Model):
    id:         SO.Mapped[int] = SO.mapped_column(primary_key=True)
    user_id:    SO.Mapped[int] = SO.mapped_column(SA.ForeignKey(User.id), index=True)
    timestamp:  SO.Mapped[datetime] = SO.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    title:      SO.Mapped[str] = SO.mapped_column(SA.String(64), index=True)
    body:       SO.Mapped[str] = SO.mapped_column(SA.String(4096))

    author:     SO.Mapped[User] = SO.relationship(back_populates='posts')

    def __repr__(self):
        return f'<Post {self.title} by {self.user_id}'
    