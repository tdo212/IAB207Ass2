from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TelField, SelectField, DateField, TimeField, IntegerField, TextAreaField, SubmitField, SearchField, ValidationError
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange, Optional, DataRequired, Length
from flask_wtf.file import FileRequired, FileField, FileAllowed

# Custom validators for password and phone number checks
from .auth import auth_validators

# Allowed file types for uploaded images
ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'png', 'jpg', 'jpeg'}

# Centralise category choices so Create/Edit stay in sync
CATEGORY_CHOICES = [
    ('cs', 'Computer Science'),
    ('business', 'Business'),
    ('engineering', 'Engineering'),
    ('medicine', 'Medicine'),
    ('social', 'Social Sciences'),
    ('other', 'Other'),
]

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[InputRequired(message='Enter your email address.'), Email(message='Enter a valid email address.')], render_kw={'class': 'auth-form-control'})
    password = PasswordField('Password', validators=[InputRequired(message='Please enter your password.')], render_kw={'class': 'auth-form-control'})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})

class RegisterForm(FlaskForm):
    first_name = StringField('First name', validators=[InputRequired(message='Please enter a first name.')], render_kw={'class': 'auth-form-control'})
    last_name = StringField('Last name', validators=[InputRequired(message='Please enter a last name.')], render_kw={'class': 'auth-form-control'})
    email = StringField('Email address', validators=[InputRequired(message='Please enter an email address.'), Email(message='Enter a valid email address.'), auth_validators.email_validator()], render_kw={'class': 'auth-form-control'})
    password = PasswordField('Password', validators=[InputRequired(), auth_validators.password_validator()], render_kw={'class': 'auth-form-control'})
    confirm_password = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords must match.')], render_kw={'class': 'auth-form-control'})
    number = TelField('Phone number', validators=[InputRequired(message='Please enter your number.'), auth_validators.phone_number_validator()], render_kw={'class': 'auth-form-control'})
    address = StringField('Street address', validators=[InputRequired(message='Please enter your street address.')], render_kw={'class': 'auth-form-control'})
    accept_toc = BooleanField('I accept all Terms and Conditions', validators=[InputRequired(message="You must accept the terms and conditions to continue.")])
    submit = SubmitField('Create Account', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})


class CreateForm(FlaskForm):
    title = StringField('Seminar Title', validators=[InputRequired(message='Please enter a title.')])
    category = SelectField('Category', choices=CATEGORY_CHOICES, validators=[InputRequired()], coerce=str)
    description = TextAreaField('Description', validators=[InputRequired(message='Please enter a description of your seminar.')])
    date = DateField('Date', validators=[InputRequired(message='Please enter a valid date.')])
    start_time = TimeField('Start Time', validators=[InputRequired(message='Please enter a valid start time.')])
    end_time = TimeField('End Time', validators=[InputRequired(message='Please enter a valid end time.')])
    location = StringField('Location', validators=[InputRequired(message='Please enter a location for the seminar.')])
    capacity = IntegerField('Capacity', validators=[InputRequired(message='Please enter the maximum attendees.'), NumberRange(min=0)])
    speaker = StringField('Speaker Name', validators=[InputRequired(message="Please enter the speaker's name.")])
    speaker_bio = TextAreaField('Speaker Bio', validators=[Optional()])
    image = FileField('Seminar Image', validators=[FileRequired(message='Please select an image to upload.'), FileAllowed(ALLOWED_FILE, message='Uploaded image must be a PNG, JPG or JPEG.')])
    accept_toc = BooleanField('I confirm that I have the rights to organize this event and agree to the ', validators=[InputRequired(message="You must accept the terms and conditions to continue.")])
    submit = SubmitField('Create Seminar', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})

    # End time is after start time (on the same date)
    def validate_end_time(self, field):
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End Time must be after Start Time.')


class EditForm(CreateForm):
    # Make image optional when editing
    image = FileField('Seminar Image', validators=[Optional(), FileAllowed(ALLOWED_FILE, message='Uploaded image must be a PNG, JPG or JPEG.')])
    accept_toc = BooleanField('I confirm that I have the rights to organize this event and agree to the ', validators=[Optional()])
    submit = SubmitField('Save Seminar', render_kw={'class': 'mt-4 btn btn-primary login-button btn-lg'})


class SearchForm(FlaskForm):
    search = SearchField('Search', validators=[InputRequired()])
    submit = SubmitField('Search', render_kw={'class': 'btn btn-block'})


class CommentForm(FlaskForm):
    text = TextAreaField("Add your comment", validators=[DataRequired(message="Comment can't be empty."), Length(max=1000)])
    submit = SubmitField("Post Comment")
