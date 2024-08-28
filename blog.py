import sqlalchemy as sqa
import sqlalchemy.orm as sqo
from webapp import create_app, db
from webapp.models import User, Post

app = create_app()

@app.shell_context_processor
def shell_context():
    return {'sqa': sqa, 'sqo': sqo, 'app': app, 'db': db, 'User': User, 'Post': Post}
