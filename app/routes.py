from app import app, db
from app.froms import LoginForm, RegistrationForm, WorkingHoursForm, EditUserForm, EditWorkingHoursForm, EmptySubmitForm
from app.models import User, WorkingHours
import datetime
from dateutil.relativedelta import relativedelta
from flask import redirect, request, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import asc, func
from werkzeug.urls import url_parse
from wtforms import Label


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login_page'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('working_hours_page')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, company=form.company.data, job=form.job.data, target_time=form.target_time.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('user_page'))

    return render_template('register.html', form=form)


@app.route('/')
@app.route('/working-hours', methods=['GET', 'POST'])
@login_required
def working_hours_page():
    current_date = datetime.date.today()
    given_month = current_date.month
    given_year = current_date.year

    requested_month = request.args.get('month')
    if requested_month is not None:
        try:
            given_month = min(max(int(requested_month), 1), 12)
        except:
            pass

    requested_year = request.args.get('year')
    if requested_year is not None:
        try:
            given_year = min(max(int(requested_year), 2022), 3000)
        except:
            pass

    hours = db.session.query(WorkingHours)\
        .filter(WorkingHours.user_id == current_user.id)\
        .filter(WorkingHours.date >= datetime.date(given_year, given_month, 1))\
        .filter(WorkingHours.date < (datetime.date(given_year, given_month, 1) + relativedelta(months=+1)))\
        .order_by(asc(WorkingHours.date))\
        .all()
    all_hours = WorkingHours.query.filter_by(user_id=current_user.id).all()
    all_dates = list(map(lambda x: x.date, all_hours))
    minimal_date = min(all_dates)
    maximal_date = max(all_dates)

    years = []
    for year in range(minimal_date.year, maximal_date.year + 1):
        years.append(year)

    months = []
    for month in range(1, 13):
        months.append(datetime.date(2022, month, 1).strftime('%B'))

    form = WorkingHoursForm()
    if form.validate_on_submit():
        hours = WorkingHours(date=form.date.data, working_hours=form.hours.data, comment=form.comment.data, user_id=current_user.id)
        db.session.add(hours)
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    return render_template('working_hours/working-hours.html', form=form, hours=hours, months=months, years=years, given_month=given_month, given_year=given_year)


@app.route('/edit-working-hours/<working_hours_id>', methods=['GET', 'POST'])
@login_required
def edit_working_hours_page(working_hours_id):
    current_date = datetime.date.today()
    given_month = current_date.month
    given_year = current_date.year

    requested_month = request.args.get('month')
    if requested_month is not None:
        try:
            given_month = min(max(int(requested_month), 1), 12)
        except:
            pass

    requested_year = request.args.get('year')
    if requested_year is not None:
        try:
            given_year = min(max(int(requested_year), 2022), 3000)
        except:
            pass

    hours = db.session.query(WorkingHours) \
        .filter(WorkingHours.user_id == current_user.id) \
        .filter(WorkingHours.date >= datetime.date(given_year, given_month, 1)) \
        .filter(WorkingHours.date < (datetime.date(given_year, given_month, 1) + relativedelta(months=+1))) \
        .order_by(asc(WorkingHours.date)) \
        .all()
    edit_working_hour = WorkingHours.query.filter_by(id=working_hours_id, user_id=current_user.id).first_or_404()

    if edit_working_hour is None:
        return redirect(url_for('working_hours_page'))

    form = EditWorkingHoursForm()
    if form.validate_on_submit():
        edit_working_hour.working_hours = form.hours.data
        edit_working_hour.comment = form.comment.data
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    elif request.method == 'GET':
        form.hours.data = edit_working_hour.working_hours
        if edit_working_hour.comment is not None:
            form.comment.data = edit_working_hour.comment

    months = []
    for month in range(1, 13):
        months.append(datetime.date(2022, month, 1).strftime('%B'))

    return render_template('working_hours/edit-working-hours.html', form=form, hours=hours, edit_working_hour=edit_working_hour, months=months, given_month=given_month, given_year=given_year)


@app.route('/delete-working-hours/<working_hours_id>', methods=['GET', 'POST'])
@login_required
def delete_working_hours_page(working_hours_id):
    form = EmptySubmitForm()
    form.submit.label = Label(form.submit.id, 'Delete')
    working_hour = WorkingHours.query.filter_by(id=working_hours_id, user_id=current_user.id).first()

    if working_hour is None:
        return redirect(url_for('working_hours_page'))

    if form.validate_on_submit():
        db.session.delete(working_hour)
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    return render_template('working_hours/delete-working-hours.html', form=form, working_hour=working_hour)


@app.route('/user')
@login_required
def user_page():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    total_hours = db.session.query(func.count(WorkingHours.date), func.sum(WorkingHours.working_hours)).filter_by(user_id=current_user.id).all()[0]
    (worked_days, worked_hours) = total_hours
    worked_hours = round(worked_hours or 0, 2)
    flextime = round(worked_hours - (worked_days * user.target_time), 2)
    return render_template('profile/user.html', user=user, flextime=flextime, worked_hours=worked_hours)


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
        user.target_time = form.target_time.data
        db.session.commit()
        logout_user()
        login_user(user)
        return redirect(url_for('user_page'))

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.company.data = user.company
        form.job.data = user.job
        form.target_time.data = user.target_time

    return render_template('profile/edit-user.html', user=user, form=form)
