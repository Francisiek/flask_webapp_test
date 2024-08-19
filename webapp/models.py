from typing import Optional
import sqlalchemy as SA
import sqlalchemy.orm as SO
from webapp import db

class User(db.Model):
    id:         SO.Mapped[int] = SO.mapped_column(primary_key=True)
    username:   SO.Mapped[str] = SO.mapped_column(SA.String(64), index=True, unique=True)
    email:      SO.Mapped[str] = SO.mapped_column(SA.String(128), index=True, unique=True)
    hashed_pass:SO.Mapped[Optional[str]] = SO.mapped_column(SA.String(256))

    def __repr__(self):
        return f'<User {self.username}>'
