from flask import render_template
from webapp import app, db

@app.errorhandler(404)
def error_404_page(error):
    return render_template('error_404_page.html'), 404


@app.errorhandler(500)
def error_500_page(error):
    db.session.rollback()
    return render_template('error_500_page.html'), 500