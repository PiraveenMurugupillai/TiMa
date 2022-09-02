"""
All served Web API's are listed in this file
"""

from app import app, db
from app.models import User, WorkingHours
import datetime
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    """
    This method verifies, if a username and password match.
    If the provided credentials match, the user gets his own user object as response.
    Otherwise, the user will receive an error response.
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return jsonify({'error': 'Username or password is wrong.'}), 400


@basic_auth.error_handler
def basic_auth_error(status):
    """
    This is a basic handler to response only with given status code from basic auth
    """
    return '', status


@token_auth.verify_token
def verify_token(token):
    """
    This is a basic handler to verify if a given token is correct.
    """
    return User.check_token(token) if token else jsonify({'error': 'Invalid authorization token.'}), 401


@token_auth.error_handler
def token_auth_error(status):
    """
    This is a basic handler to response only with given status code from token auth
    """
    return jsonify({'error': 'Invalid authorization token.'}), status


@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """
    This method responses to a user with an authorization token, if given credentials are correct
    """
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})


@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """
    This method revokes the current active token, so that it is not usable anymore
    """
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204


@app.route('/api/users', methods=['GET'])
@token_auth.login_required
def get_user():
    """
    This method responses with fetched user data accordingly to given authorization token
    """
    data = User.query.get_or_404(token_auth.current_user().id).to_dict()
    return jsonify(data)


@app.route('/api/users', methods=['POST'])
def create_new_user():
    """
    This method takes all necessary data to create a new user. With those data, a new user is created and stored
    in the database. If some requirements are not met, the user will get an error.
    """
    try:
        # try to read all required data from json body
        user_data = request.get_json()
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']
        company = user_data['company']
        job = user_data['job']
        target_time = user_data['target_time']

        # check if there is already a user with desired username or email
        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(username=username).first()
        if (existing_username is not None) or (existing_email is not None):
            return jsonify({'error': 'Please use a different username or email'}), 400

        # check if given target_time mets the requirements
        if float(target_time) < 0 or float(target_time) > 24:
            return jsonify({'error': 'Please enter target time in a valid range (0 to 24)'}), 400

        # create user and save it to database
        user = User(username=username, email=email, company=company, job=job, target_time=target_time)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 201
    except Exception as error:
        app.logger.error(error)
        return '', 400


@app.route('/api/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    """
    This methods allows a user to change his own data due to given conditions
    """
    try:
        # try to retrieve json body. If it fails, the fallbock of an empty body is taken.
        user_data = request.get_json()
    except:
        user_data = {}

    user = User.query.get(token_auth.current_user().id)
    for key in user_data.keys():
        # check if given json key is an attribute of a user
        if key in user.to_dict().keys():
            # if it's username, further validation is done (no one else should have the new username)
            if key == 'username':
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user is not None and existing_user.id != token_auth.current_user().id:
                    return jsonify({'error': 'Given username is already taken. Choose another one.'}), 400

            # if it's email, further validation is done (no one else should have the new email address)
            if key == 'email':
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user is not None and existing_user.id != token_auth.current_user().id:
                    return jsonify({'error': 'Given e-mail address is already taken. Choose another one.'}), 400

            # if key is part of user attribute, it will be updated
            setattr(user, key, user_data[key])

    # save everything to database
    db.session.commit()
    return jsonify(user.to_dict())


@app.route('/api/working-hours', methods=['GET'])
@token_auth.login_required
def get_working_hours():
    """
    This method responses with all tracked working hours of the user
    """
    data = WorkingHours.query.filter_by(user_id=token_auth.current_user().id).all()
    return jsonify(list(map(lambda x: x.to_dict(), data)))


@app.route('/api/working-hours/<int:id>', methods=['GET'])
@token_auth.login_required
def get_working_hours_by_id(id):
    """
    This method responses with a specific tracked working hours identified by the id of the user
    If the record is not from the user, the user will receive a 404 response
    """
    data = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, id=id).first()
    if data is None:
        return jsonify({'error': 'There is no entry with given id.'}), 404

    return jsonify(data.to_dict())


@app.route('/api/working-hours', methods=['POST'])
@token_auth.login_required
def add_working_hours():
    """
    This methods allows the user to create new records of working hours.
    The date must be in Format YYYY-MM-DD, provided working_hours must match the conditions (between 0 & 24)
    """
    try:
        # try to read all required data from json body
        hours = request.get_json()
        date = datetime.datetime.strptime(hours['date'], '%Y-%m-%d')
        working_hours = hours['working_hours']
        comment = ''
        # if comment is provided, it will be taken. Otherwise, it's an empty string
        if 'comment' in hours.keys():
            comment = hours['comment']

        # check if there is already a record of given user for given date.
        existing_hours = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, date=date).first()
        if existing_hours is not None:
            return jsonify({'error': 'There is already an entry for given date.'}), 400

        # check if provided working hours mets the requirements
        if float(working_hours) < 0 or float(working_hours) > 24:
            return jsonify({'error': 'Working hours must be between 0 and 24'}), 400

        # create record and save it to database
        working_hours = WorkingHours(date=date, working_hours=working_hours, comment=comment,
                                     user_id=token_auth.current_user().id)
        db.session.add(working_hours)
        db.session.commit()
        return jsonify(working_hours.to_dict()), 201
    except Exception as error:
        app.logger.error(error)
        return '', 400


@app.route('/api/working-hours/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_working_hours(id):
    """
    This method allows the user to update an existing record to working hours.
    If all requirements are met, the changed record is responded to the user.
    """
    try:
        # try to retrieve json body. If it fails, the fallbock of an empty body is taken.
        hours_data = request.get_json()
    except:
        hours_data = {}

    # check if there is already a record to be updated
    hours_entry = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, id=id).first()
    if hours_entry is None:
        return jsonify({'error': 'There is no entry for given id.'}), 404

    # if working hours are updated, it has to satisfy the requirements
    if 'working_hours' in hours_data.keys():
        if 0 <= hours_data['working_hours'] <= 24:
            setattr(hours_entry, 'working_hours', hours_data['working_hours'])

    # if comment is provided, update the comment
    if 'comment' in hours_data.keys():
        setattr(hours_entry, 'comment', hours_data['comment'])

    # save changes to database
    db.session.commit()
    return jsonify(hours_entry.to_dict())


@app.route('/api/working-hours/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_working_hours(id):
    """
    This method allows to delete an existing record of working hours from the user
    """
    # check if there is a record of this user, which can be deleted
    hours_entry = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, id=id).first()
    if hours_entry is None:
        return jsonify({'error': 'There is no entry for given id.'}), 404

    # delete the record from database
    db.session.delete(hours_entry)
    db.session.commit()
    return '', 204
