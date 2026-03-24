from flask import Blueprint, render_template
from flask_login import login_required
from extensions import db
from models import Train, Booking
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    fares = [b.fare_amount for b in Booking.query.filter_by(booking_status='Confirmed').all()]

    class_data = db.session.query(
        Booking.travel_class, func.count(Booking.id)
    ).group_by(Booking.travel_class).all()

    source_data = db.session.query(
        Booking.source_station, func.count(Booking.id)
    ).group_by(Booking.source_station)\
     .order_by(func.count(Booking.id).desc()).limit(10).all()

    revenue_data = db.session.query(
        Booking.train_number_fk, func.sum(Booking.fare_amount)
    ).filter(Booking.booking_status == 'Confirmed')\
     .group_by(Booking.train_number_fk)\
     .order_by(func.sum(Booking.fare_amount).desc()).limit(10).all()

    payment_data = db.session.query(
        Booking.payment_method, func.count(Booking.id)
    ).group_by(Booking.payment_method).all()

    train_type_data = db.session.query(
        Train.train_type, func.count(Booking.id)
    ).join(Booking, Train.train_number == Booking.train_number_fk)\
     .group_by(Train.train_type).all()

    return render_template('analytics/index.html',
        fares          = fares,
        class_labels   = [r[0] for r in class_data],
        class_counts   = [r[1] for r in class_data],
        source_labels  = [r[0] for r in source_data],
        source_counts  = [r[1] for r in source_data],
        revenue_trains = [str(r[0]) for r in revenue_data],
        revenue_amounts= [float(r[1]) for r in revenue_data],
        payment_labels = [r[0] for r in payment_data],
        payment_counts = [r[1] for r in payment_data],
        tt_labels      = [r[0] for r in train_type_data],
        tt_counts      = [r[1] for r in train_type_data],
    )
