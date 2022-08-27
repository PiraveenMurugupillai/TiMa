import datetime
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms.widgets import NumberInput

from app.models import User, WorkingHours


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    company = StringField('Company', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class WorkingHoursForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], default=datetime.datetime.utcnow())
    hours = FloatField('Worked Hours', validators=[DataRequired()], widget=NumberInput(min=0, max=24))
    submit = SubmitField('Add')

    def validate_date(self, date):
        hour = WorkingHours.query.filter_by(user_id=current_user.id, date=date.data).first()
        if hour is not None:
            print('There is already an entry for this date.', flush=True)
            raise ValidationError('There is already an entry for this date.')


class EditWorkingHoursForm(FlaskForm):
    hours = FloatField('Worked Hours', validators=[DataRequired()], widget=NumberInput(min=0, max=24))
    submit = SubmitField('Save')


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')
