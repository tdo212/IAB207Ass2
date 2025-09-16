from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

# this is a hint for a login function
@auth_bp.route('/login', methods=['GET', 'POST'])
# view function
def login():
    """Attempts to log the user in when the LoginForm is submitted. This function will automatically search for an entry in the application database that matches the credentials provided.

    If successful, will redirect to the index page and flash a success message.

    If unsuccessful, with reload the Login page and flash an error message.
    """

    login_form = LoginForm()
    error = None

    # Check for user already logged in
    if current_user.is_authenticated:
        # Development information
        print('Already logged in as {}'.format(current_user))
        return redirect(url_for('main.index'))

    if login_form.validate_on_submit():
        # Development information
        print('Login requested for user {}, remember me = {}'. format(login_form.email.data, login_form.remember_me.data))

        # Get input credentials
        email = login_form.email.data
        password = login_form.password.data

        # Attempt to find match in database
        user = db.session.scalar(db.select(User).where(User.email == email))
        
        # If no user email
        if user is None:
            error = 'Incorrect email'
        # If correct email but incorrect password
        elif not check_password_hash(user.password_hash, password): # takes the hash and cleartext password
            error = 'Incorrect password'
        # If all credentials correct
        if error is None:
            login_user(user)
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp)
            if next is None or not nextp.startswith('/'):
                flash('Successfully logged in.')
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error)

    return render_template('login.html', form = login_form, heading = 'Login', logo_message = 'Log in to')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logs the user out of their account."""
    
    # Development information
    print('Logout requested for user {}'. format(current_user))

    logout_user()

    return redirect(url_for('main.index'))

@auth_bp.route('/signup', methods = ['GET', 'POST'])
def signup():
    """Attempts to register the user when the RegisterForm is submitted. 

    If the form is valid will take the user to the index page and flash a success message.
    
    If the form is not valid will automatically redirect the user to the Signup page."""
    signup_form = RegisterForm()

    # Check for validity of form on submit
    if signup_form.validate_on_submit():
        # Development information
        print('Sign up request for user {}, password match {}'.format(signup_form.email.data, not signup_form.confirm_password.errors))

        # Hash password and format full name for entry into database
        hashed_password = generate_password_hash(signup_form.password.data)
        full_name = f"{signup_form.first_name.data} {signup_form.last_name.data}"

        # TODO: Needs database to be created and integrated into app to work.
        # Create User object and store in database
        user = User(name = full_name, email = signup_form.email.data, password_hash = hashed_password, number = signup_form.number.data, address = signup_form.address.data)

        # Add to database
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created.')

        return redirect(url_for('main.index'))
    return render_template('signup.html', heading = 'Sign Up', logo_message = 'Become a member of', form = signup_form)