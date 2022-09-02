"""
Default error handling, on error responses by server
"""

from flask import jsonify, render_template, request
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """
    This method is called by flask on a 404 error.
    If it demands an HTML Page, the error page is rendered.
    Otherwise, a generic json 404 response is provided.
    """
    app.logger.error(error)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({ 'error': 'Not found' }), 404
    else:
        return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    This method is called by flask on a 500 error.
    If it demands an HTML Page, the error page is rendered.
    Otherwise, a generic json 500 response is provided.
    """
    app.logger.error(error)
    db.session.rollback()
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({ 'error': 'Internal Server Error' }), 500
    else:
        return render_template('errors/500.html'), 500
