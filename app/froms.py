"""
Different FlaskForms are created to handle user input
"""

import datetime
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length, ValidationError
from wtforms.widgets import NumberInput
from app.models import User, WorkingHours


class LoginForm(FlaskForm):
    """
    This Form is used for the login page.
    It must have the fields username & password
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    This Form is used for user registration.
    It must have username, email, password (and matching repeated password), company, job & target_time fields.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    company = StringField('Company', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    target_time = FloatField('Target hours per day', validators=[DataRequired(), NumberRange(min=0, max=24)],
                             widget=NumberInput(min=0, max=24))
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        This method validates if a provided username is already taken
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """
        This method validates if a provided email address is already taken
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class WorkingHoursForm(FlaskForm):
    """
    This Form is used to register new records of working hours.
    It must have date & hours fields. Optionally it can contain a comment.
    """
    date = DateField('Date', validators=[DataRequired()], default=datetime.datetime.utcnow())
    hours = FloatField('Worked Hours', validators=[DataRequired(), NumberRange(min=0, max=24)],
                       widget=NumberInput(min=0, max=24))
    comment = StringField('Comment')
    submit = SubmitField('Add')

    def validate_date(self, date):
        """
        This method validates if there is no entry of this user on the given date already.
        """
        hour = WorkingHours.query.filter_by(user_id=current_user.id, date=date.data).first()
        if hour is not None:
            raise ValidationError('There is already an entry for this date.')


class EditWorkingHoursForm(FlaskForm):
    """
    This Form is used to edit existing records of working hours.
    It must have only the field hours. Optionally it can contain a comment.
    """
    hours = FloatField('Worked Hours', validators=[DataRequired(), NumberRange(min=0, max=24)],
                       widget=NumberInput(min=0, max=24))
    comment = StringField('Comment', validators=[Length(max=64)])
    submit = SubmitField('Save')


class EditUserForm(FlaskForm):
    """
    This Form is used to edit the current user.
    It must have username, email, company, job & target_time fields.
    """
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired()])
    job = StringField('Job', validators=[DataRequired()])
    target_time = FloatField('Target hours per day', validators=[DataRequired(), NumberRange(min=0, max=24)],
                             widget=NumberInput(min=0, max=24))
    submit = SubmitField('Save')

    def validate_username(self, username):
        """
        This method validates, if the desired new username is not already taken.
        It has only to validate, if it's not the same as the current username.
        """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """
        This method validates, if the desired new email address is not already taken.
        It has only to validate, if it's not the same as the current email address.
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')


class EmptySubmitForm(FlaskForm):
    """
    This empty Form is used with only a submit button.
    It is intended as a confirmation from the user for any actions.
    """
    submit = SubmitField()
