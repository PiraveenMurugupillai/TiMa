from app import app, db
from app.froms import LoginForm, RegistrationForm, WorkingHoursForm, EditUserForm, EditWorkingHoursForm
from app.models import User, WorkingHours
from flask import redirect, request, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import asc
from werkzeug.urls import url_parse
from socket import gethostname


@app.route('/')
@login_required
def home_page():
    posts = [
        {
            'author': {'username': 'Pira'},
            'body': 'Schöner Abend hier in Aarburg'
        },
        {
            'author': {'username': 'Rethu'},
            'body': 'Meine Ferien ohne Pira sind einfach perfekt!'
        }
    ]
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login_page'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home_page')
        return redirect(next_page)
    return render_template('login.html', form=form, hostname=gethostname())


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, company=form.company.data, job=form.job.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('home_page'))

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/working-hours', methods=['GET', 'POST'])
@login_required
def working_hours_page():
    form = WorkingHoursForm()
    hours = WorkingHours.query.filter_by(user_id=current_user.id).order_by(asc(WorkingHours.date))

    if form.validate_on_submit():
        hours = WorkingHours(date=form.date.data, working_hours=form.hours.data, user_id=current_user.id)
        db.session.add(hours)
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    return render_template('working_hours/working-hours.html', form=form, hours=hours, number_of_entries=hours.count())


@app.route('/edit-working-hours/<working_hours_id>', methods=['GET', 'POST'])
@login_required
def edit_working_hours_page(working_hours_id):
    form = EditWorkingHoursForm()
    hours = WorkingHours.query.filter_by(user_id=current_user.id).order_by(asc(WorkingHours.date))
    edit_working_hour = WorkingHours.query.filter_by(id=working_hours_id).first_or_404()

    if edit_working_hour is None:
        return redirect(url_for('working_hours_page'))

    if form.validate_on_submit():
        edit_working_hour.working_hours = form.hours.data
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    elif request.method == 'GET':
        form.hours.data = edit_working_hour.working_hours

    return render_template('working_hours/edit-working-hours.html', form=form, hours=hours, edit_working_hour=edit_working_hour, number_of_entries=hours.count())




@app.route('/user')
@login_required
def user_page():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    return render_template('profile/user.html', user=user)


@app.route('/edit-user', methods=['GET', 'POST'])
@login_required
def edit_user_page():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = EditUserForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.company = form.company.data
        user.job = form.job.data
        db.session.commit()
        logout_user()
        login_user(user)
        return redirect(url_for('user_page'))

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.company.data = user.company
        form.job.data = user.job

    return render_template('profile/edit-user.html', user=user, form=form)