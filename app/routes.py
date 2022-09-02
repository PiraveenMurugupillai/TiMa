"""
All routes for the web application
"""
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
    """
    This method shows the login page and handles the login form input
    """
    # if the current user is already logged in, redirect to the page with records of working hours
    if current_user.is_authenticated:
        return redirect(url_for('working_hours_page'))

    form = LoginForm()
    # if the sent form is valid, it is checked for correct credentials before logging in
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login_page'))

        login_user(user, remember=form.remember_me.data)

        # redirect the user to the previous page (before login) or if not provided to page with records of working hours
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('working_hours_page')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """
    This method logs the current user out
    """
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """
    This page shows a registration page for new users
    """
    # if the current user is already logged in, redirect to the page with records of working hours
    if current_user.is_authenticated:
        return redirect(url_for('working_hours_page'))

    form = RegistrationForm()
    # if the submitted form is valid, the new user is created, stored to database and the user is automatically logged in and forwarded to his profile page
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
    """
    This page shows records of working hours of current or selected specific month
    It includes a form to create new records as well
    """
    # get current month & year as default values
    current_date = datetime.date.today()
    given_month = current_date.month
    given_year = current_date.year

    # checks for valid query parameter 'month' (must be between 1 & 12)
    requested_month = request.args.get('month')
    if requested_month is not None:
        try:
            given_month = min(max(int(requested_month), 1), 12)
        except:
            pass

    # checks for valid query parameter 'year' (must be between 2022 & 3000)
    requested_year = request.args.get('year')
    if requested_year is not None:
        try:
            given_year = min(max(int(requested_year), 2022), 3000)
        except:
            pass

    # calculates the oldest and most recent record entry
    all_hours = WorkingHours.query.filter_by(user_id=current_user.id).all()
    all_dates = list(map(lambda x: x.date, all_hours))
    minimal_date = min(all_dates, default=current_date)
    maximal_date = max(all_dates, default=current_date)

    # creates a list of all available years (for year selection on the web page)
    years = []
    for year in range(minimal_date.year, maximal_date.year + 1):
        years.append(year)

    # creates a list of all available months (for month selection on the web page)
    months = []
    for month in range(1, 13):
        months.append(datetime.date(2022, month, 1).strftime('%B'))

    # collects all records of the user in the given month of given year sorted by date
    hours = db.session.query(WorkingHours) \
        .filter(WorkingHours.user_id == current_user.id) \
        .filter(WorkingHours.date >= datetime.date(given_year, given_month, 1)) \
        .filter(WorkingHours.date < (datetime.date(given_year, given_month, 1) + relativedelta(months=+1))) \
        .order_by(asc(WorkingHours.date)) \
        .all()

    form = WorkingHoursForm()
    # if submitted form is valid, a new record is created with provided data
    if form.validate_on_submit():
        hours = WorkingHours(date=form.date.data, working_hours=form.hours.data, comment=form.comment.data, user_id=current_user.id)
        db.session.add(hours)
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    return render_template('working_hours/working-hours.html', form=form, hours=hours, months=months, years=years, given_month=given_month, given_year=given_year)


@app.route('/edit-working-hours/<working_hours_id>', methods=['GET', 'POST'])
@login_required
def edit_working_hours_page(working_hours_id):
    """
    This page allows a user to edit already existing records of working hours.
    """
    # get current month & year as default values
    current_date = datetime.date.today()
    given_month = current_date.month
    given_year = current_date.year

    # checks for valid query parameter 'month' (must be between 1 & 12)
    requested_month = request.args.get('month')
    if requested_month is not None:
        try:
            given_month = min(max(int(requested_month), 1), 12)
        except:
            pass

    # checks for valid query parameter 'year' (must be between 2022 & 3000)
    requested_year = request.args.get('year')
    if requested_year is not None:
        try:
            given_year = min(max(int(requested_year), 2022), 3000)
        except:
            pass

    # collects all records of the user in the given month of given year sorted by date
    hours = db.session.query(WorkingHours) \
        .filter(WorkingHours.user_id == current_user.id) \
        .filter(WorkingHours.date >= datetime.date(given_year, given_month, 1)) \
        .filter(WorkingHours.date < (datetime.date(given_year, given_month, 1) + relativedelta(months=+1))) \
        .order_by(asc(WorkingHours.date)) \
        .all()
    # load the entry to be edited
    edit_working_hour = WorkingHours.query.filter_by(id=working_hours_id, user_id=current_user.id).first_or_404()

    # if there is no entry, which wants to be edited, the user is redirected to the overview page of records
    if edit_working_hour is None:
        return redirect(url_for('working_hours_page'))

    form = EditWorkingHoursForm()
    # if submitted form is valid, the data is updated
    if form.validate_on_submit():
        edit_working_hour.working_hours = form.hours.data
        edit_working_hour.comment = form.comment.data
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    # if the edit page is loaded, the already existing data is prefilled
    elif request.method == 'GET':
        form.hours.data = edit_working_hour.working_hours
        if edit_working_hour.comment is not None:
            form.comment.data = edit_working_hour.comment

    # create a list of months to put the correct title
    months = []
    for month in range(1, 13):
        months.append(datetime.date(2022, month, 1).strftime('%B'))

    return render_template('working_hours/edit-working-hours.html', form=form, hours=hours, edit_working_hour=edit_working_hour, months=months, given_month=given_month, given_year=given_year)


@app.route('/delete-working-hours/<working_hours_id>', methods=['GET', 'POST'])
@login_required
def delete_working_hours_page(working_hours_id):
    """
    This page gives the user an overview of one specific record and allows the user to delete it
    """
    form = EmptySubmitForm()
    form.submit.label = Label(form.submit.id, 'Delete')

    # searched entry is loaded from database
    working_hour = WorkingHours.query.filter_by(id=working_hours_id, user_id=current_user.id).first()

    # if there is no entry with given id for the user, the user is redirected to the overview page with records of working hours
    if working_hour is None:
        return redirect(url_for('working_hours_page'))

    # if the user pressed on delete, the record is deleted and the user is redirected to the overview page
    if form.validate_on_submit():
        db.session.delete(working_hour)
        db.session.commit()
        return redirect(url_for('working_hours_page'))

    return render_template('working_hours/delete-working-hours.html', form=form, working_hour=working_hour)


@app.route('/user')
@login_required
def user_page():
    """
    This page shows an overview of the users profile
    """
    # the current logged in user is loaded from the database
    user = User.query.filter_by(username=current_user.username).first_or_404()
    # total worked days and hours are loaded from the database
    total_hours = db.session.query(func.count(WorkingHours.date), func.sum(WorkingHours.working_hours)).filter_by(user_id=current_user.id).all()[0]
    (worked_days, worked_hours) = total_hours
    # this fallback will take care of new users without any records of worked hours
    worked_hours = round(worked_hours or 0, 2)
    # calculation of flextime (if the user has worked more or less than the target_time)
    flextime = round(worked_hours - (worked_days * user.target_time), 2)
    return render_template('profile/user.html', user=user, flextime=flextime, worked_hours=worked_hours)


@app.route('/edit-user', methods=['GET', 'POST'])
@login_required
def edit_user_page():
    """
    On this page, the user can edit his profile
    """
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = EditUserForm()

    # if a valid form is submitted, the changes are saved to the database
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

    # all input fields of the editing page are prefilled with the existing values
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.company.data = user.company
        form.job.data = user.job
        form.target_time.data = user.target_time

    return render_template('profile/edit-user.html', user=user, form=form)
