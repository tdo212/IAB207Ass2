from flask import Blueprint, render_template, redirect, request, url_for
from .forms import CreateForm
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        # Create seminar class object here including image = db_file_path
        # seminar = Seminar()

        # Add object to database
        # db.session.add(seminar)

        # Commit to database
        # db.session.commit()
        print('Successfully created new seminar', 'success')
        return redirect(url_for('main.create'))
    return render_template('create.html', form = form)

def check_upload_file(form):
    # Form file data
    fp = form.image.data
    filename = fp.filename
    # Gets relative current path of the module file 
    BASE_PATH = os.path.dirname(__file__)
    # Upload path = static/img
    upload_path = os.path.join(BASE_PATH, 'static/img', secure_filename(filename))
    # Store relative upload path into DB as image location
    db_upload_path = 'static/img' + secure_filename(filename)
    # Save file and return db path
    fp.save(upload_path)

    return db_upload_path

@main_bp.route('/bookings')
def booking():
    return render_template('bookings.html')