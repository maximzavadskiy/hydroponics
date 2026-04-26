from flask import Flask, render_template, jsonify, send_file, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import plotly.graph_objects as go
from pathlib import Path
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hydroponics.db'
db = SQLAlchemy(app)

# Database model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    tds_voltage = db.Column(db.Float)
    motor_speed = db.Column(db.Float, default=1.0)
    light_on = db.Column(db.Boolean, default=False)

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/sensor-data')
def get_sensor_data():
    hours = int(request.args.get('hours', 24))
    since = datetime.utcnow() - timedelta(hours=hours)
    data = SensorData.query.filter(SensorData.timestamp >= since).order_by(SensorData.timestamp).all()

    return jsonify([{
        'timestamp': d.timestamp.isoformat(),
        'ph': d.ph,
        'tds': d.tds,
        'tds_voltage': d.tds_voltage,
        'motor_speed': d.motor_speed,
        'light_on': d.light_on
    } for d in data])

@app.route('/api/plot-ph')
def plot_ph():
    hours = int(request.args.get('hours', 24))
    since = datetime.utcnow() - timedelta(hours=hours)
    data = SensorData.query.filter(SensorData.timestamp >= since).order_by(SensorData.timestamp).all()

    timestamps = [d.timestamp.strftime('%H:%M') for d in data]
    ph_values = [d.ph for d in data]

    return jsonify({
        'x': timestamps,
        'y': ph_values,
        'title': 'pH Over Time',
        'yaxis': 'pH'
    })

@app.route('/api/plot-tds')
def plot_tds():
    hours = int(request.args.get('hours', 24))
    since = datetime.utcnow() - timedelta(hours=hours)
    data = SensorData.query.filter(SensorData.timestamp >= since).order_by(SensorData.timestamp).all()

    timestamps = [d.timestamp.strftime('%H:%M') for d in data]
    tds_values = [d.tds for d in data]

    return jsonify({
        'x': timestamps,
        'y': tds_values,
        'title': 'TDS Over Time',
        'yaxis': 'TDS (ppm)'
    })

@app.route('/api/snapshots')
def get_snapshots():
    snapshots = Snapshot.query.order_by(Snapshot.timestamp.desc()).all()
    return jsonify([{
        'filename': s.filename,
        'timestamp': s.timestamp.isoformat()
    } for s in snapshots])

@app.route('/snapshots/<filename>')
def serve_snapshot(filename):
    snapshot_dir = Path(__file__).parent / "snapshots"
    return send_file(snapshot_dir / filename)

app_start_time = datetime.utcnow()

@app.route('/api/app-status')
def app_status():
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()

    if latest:
        time_since_update = (datetime.utcnow() - latest.timestamp).total_seconds()
        is_alive = time_since_update < 30
    else:
        time_since_update = float('inf')
        is_alive = False

    uptime = datetime.utcnow() - app_start_time
    uptime_str = format_uptime(uptime)

    return jsonify({
        'alive': is_alive,
        'time_since_update': int(time_since_update),
        'last_update': latest.timestamp.isoformat() if latest else None,
        'uptime': uptime_str,
        'app_start_time': app_start_time.isoformat()
    })

def format_uptime(td):
    """Format timedelta as '2d 3h 45m'"""
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    return ' '.join(parts) if parts else '0m'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
