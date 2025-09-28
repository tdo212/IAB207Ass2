from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/create')
def create():
    return render_template('create.html')

@main_bp.route('/bookings')
def booking():
    return render_template('bookings.html')