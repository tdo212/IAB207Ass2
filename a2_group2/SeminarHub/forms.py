from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, BooleanField, TelField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[InputRequired(message='Enter your email address.'), Email(message='Enter a valid email address.')], render_kw={'class': 'auth-form-control'})
    password = PasswordField('Password', validators=[InputRequired(message='Please enter your password.')], render_kw={'class': 'auth-form-control'})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})

class RegisterForm(FlaskForm):
    first_name = StringField('First name', validators=[InputRequired(message='Please enter a first name.')], render_kw={'class': 'auth-form-control'})
    last_name = StringField('Last name', validators=[InputRequired(message='Please enter a last name.')], render_kw={'class': 'auth-form-control'})
    email = StringField('Email address', validators=[InputRequired(message='Please enter an email address.'), Email(message='Enter a valid email address.')], render_kw={'class': 'auth-form-control'})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, message='Must be 6 characters long or more.'), DataRequired()], render_kw={'class': 'auth-form-control'})
    confirm_password = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords must match.')], render_kw={'class': 'auth-form-control'})
    number = TelField('Phone number', validators=[InputRequired(message='Please enter your number.')], render_kw={'class': 'auth-form-control'})
    address = StringField('Street address', validators=[InputRequired(message='Please enter your street address.')], render_kw={'class': 'auth-form-control'})
    accept_toc = BooleanField('I accept all Terms and Conditions', validators=[InputRequired(message="You must accept the terms and conditions to continue.")])
    submit = SubmitField('Create Account', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})