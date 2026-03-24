"""
migrate_data.py
───────────────
Run this ONCE after setting up the database to import
your existing CSV data into MySQL.

Usage:
    python migrate_data.py
"""

import pandas as pd
from app import create_app
from extensions import db
from models import Train, Booking, User
from datetime import datetime


def migrate_trains(path="Trains Data.csv"):
    df = pd.read_csv(path)
    count = 0
    for _, row in df.iterrows():
        # Skip if already exists
        if Train.query.filter_by(train_number=int(row['Train Number'])).first():
            continue
        train = Train(
            state_ut        = str(row['State/Union Territory']),
            train_number    = int(row['Train Number']),
            train_name      = str(row['Train Name']),
            route           = str(row['Route']),
            departure_time  = str(row['Departure Time']),
            arrival_time    = str(row['Arrival Time']),
            train_type      = str(row['Train Type']),
            status          = str(row.get('Status', 'Active')),
            capacity        = int(row['Capacity']),
            platform_number = int(row['Platform Number']),
            distance_km     = float(row['Distance (km)']),
        )
        db.session.add(train)
        count += 1
    db.session.commit()
    print(f"✅ Migrated {count} trains.")


def migrate_passengers(path="Passenger Data.csv"):
    df = pd.read_csv(path)
    count = 0
    for _, row in df.iterrows():
        if Booking.query.filter_by(booking_id=str(row['Booking ID'])).first():
            continue
        try:
            journey_date = datetime.strptime(str(row['Journey Date']), '%m/%d/%Y').date()
            booking_date = datetime.strptime(str(row['Booking Date']), '%m/%d/%Y')
        except Exception:
            journey_date = datetime.today().date()
            booking_date = datetime.today()

        booking = Booking(
            booking_id          = str(row['Booking ID']),
            passenger_id        = str(row['Passenger ID']),
            train_number_fk     = int(row['Train Number']),
            journey_date        = journey_date,
            source_station      = str(row['Source Station']),
            destination_station = str(row['Destination Station']),
            travel_class        = str(row['Class']),
            seat_berth_number   = int(row['Seat/Berth Number']) if pd.notna(row.get('Seat/Berth Number')) else None,
            fare_amount         = float(row['Fare Amount']),
            booking_status      = str(row['Booking Status']),
            booking_date        = booking_date,
            payment_method      = str(row['Payment Method']),
            passenger_name      = str(row['Passenger Name']),
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
