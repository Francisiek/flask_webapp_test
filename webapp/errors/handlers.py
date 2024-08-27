from flask import render_template
from webapp import db
from webapp.errors import bp

@bp.app_errorhandler(404)
def error_404_page(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def error_500_page(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500