"""
migrate_data.py
───────────────
Run this ONCE locally (before deploying) to import your CSV data into MySQL.
Uses only the built-in csv module — no pandas needed.

Usage:
    python migrate_data.py
"""

import csv
from datetime import datetime
from app import create_app
from extensions import db
from models import Train, Booking, User


def migrate_trains(path="Trains Data.csv"):
    count = 0
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if Train.query.filter_by(train_number=int(row['Train Number'])).first():
                continue
            train = Train(
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
            )
            db.session.add(train)
            count += 1
    db.session.commit()
    print(f"✅ Migrated {count} trains.")


def migrate_passengers(path="Passenger Data.csv"):
    count = 0
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if Booking.query.filter_by(booking_id=row['Booking ID']).first():
                continue
            try:
                journey_date = datetime.strptime(row['Journey Date'], '%m/%d/%Y').date()
                booking_date = datetime.strptime(row['Booking Date'], '%m/%d/%Y')
            except Exception:
                journey_date = datetime.today().date()
                booking_date = datetime.today()

            seat = row.get('Seat/Berth Number', '').strip()
            booking = Booking(
                booking_id          = row['Booking ID'],
                passenger_id        = row['Passenger ID'],
                train_number_fk     = int(row['Train Number']),
                journey_date        = journey_date,
                source_station      = row['Source Station'],
                destination_station = row['Destination Station'],
                travel_class        = row['Class'],
                seat_berth_number   = int(seat) if seat.isdigit() else None,
                fare_amount         = float(row['Fare Amount']),
                booking_status      = row['Booking Status'],
                booking_date        = booking_date,
                payment_method      = row['Payment Method'],
                passenger_name      = row['Passenger Name'],
            )
            db.session.add(booking)
            count += 1
    db.session.commit()
    print(f"✅ Migrated {count} passenger bookings.")


def create_default_admin():
    if not User.query.filter_by(email='admin@railconnect.com').first():
        admin = User(name='Admin', email='admin@railconnect.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created: admin@railconnect.com / admin123")
    else:
        print("ℹ️  Admin already exists.")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("Creating tables…")
        db.create_all()
        print("Migrating trains…")
        migrate_trains()
        print("Migrating passengers…")
        migrate_passengers()
        print("Creating admin user…")
        create_default_admin()
        print("\n🚂 Migration complete! Run: python app.py")
