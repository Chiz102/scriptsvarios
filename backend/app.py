from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Task, User
import os
from datetime import datetime, timedelta
from sqlalchemy import func, extract

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Cambiar en producción

# Inicializar la base de datos y las migraciones
db.init_app(app)
migrate = Migrate(app, db)

# Crear las tablas si no existen
with app.app_context():
    # Eliminar todas las tablas existentes
    db.drop_all()
    # Crear las tablas con el esquema actualizado
    db.create_all()

# Rutas para servir archivos estáticos
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Rutas de autenticación
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Verificar si el usuario ya existe
    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already registered'}, 400
    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already taken'}, 400
    
    # Crear nuevo usuario
    user = User(
        email=data['email'],
        username=data['username']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return user.to_dict(), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    # Buscar usuario por email
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        return user.to_dict()
    
    return {'error': 'Invalid credentials'}, 401

# Rutas de la API
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    if user_id:
        tasks = Task.query.filter_by(user_id=user_id).all()
    else:
        tasks = Task.query.all()
    return {'tasks': [task.to_dict() for task in tasks]}

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    
    # Verificar que el usuario existe
    user = User.query.get_or_404(data['user_id'])
    
    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        estimated_hours=data.get('estimated_hours', 0),
        actual_hours=data.get('actual_hours', 0),
        category=data.get('category', 'general'),
        tags=','.join(data.get('tags', [])),
        user_id=user.id
    )
    db.session.add(task)
    db.session.commit()
    return task.to_dict()

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)
    task.due_date = datetime.fromisoformat(data['due_date']) if data.get('due_date') else task.due_date
    task.estimated_hours = data.get('estimated_hours', task.estimated_hours)
    task.actual_hours = data.get('actual_hours', task.actual_hours)
    task.category = data.get('category', task.category)
    task.tags = ','.join(data.get('tags', [])) if data.get('tags') else task.tags
    
    if 'status' in data:
        task.update_status(data['status'])
    
    db.session.commit()
    return task.to_dict()

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deleted successfully'}

# Rutas para el calendario
@app.route('/api/calendar/tasks', methods=['GET'])
def get_calendar_tasks():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    query = Task.query
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Task.due_date.between(start, end))
    
    tasks = query.all()
    return {'tasks': [task.to_dict() for task in tasks]}

# Rutas para reportes
@app.route('/api/reports/summary', methods=['GET'])
def get_summary_report():
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status='completed').count()
    pending_tasks = Task.query.filter_by(status='pending').count()
    in_progress_tasks = Task.query.filter_by(status='in_progress').count()
    
    overdue_tasks = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).count()
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

@app.route('/api/reports/by-category', methods=['GET'])
def get_category_report():
    categories = db.session.query(
        Task.category,
        func.count(Task.id).label('total'),
        func.count(Task.completed_date).label('completed')
    ).group_by(Task.category).all()
    
    return {
        'categories': [{
            'name': category,
            'total': total,
            'completed': completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        } for category, total, completed in categories]
    }

@app.route('/api/reports/time-tracking', methods=['GET'])
def get_time_tracking_report():
    tasks = Task.query.filter(Task.completed_date.isnot(None)).all()
    
    total_estimated = sum(task.estimated_hours for task in tasks)
    total_actual = sum(task.actual_hours for task in tasks)
    
    return {
        'total_estimated_hours': total_estimated,
        'total_actual_hours': total_actual,
        'accuracy_rate': (total_estimated / total_actual * 100) if total_actual > 0 else 0,
        'tasks': [{
            'title': task.title,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours,
            'completed_date': task.completed_date.isoformat() if task.completed_date else None
        } for task in tasks]
    }

@app.route('/api/reports/productivity', methods=['GET'])
def get_productivity_report():
    period = request.args.get('period', 'week')  # week, month, year
    
    now = datetime.utcnow()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=365)
    
    tasks = Task.query.filter(
        Task.completed_date.between(start_date, now)
    ).all()
    
    return {
        'total_completed': len(tasks),
        'total_hours': sum(task.actual_hours for task in tasks),
        'by_day': [{
            'date': (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
            'completed': sum(1 for task in tasks if task.completed_date.date() == (start_date + timedelta(days=i)).date()),
            'hours': sum(task.actual_hours for task in tasks if task.completed_date.date() == (start_date + timedelta(days=i)).date())
        } for i in range((now - start_date).days + 1)]
    }

if __name__ == '__main__':
    app.run(debug=True)
