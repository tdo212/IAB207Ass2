from wtforms.validators import ValidationError
from .. import db
from ..models import User

def password_validator():
    """Checks the password entered by a user in a form to make sure that it contains an uppercase letter, a lower case letter, a special character and that it is at least 6 characters long.
    
    If this is not the case a ValidationError is thrown and a message displayed in the form.
    """

    character_message = "Password must have an upper case, lower case and special character to be valid."
    length_message = "Password must be at least 6 characters long to be valid."

    def _password_validator(form, field):
        special_characters = r"!@#$%^&*()_+[]{}|;:,.<>?/\`~=-"
        password = field.data
        # Validate length greater than 6
        if len(password) < 6:
            raise ValidationError(length_message)
        # Validate special character presence
        elif not any(char in special_characters for char in password):
            raise ValidationError(character_message)
        # Validate capital letter
        elif not any(char.isupper() for char in password):
            raise ValidationError(character_message)
        
    return _password_validator
    

def phone_number_validator():
    """Checks the phone number entered by a user in a form to make sure that it only contains digits or the beginnings of a country code with the character '+'.

    If the phone number is invalid it will throw a ValidationError and display a message in the form.

    For future iterations using the python module 'phonenumbers' would be more efficient and accurate.
    """

    message = "Please enter a valid phone number."

    def _phone_number_validator(form, field):
        number = field.data

        # Check if there is the start of a country code prefix in the number. 
        if number.startswith("+"):
            # If there is, turn into a list, pop the '+' and check the rest of the input to make sure it's all digits.
            number_list = list(number)
            number_list.pop(0)
            # Remake into a string
            new_number = "".join(number_list)
            
            if not new_number.isdigit():
                raise ValidationError(message)
        
        # If no '+' at start, check input for digits. If not digits, throw error.
        elif not number.isdigit():
            raise ValidationError(message)
        
    return _phone_number_validator


def email_validator():
    """Checks the email entered by the user in the sign up form to make sure that it is unique within the database.

    If the email address already exists it will throw a ValidationError and display a message in the form.
    """
    message = "An account with that email already exists."

    def _email_validator(form, field):
        email = field.data

        # Check for a user that already exists in the database with that email
        check_existing_user = db.session.scalar(db.select(User).where(User.email == email))
        if check_existing_user:
            raise ValidationError(message)
        
    return _email_validator