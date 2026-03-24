from flask import Blueprint, render_template, request
from flask_login import login_required

fare_bp = Blueprint('fare', __name__, url_prefix='/fare')

FARE_BASE   = {"Sleeper": 1.0, "General": 0.8, "AC 3-Tier": 2.0, "AC 2-Tier": 3.0}
FARE_CHARGE = {"Passenger": 0.0, "Mail": 0.05, "Express": 0.10,
               "Superfast": 0.20, "Rajdhani": 0.30, "Shatabdi": 0.35}


@fare_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    result = None
    if request.method == 'POST':
        train_class = request.form['train_class']
        train_type  = request.form['train_type']
        distance    = float(request.form['distance'])
        base  = distance * FARE_BASE.get(train_class, 1.0)
        fare  = round(base * (1 + FARE_CHARGE.get(train_type, 0.0)), 2)
        result = {
            'fare':     fare,
            'class':    train_class,
            'type':     train_type,
            'distance': distance,
        }
    return render_template('fare/index.html', result=result,
                           classes=list(FARE_BASE.keys()),
                           types=list(FARE_CHARGE.keys()))
