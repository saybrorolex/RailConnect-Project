from flask import Blueprint, render_template
from flask_login import login_required
from models import Train, Booking, User
from extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # ── KPI Stats ──────────────────────────────────────────
    total_trains     = Train.query.count()
    total_bookings   = Booking.query.count()
    total_passengers = User.query.filter_by(role='passenger').count()
    total_revenue    = db.session.query(func.sum(Booking.fare_amount))\
                         .filter(Booking.booking_status == 'Confirmed').scalar() or 0

    # ── Booking Status Breakdown (for doughnut chart) ──────
    status_data = db.session.query(
        Booking.booking_status, func.count(Booking.id)
    ).group_by(Booking.booking_status).all()
    status_labels = [s[0] for s in status_data]
    status_counts = [s[1] for s in status_data]

    # ── Revenue by Class (for bar chart) ───────────────────
    class_revenue = db.session.query(
        Booking.travel_class, func.sum(Booking.fare_amount)
    ).filter(Booking.booking_status == 'Confirmed')\
     .group_by(Booking.travel_class).all()
    class_labels  = [r[0] for r in class_revenue]
    class_amounts = [float(r[1]) for r in class_revenue]

    # ── Train Type Distribution (for line chart) ───────────
    type_data = db.session.query(
        Train.train_type, func.count(Train.id)
    ).group_by(Train.train_type).all()
    type_labels = [t[0] for t in type_data]
    type_counts = [t[1] for t in type_data]

    # ── Recent Bookings ────────────────────────────────────
    recent_bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).limit(6).all()

    # ── Active Trains ──────────────────────────────────────
    active_trains = Train.query.filter_by(status='Active').limit(5).all()

    return render_template('dashboard/index.html',
        total_trains=total_trains,
        total_bookings=total_bookings,
        total_passengers=total_passengers,
        total_revenue=total_revenue,
        status_labels=status_labels,
        status_counts=status_counts,
        class_labels=class_labels,
        class_amounts=class_amounts,
        type_labels=type_labels,
        type_counts=type_counts,
        recent_bookings=recent_bookings,
        active_trains=active_trains,
    )
