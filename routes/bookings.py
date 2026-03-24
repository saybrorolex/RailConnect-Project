from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Booking, Train, User
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')

FARE_BASE   = {"Sleeper": 1.0, "General": 0.8, "AC 3-Tier": 2.0, "AC 2-Tier": 3.0}
FARE_CHARGE = {"Passenger": 0.0, "Mail": 0.05, "Express": 0.10,
               "Superfast": 0.20, "Rajdhani": 0.30, "Shatabdi": 0.35}

def calculate_fare(train_class, train_type, distance):
    base  = distance * FARE_BASE[train_class]
    fare  = base * (1 + FARE_CHARGE[train_type])
    return round(fare, 2)


@bookings_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    else:
        bookings = Booking.query.filter_by(
            passenger_id=current_user.passenger_id
        ).order_by(Booking.booking_date.desc()).all()

    return render_template('bookings/index.html', bookings=bookings)


@bookings_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    trains = Train.query.filter_by(status='Active').order_by(Train.train_name).all()

    if request.method == 'POST':
        try:
            train_number    = int(request.form['train_number'])
            travel_class    = request.form['travel_class']
            journey_date    = datetime.strptime(request.form['journey_date'], '%Y-%m-%d').date()
            payment_method  = request.form['payment_method']
            passenger_name  = request.form.get('passenger_name', current_user.name).strip()

            train = Train.query.filter_by(train_number=train_number).first()
            if not train:
                flash('Invalid train selected.', 'danger')
                return redirect(url_for('bookings.book'))

            if train.available_seats <= 0:
                flash('No seats available on this train. Booking as Waitlisted.', 'warning')
                status = 'Waitlisted'
            else:
                status = 'Confirmed'

            fare = calculate_fare(travel_class, train.train_type, train.distance_km)

            booking = Booking(
                passenger_id        = current_user.passenger_id or 'GUEST',
                passenger_id_fk     = current_user.id,
                train_number_fk     = train.train_number,
                journey_date        = journey_date,
                source_station      = train.source_station,
                destination_station = train.destination_station,
                travel_class        = travel_class,
                fare_amount         = fare,
                booking_status      = status,
                payment_method      = payment_method,
                passenger_name      = passenger_name,
            )
            booking.generate_booking_id()
            if status == 'Confirmed':
                booking.assign_seat()

            db.session.add(booking)
            db.session.commit()
            flash(f'Booking confirmed! Your Booking ID is {booking.booking_id}. Fare: ₹{fare}', 'success')
            return redirect(url_for('bookings.detail', booking_id=booking.booking_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Booking failed: {str(e)}', 'danger')

    return render_template('bookings/book.html', trains=trains)


@bookings_bp.route('/<booking_id>')
@login_required
def detail(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id).first_or_404()
    # Passengers can only see their own bookings
    if current_user.role != 'admin' and booking.passenger_id != current_user.passenger_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('bookings.index'))
    train = Train.query.filter_by(train_number=booking.train_number_fk).first()
    return render_template('bookings/detail.html', booking=booking, train=train)


@bookings_bp.route('/cancel/<booking_id>', methods=['POST'])
@login_required
def cancel(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id).first_or_404()
    if current_user.role != 'admin' and booking.passenger_id != current_user.passenger_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('bookings.index'))
    if booking.booking_status == 'Cancelled':
        flash('Ticket is already cancelled.', 'warning')
    else:
        booking.booking_status = 'Cancelled'
        db.session.commit()
        flash(f'Ticket {booking_id} cancelled successfully.', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/upgrade/<booking_id>', methods=['GET', 'POST'])
@login_required
def upgrade(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id).first_or_404()
    if current_user.role != 'admin' and booking.passenger_id != current_user.passenger_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('bookings.index'))

    train = Train.query.filter_by(train_number=booking.train_number_fk).first()

    if request.method == 'POST':
        new_class = request.form['travel_class']
        if new_class == booking.travel_class:
            flash('Please select a different class to upgrade.', 'warning')
        else:
            new_fare = calculate_fare(new_class, train.train_type, train.distance_km)
            booking.travel_class = new_class
            booking.fare_amount  = new_fare
            db.session.commit()
            flash(f'Ticket upgraded to {new_class}. New fare: ₹{new_fare}', 'success')
            return redirect(url_for('bookings.detail', booking_id=booking_id))

    classes = ['Sleeper', 'General', 'AC 3-Tier', 'AC 2-Tier']
    fare_preview = {c: calculate_fare(c, train.train_type, train.distance_km) for c in classes}
    return render_template('bookings/upgrade.html', booking=booking,
                           train=train, classes=classes, fare_preview=fare_preview)


@bookings_bp.route('/api/fare')
@login_required
def api_fare():
    """AJAX endpoint: returns fare for given class/type/distance"""
    train_class  = request.args.get('class', '')
    train_number = request.args.get('train', '')
    if not train_class or not train_number:
        return jsonify({'error': 'Missing params'}), 400
    train = Train.query.filter_by(train_number=train_number).first()
    if not train:
        return jsonify({'error': 'Train not found'}), 404
    fare = calculate_fare(train_class, train.train_type, train.distance_km)
    return jsonify({'fare': fare})
