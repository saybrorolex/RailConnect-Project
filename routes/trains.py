from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Train
from functools import wraps

trains_bp = Blueprint('trains', __name__, url_prefix='/trains')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@trains_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    train_type = request.args.get('type', '')
    status = request.args.get('status', '')

    query = Train.query
    if search:
        query = query.filter(
            (Train.train_name.ilike(f'%{search}%')) |
            (Train.train_number == search if search.isdigit() else False)
        )
    if train_type:
        query = query.filter_by(train_type=train_type)
    if status:
        query = query.filter_by(status=status)

    trains = query.order_by(Train.train_number).all()
    train_types = ['Passenger','Mail','Express','Superfast','Rajdhani','Shatabdi']
    return render_template('trains/index.html', trains=trains,
                           train_types=train_types, search=search,
                           selected_type=train_type, selected_status=status)


@trains_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        try:
            train = Train(
                state_ut        = request.form['state_ut'],
                train_number    = int(request.form['train_number']),
                train_name      = request.form['train_name'],
                route           = request.form['route'],
                departure_time  = request.form['departure_time'],
                arrival_time    = request.form['arrival_time'],
                train_type      = request.form['train_type'],
                status          = request.form.get('status', 'Active'),
                capacity        = int(request.form['capacity']),
                platform_number = int(request.form['platform_number']),
                distance_km     = float(request.form['distance_km']),
            )
            db.session.add(train)
            db.session.commit()
            flash(f'Train {train.train_name} added successfully!', 'success')
            return redirect(url_for('trains.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding train: {str(e)}', 'danger')

    return render_template('trains/form.html', train=None, action='Add')


@trains_bp.route('/edit/<int:train_number>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(train_number):
    train = Train.query.filter_by(train_number=train_number).first_or_404()

    if request.method == 'POST':
        try:
            train.state_ut        = request.form['state_ut']
            train.train_name      = request.form['train_name']
            train.route           = request.form['route']
            train.departure_time  = request.form['departure_time']
            train.arrival_time    = request.form['arrival_time']
            train.train_type      = request.form['train_type']
            train.status          = request.form.get('status', 'Active')
            train.capacity        = int(request.form['capacity'])
            train.platform_number = int(request.form['platform_number'])
            train.distance_km     = float(request.form['distance_km'])
            db.session.commit()
            flash(f'Train {train.train_name} updated successfully!', 'success')
            return redirect(url_for('trains.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating train: {str(e)}', 'danger')

    return render_template('trains/form.html', train=train, action='Edit')


@trains_bp.route('/delete/<int:train_number>', methods=['POST'])
@login_required
@admin_required
def delete(train_number):
    train = Train.query.filter_by(train_number=train_number).first_or_404()
    try:
        db.session.delete(train)
        db.session.commit()
        flash(f'Train {train.train_name} deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Cannot delete: {str(e)}', 'danger')
    return redirect(url_for('trains.index'))


@trains_bp.route('/api/<int:train_number>')
@login_required
def api_train(train_number):
    """Returns train info as JSON — used by booking form."""
    train = Train.query.filter_by(train_number=train_number).first()
    if not train:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'train_number':   train.train_number,
        'train_name':     train.train_name,
        'train_type':     train.train_type,
        'distance_km':    train.distance_km,
        'source':         train.source_station,
        'destination':    train.destination_station,
        'departure_time': train.departure_time,
        'arrival_time':   train.arrival_time,
        'available_seats':train.available_seats,
        'status':         train.status,
    })
