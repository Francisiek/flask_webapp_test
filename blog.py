import time
import asyncio
from datetime import datetime
from threading import Thread

import sqlalchemy as sqa
import sqlalchemy.orm as sqo
from webapp import create_app, db
from webapp.models import User, Post

app = create_app()

def all_time_cleanup():
    while True:
        with app.app_context():
            User.delete_inactiveted_accounts()
            db.session.commit()
        print('cleaned')
        time.sleep(app.config['CLEANUP_TIME_MINUTES']*60)

app.cleanup_func = all_time_cleanup
#Thread(target=app.cleanup_func, args=()).start()

@app.shell_context_processor
def shell_context():
    return {'sqa': sqa, 'sqo': sqo, 'app': app, 'db': db, 'User': User, 'Post': Post}
