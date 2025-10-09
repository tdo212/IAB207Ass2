from flask import Blueprint, flash, render_template, url_for, redirect
from .. import db
from ..models import Booking
from flask_login import login_required, current_user

booking_bp = Blueprint('booking', __name__, template_folder='templates')

@booking_bp.route('/bookings')
@login_required
def booking():
    """User’s bookings, split by status."""
    confirmed_bookings = Booking.query.filter(
        Booking.status == "Confirmed",
        Booking.user_id == current_user.id
    ).all()

    completed_bookings = Booking.query.filter(
        Booking.status == "Completed",
        Booking.user_id == current_user.id
    ).all()

    cancelled_bookings = Booking.query.filter(
        Booking.status == "Cancelled",
        Booking.user_id == current_user.id
    ).all()

    return render_template(
        'bookings.html',
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        heading='My Bookings | '
    )

@booking_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking (only if you own it and it’s Confirmed)."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('booking.booking'))

    if booking.status != 'Confirmed':
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('booking.booking'))

    booking.status = 'Cancelled'
    db.session.commit()
    flash(f'Booking {booking.booking_number} has been cancelled.', 'success')
    return redirect(url_for('booking.booking'))