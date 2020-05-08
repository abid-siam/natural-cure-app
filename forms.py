from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField,\
                    SelectMultipleField, SelectField, RadioField 
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, Email
from wtforms.fields.html5 import EmailField, IntegerField, DateField
from connection import *


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    sex = SelectField('Sex', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    addr_street = StringField('Address--Street', validators=[DataRequired(), Length(min=1, max=50)])
    addr_city = StringField('Address--City', validators=[DataRequired(), Length(min=1, max=25)])
    addr_state = StringField('Address--State', validators=[DataRequired(), Length(min=2, max=2)])
    addr_zip = StringField('Address--Zip Code', validators=[DataRequired(), Length(min=5, max=5)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        cursor = conn.cursor()
        query = 'SELECT * FROM user WHERE username = %s'
        cursor.execute(query, (username.data))
        data = cursor.fetchone()
        cursor.close()
        if (data):
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    addr_street = StringField('Address--Street', validators=[DataRequired(), Length(min=1, max=50)])
    addr_city = StringField('Address--City', validators=[DataRequired(), Length(min=1, max=25)])
    addr_state = StringField('Address--State', validators=[DataRequired(), Length(min=2, max=2)])
    addr_zip = StringField('Address--Zip Code', validators=[DataRequired(), Length(min=5, max=5)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != session['username']:
            cursor = conn.cursor()
            query = 'SELECT * FROM user WHERE username = %s'
            cursor.execute(query, (username.data))
            data = cursor.fetchone()
            if (data):
                raise ValidationError('That username is taken. Please choose a different one.')


class UploadDocumentForm(FlaskForm):
    document = FileField('Select a document', validators=[FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc']), DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=1024)])
    submit = SubmitField('Upload')

class ShareRecordsForm(FlaskForm):
    recipient = EmailField('Receiver Email Address', validators=[DataRequired(), Email()])
    user_email = EmailField('Sender Email Address', validators=[DataRequired(), Email()])
    user_password = PasswordField('Sender Email Password', validators=[DataRequired()])
    subject = StringField('Subject', validators=[Length(max=78)])
    body = TextAreaField('Message', validators=[Length(max=1024)])
    select = SelectField('Choose a file', validators=[DataRequired()])
    submit = SubmitField('Send')