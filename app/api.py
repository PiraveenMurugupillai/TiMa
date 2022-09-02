from app import app, db
from app.models import User, WorkingHours
import datetime
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return jsonify({'error': 'Username or password is wrong.'}), 400


@basic_auth.error_handler
def basic_auth_error(status):
    return '', status


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else jsonify({'error': 'Invalid authorization token.'}), 401


@token_auth.error_handler
def token_auth_error(status):
    return jsonify({'error': 'Invalid authorization token.'}), status


@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})


@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204


@app.route('/api/users', methods=['GET'])
@token_auth.login_required
def get_user():
    data = User.query.get_or_404(token_auth.current_user().id).to_dict()
    return jsonify(data)


@app.route('/api/users', methods=['POST'])
def create_new_user():
    try:
        user_data = request.get_json()
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']
        company = user_data['company']
        job = user_data['job']
        target_time = user_data['target_time']

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(username=username).first()
        if (existing_username is not None) or (existing_email is not None):
            return jsonify({'error': 'Please use a different username or email'}), 400

        if float(target_time) < 0 or float(target_time) > 24:
            return jsonify({'error': 'Please enter target time in a valid range (0 to 24)'}), 400

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
    try:
        user_data = request.get_json()
    except:
        user_data = {}

    user = User.query.get(token_auth.current_user().id)
    for key in user_data.keys():
        if key in user.to_dict().keys():
            if key == 'username':
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user is not None and existing_user.id != token_auth.current_user().id:
                    return jsonify({'error': 'Given username is already taken. Choose another one.'}), 400

            if key == 'email':
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if existing_user is not None and existing_user.id != token_auth.current_user().id:
                    return jsonify({'error': 'Given e-mail address is already taken. Choose another one.'}), 400

            setattr(user, key, user_data[key])

    db.session.commit()
    return jsonify(user.to_dict())


@app.route('/api/working-hours', methods=['GET'])
@token_auth.login_required
def get_working_hours():
    data = WorkingHours.query.filter_by(user_id=token_auth.current_user().id).all()
    return jsonify(list(map(lambda x: x.to_dict(), data)))


@app.route('/api/working-hours/<int:id>', methods=['GET'])
@token_auth.login_required
def get_working_hours_by_id(id):
    data = WorkingHours.query.get_or_404(id).to_dict()

    if token_auth.current_user().id != data['user_id']:
        return jsonify({'error': 'You are only allowed to see your own working hours entries.'}), 403

    return jsonify(data)


@app.route('/api/working-hours', methods=['POST'])
@token_auth.login_required
def add_working_hours():
    try:
        hours = request.get_json()
        date = datetime.datetime.strptime(hours['date'], '%Y-%m-%d')
        working_hours = hours['working_hours']
        comment = ''
        if 'comment' in hours.keys():
            comment = hours['comment']

        existing_hours = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, date=date).first()
        if existing_hours is not None:
            return jsonify({'error': 'There is already an entry for given date.'}), 400

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
    try:
        hours_data = request.get_json()
    except:
        hours_data = {}

    hours_entry = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, id=id).first()
    if hours_entry is None:
        return jsonify({'error': 'There is no entry for given id.'}), 404

    if 'working_hours' in hours_data.keys():
        if 0 <= hours_data['working_hours'] <= 24:
            setattr(hours_entry, 'working_hours', hours_data['working_hours'])

    if 'comment' in hours_data.keys():
        setattr(hours_entry, 'comment', hours_data['comment'])

    db.session.commit()
    return jsonify(hours_entry.to_dict())


@app.route('/api/working-hours/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_working_hours(id):
    hours_entry = WorkingHours.query.filter_by(user_id=token_auth.current_user().id, id=id).first()
    if hours_entry is None:
        return jsonify({'error': 'There is no entry for given id.'}), 404

    db.session.delete(hours_entry)
    db.session.commit()
    return '', 204
