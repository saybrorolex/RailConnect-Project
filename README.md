# 🚂 RailConnect

A full-stack Railway Management System built with **Flask**, **MySQL**, and vanilla **HTML/CSS/JS**. Manage trains, book tickets, track passengers, and visualize analytics — all from a clean railway-themed web interface.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔐 **Auth** | Role-based login — Admin and Passenger accounts |
| 📊 **Dashboard** | Live KPIs, revenue charts, booking status breakdown |
| 🚂 **Train Management** | Full CRUD — add, edit, delete, filter trains (Admin only) |
| 🎫 **Ticket Booking** | Live fare preview, seat auto-assignment, payment methods |
| 🔄 **Upgrade / Cancel** | Upgrade class with live fare diff, cancel anytime |
| 📈 **Analytics** | 6 interactive charts — histograms, doughnuts, bar/line charts |
| 🔍 **Search System** | Multi-filter search for trains and passengers |
| 🧮 **Fare Calculator** | Calculate fare by class, train type, and distance |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy, Flask-Login
- **Database**: MySQL (local) / Railway MySQL or Render PostgreSQL (production)
- **Frontend**: HTML5, CSS3 (custom), Vanilla JavaScript, Chart.js
- **Fonts**: Bebas Neue, DM Sans, JetBrains Mono
- **Deployment**: Render.com or Railway.app

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/railconnect.git
cd railconnect
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your MySQL credentials and a secret key
```

### 5. Create the MySQL database
```sql
CREATE DATABASE railconnect;
```

### 6. Migrate existing CSV data (first time only)
```bash
# Place your CSV files in the project root first:
#   Trains Data.csv
#   Passenger Data.csv
python migrate_data.py
```
This creates all tables, imports your CSV data, and creates a default admin account:
- **Email**: `admin@railconnect.com`
- **Password**: `admin123`
> ⚠️ Change the admin password immediately after first login!

### 7. Run the development server
```bash
python app.py
# → http://localhost:5000
```

---

## ☁️ Deploying to Render.com (Recommended — Free Tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repo — Render will auto-detect `render.yaml`
4. It will provision a **web service** + **MySQL database** automatically
5. Add your `SECRET_KEY` in the Render environment variables dashboard
6. After deploy, run the migration:
   ```bash
   # In Render dashboard → your service → Shell
   python migrate_data.py
   ```

---

## 🚃 Deploying to Railway.app (Alternative)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Add a **MySQL** plugin from the Railway dashboard
4. Set environment variables:
   - `SECRET_KEY` → any random string
   - `DATABASE_URL` → Railway auto-populates this from the MySQL plugin
5. Railway auto-detects `railway.toml` and deploys
6. Run migration via Railway's shell panel

---

## 📁 Project Structure

```
railconnect/
├── app.py                  # Flask app factory
├── config.py               # Configuration (reads from env vars)
├── extensions.py           # SQLAlchemy + Flask-Login instances
├── models.py               # User, Train, Booking models
├── migrate_data.py         # CSV → MySQL one-time import script
├── requirements.txt
├── Procfile                # Gunicorn start command
├── render.yaml             # Render.com deployment config
├── railway.toml            # Railway.app deployment config
├── .env.example            # Environment variable template
├── .gitignore
├── routes/
│   ├── auth.py             # Login, Register, Logout
│   ├── dashboard.py        # Dashboard with live charts
│   ├── trains.py           # Train CRUD
│   ├── bookings.py         # Booking flow + cancel/upgrade
│   ├── analytics.py        # Analytics charts
│   ├── search.py           # Search system
│   └── fare.py             # Fare calculator
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── trains/
│   ├── bookings/
│   ├── analytics/
│   ├── search/
│   └── fare/
└── static/
    ├── css/style.css       # Railway-themed dark UI
    └── js/main.js
```

---

## 🔐 Role Permissions

| Action | Admin | Passenger |
|--------|-------|-----------|
| View all trains | ✅ | ✅ |
| Add / Edit / Delete trains | ✅ | ❌ |
| View all bookings | ✅ | Own only |
| Book a ticket | ✅ | ✅ |
| Cancel / Upgrade ticket | ✅ | Own only |
| View analytics | ✅ | ✅ |
| Search all passengers | ✅ | ❌ |

---

## 📄 License

MIT License — free to use, modify, and distribute.
