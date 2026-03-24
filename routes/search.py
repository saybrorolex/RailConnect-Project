from flask import Blueprint, render_template, request
from flask_login import login_required
from models import Train, Booking
from extensions import db
from sqlalchemy import func

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
@login_required
def index():
    return render_template('search/index.html')


@search_bp.route('/trains')
@login_required
def search_trains():
    q       = request.args.get('q', '').strip()
    by      = request.args.get('by', 'name')
    results = []

    if q:
        if by == 'name':
            results = Train.query.filter(Train.train_name.ilike(f'%{q}%')).all()
        elif by == 'type':
            results = Train.query.filter(Train.train_type.ilike(f'%{q}%')).all()
        elif by == 'station':
            results = Train.query.filter(Train.route.ilike(f'%{q}%')).all()
        elif by == 'platform':
            results = Train.query.filter_by(platform_number=int(q) if q.isdigit() else -1).all()

    return render_template('search/trains.html', results=results, q=q, by=by)


@search_bp.route('/passengers')
@login_required
def search_passengers():
    q       = request.args.get('q', '').strip()
    by      = request.args.get('by', 'name')
    results = []

    if q:
        if by == 'name':
            results = Booking.query.filter(Booking.passenger_name.ilike(f'%{q}%')).all()
        elif by == 'booking_id':
            results = Booking.query.filter_by(booking_id=q.upper()).all()
        elif by == 'passenger_id':
            results = Booking.query.filter_by(passenger_id=q.upper()).all()
        elif by == 'status':
            results = Booking.query.filter_by(booking_status=q).all()
        elif by == 'source':
            results = Booking.query.filter(Booking.source_station.ilike(f'%{q}%')).all()
        elif by == 'destination':
            results = Booking.query.filter(Booking.destination_station.ilike(f'%{q}%')).all()

    return render_template('search/passengers.html', results=results, q=q, by=by)
