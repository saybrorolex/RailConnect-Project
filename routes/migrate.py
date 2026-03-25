import csv, os
from datetime import datetime
from flask import Blueprint, request, abort
from extensions import db
from models import Train, Booking

migrate_bp = Blueprint('migrate', __name__, url_prefix='/migrate')

# Simple secret key to prevent anyone else from triggering this
MIGRATE_SECRET = os.environ.get('MIGRATE_SECRET', 'mysecret123')


@migrate_bp.route('/<secret>')
def run(secret):
    if not MIGRATE_SECRET or secret != MIGRATE_SECRET:
        abort(403)

    results = []

    # ── Trains ──────────────────────────────────────────
    trains_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Trains_Data.csv')
    train_count = 0
    try:
        with open(trains_path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                if Train.query.filter_by(train_number=int(row['Train Number'])).first():
                    continue
                db.session.add(Train(
                    state_ut        = row['State/Union Territory'],
                    train_number    = int(row['Train Number']),
                    train_name      = row['Train Name'],
                    route           = row['Route'],
                    departure_time  = row['Departure Time'],
                    arrival_time    = row['Arrival Time'],
                    train_type      = row['Train Type'],
                    status          = row.get('Status', 'Active'),
                    capacity        = int(row['Capacity']),
                    platform_number = int(row['Platform Number']),
                    distance_km     = float(row['Distance (km)']),
                ))
                train_count += 1
        db.session.commit()
        results.append(f'✅ Imported {train_count} trains.')
    except Exception as e:
        db.session.rollback()
        results.append(f'❌ Trains error: {e}')

    # ── Passengers ──────────────────────────────────────
    pass_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Passenger_Data.csv')
    pass_count = 0
    try:
        with open(pass_path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                if Booking.query.filter_by(booking_id=row['Booking ID']).first():
                    continue
                try:
                    jd = datetime.strptime(row['Journey Date'], '%m/%d/%Y').date()
                    bd = datetime.strptime(row['Booking Date'], '%m/%d/%Y')
                except Exception:
                    jd = datetime.today().date()
                    bd = datetime.today()
                seat = row.get('Seat/Berth Number', '').strip()
                db.session.add(Booking(
                    booking_id          = row['Booking ID'],
                    passenger_id        = row['Passenger ID'],
                    train_number_fk     = int(row['Train Number']),
                    journey_date        = jd,
                    source_station      = row['Source Station'],
                    destination_station = row['Destination Station'],
                    travel_class        = row['Class'],
                    seat_berth_number   = int(seat) if seat.isdigit() else None,
                    fare_amount         = float(row['Fare Amount']),
                    booking_status      = row['Booking Status'],
                    booking_date        = bd,
                    payment_method      = row['Payment Method'],
                    passenger_name      = row['Passenger Name'],
                ))
                pass_count += 1
        db.session.commit()
        results.append(f'✅ Imported {pass_count} passengers.')
    except Exception as e:
        db.session.rollback()
        results.append(f'❌ Passengers error: {e}')

    return '<br>'.join(results) + '<br><br>Done! You can delete this route now.'
