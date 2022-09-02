from flask import jsonify, render_template, request
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(error)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({ 'error': 'Not found' })
        response.status_code = 404
        return response
    else:
        return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(error)
    db.session.rollback()
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({ 'error': 'Internal Server Error' })
        response.status_code = 500
        return response
    else:
        return render_template('errors/500.html'), 500
