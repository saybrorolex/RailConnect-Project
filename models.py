from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager
import random, string
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='passenger', nullable=False)
    passenger_id  = db.Column(db.String(20), unique=True, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', foreign_keys='Booking.passenger_id_fk',
                               backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_passenger_id(self):
        while True:
            pid = 'P' + ''.join(random.choices(string.digits, k=5))
            if not User.query.filter_by(passenger_id=pid).first():
                self.passenger_id = pid
                break

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Train(db.Model):
    __tablename__ = 'trains'

    id              = db.Column(db.Integer, primary_key=True)
    state_ut        = db.Column(db.String(100), nullable=False)
    train_number    = db.Column(db.Integer, unique=True, nullable=False)
    train_name      = db.Column(db.String(150), nullable=False)
    route           = db.Column(db.String(200), nullable=False)
    departure_time  = db.Column(db.String(10), nullable=False)
    arrival_time    = db.Column(db.String(10), nullable=False)
    train_type      = db.Column(db.String(20), nullable=False)
    status          = db.Column(db.String(20), default='Active')
    capacity        = db.Column(db.Integer, nullable=False)
    platform_number = db.Column(db.Integer, nullable=False)
    distance_km     = db.Column(db.Float, nullable=False)

    bookings = db.relationship('Booking', backref='train', lazy=True)

    @property
    def source_station(self):
        parts = self.route.split(' to ')
        return parts[0].strip() if parts else ''

    @property
    def destination_station(self):
        parts = self.route.split(' to ')
        return parts[1].strip() if len(parts) > 1 else ''

    @property
    def booked_seats(self):
        return Booking.query.filter_by(
            train_number_fk=self.train_number,
            booking_status='Confirmed'
        ).count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.booked_seats)

    def __repr__(self):
        return f'<Train {self.train_number} - {self.train_name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id                  = db.Column(db.Integer, primary_key=True)
    booking_id          = db.Column(db.String(10), unique=True, nullable=False)
    passenger_id        = db.Column(db.String(10), nullable=False)
    passenger_id_fk     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    train_number_fk     = db.Column(db.Integer, db.ForeignKey('trains.train_number'), nullable=False)
    journey_date        = db.Column(db.Date, nullable=False)
    source_station      = db.Column(db.String(100), nullable=False)
    destination_station = db.Column(db.String(100), nullable=False)
    travel_class        = db.Column(db.String(20), nullable=False)
    seat_berth_number   = db.Column(db.Integer, nullable=True)
    fare_amount         = db.Column(db.Float, nullable=False)
    booking_status      = db.Column(db.String(20), default='Confirmed')
    booking_date        = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method      = db.Column(db.String(30), nullable=False)
    passenger_name      = db.Column(db.String(100), nullable=False)

    def generate_booking_id(self):
        while True:
            bid = 'B' + ''.join(random.choices(string.digits, k=5))
            if not Booking.query.filter_by(booking_id=bid).first():
                self.booking_id = bid
                break

    def assign_seat(self):
        existing = Booking.query.filter_by(
            train_number_fk=self.train_number_fk,
            booking_status='Confirmed'
        ).count()
        self.seat_berth_number = existing + 1

    def __repr__(self):
        return f'<Booking {self.booking_id} - {self.passenger_name}>'
