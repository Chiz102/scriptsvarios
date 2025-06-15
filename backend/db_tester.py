from app import app, db
from models import Task, User
from datetime import datetime, timedelta
import random

def generate_sample_users(num_users=5):
    """Genera usuarios de ejemplo"""
    users = []
    for i in range(num_users):
        user = User(
            email=f"user{i+1}@example.com",
            username=f"user{i+1}"
        )
        user.set_password(f"password{i+1}")
        users.append(user)
    return users

def generate_sample_tasks(users, num_tasks=20):
    """Genera un conjunto de tareas de ejemplo con datos realistas"""
    
    categories = ["desarrollo", "diseño", "marketing", "testing", "documentación", "soporte"]
    priorities = ["low", "medium", "high"]
    statuses = ["pending", "in_progress", "completed"]
    
    # Tags comunes por categoría
    category_tags = {
        "desarrollo": ["backend", "frontend", "api", "database", "security", "python", "javascript"],
        "diseño": ["ui", "ux", "mockup", "prototype", "responsive", "mobile", "web"],
        "marketing": ["social", "content", "email", "seo", "analytics", "campaign"],
        "testing": ["unit", "integration", "e2e", "performance", "security", "qa"],
        "documentación": ["api", "user-guide", "technical", "requirements", "specs"],
        "soporte": ["bug", "feature", "customer", "internal", "maintenance"]
    }
    
    tasks = []
    now = datetime.now()
    
    for i in range(num_tasks):
        # Asignar un usuario aleatorio
        user = random.choice(users)
        
        # Seleccionar categoría y tags relacionados
        category = random.choice(categories)
        num_tags = random.randint(2, 4)
        tags = ','.join(random.sample(category_tags[category], num_tags))
        
        # Determinar estado y fechas relacionadas
        status = random.choice(statuses)
        created_days_ago = random.randint(1, 30)
        created_at = now - timedelta(days=created_days_ago)
        
        # Configurar fechas según el estado
        if status == "completed":
            completed_date = created_at + timedelta(days=random.randint(1, 5))
            due_date = completed_date - timedelta(days=random.randint(0, 2))
        else:
            completed_date = None
            due_date = now + timedelta(days=random.randint(-5, 15))
        
        # Generar horas estimadas y reales
        estimated_hours = random.randint(2, 16)
        if status == "completed":
            actual_hours = estimated_hours + random.randint(-4, 4)  # Variación realista
        elif status == "in_progress":
            actual_hours = estimated_hours * random.uniform(0.2, 0.8)  # Progreso parcial
        else:
            actual_hours = 0
        
        task = Task(
            title=f"Tarea {i+1} de {category.title()}",
            description=f"Descripción detallada de la tarea {i+1} en la categoría {category}",
            status=status,
            priority=random.choice(priorities),
            due_date=due_date,
            completed_date=completed_date,
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            category=category,
            tags=tags,
            created_at=created_at,
            updated_at=created_at + timedelta(days=random.randint(0, 3)),
            user_id=user.id
        )
        tasks.append(task)
    
    return tasks

def test_database():
    with app.app_context():
        print("\n=== Probando la base de datos con datos extendidos ===")
        
        # Limpiar la base de datos
        print("\nLimpiando base de datos...")
        Task.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Crear usuarios de prueba
        print("\nCreando usuarios de prueba...")
        users = generate_sample_users()
        for user in users:
            db.session.add(user)
        db.session.commit()
        print(f"¡{len(users)} usuarios creados exitosamente!")
        
        # Crear tareas de prueba
        print("\nCreando tareas de prueba...")
        tasks = generate_sample_tasks(users)
        
        for task in tasks:
            db.session.add(task)
        
        db.session.commit()
        print(f"¡{len(tasks)} tareas creadas exitosamente!")
        
        # Análisis detallado de los datos
        print("\n=== Análisis de Datos ===")
        
        # Estadísticas por usuario
        print("\nEstadísticas por Usuario:")
        for user in users:
            user_tasks = Task.query.filter_by(user_id=user.id).all()
            total_tasks = len(user_tasks)
            completed_tasks = sum(1 for task in user_tasks if task.status == "completed")
            completion_rate = (completed_tasks/total_tasks*100) if total_tasks > 0 else 0
            print(f"\nUsuario: {user.username}")
            print(f"- Total de tareas: {total_tasks}")
            print(f"- Tareas completadas: {completed_tasks}")
            print(f"- Tasa de completitud: {completion_rate:.1f}%")
        
        # Estadísticas generales
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status="completed").count()
        overdue_tasks = Task.query.filter(
            Task.due_date < datetime.now(),
            Task.status != "completed"
        ).count()
        
        print(f"\nEstadísticas Generales:")
        print(f"- Total de tareas: {total_tasks}")
        print(f"- Tareas completadas: {completed_tasks}")
        print(f"- Tasa de completitud: {(completed_tasks/total_tasks*100):.1f}%")
        print(f"- Tareas vencidas: {overdue_tasks}")
        
        # Análisis por categoría
        print("\nDistribución por Categoría:")
        categories = db.session.query(
            Task.category,
            db.func.count(Task.id).label('total'),
            db.func.count(Task.completed_date).label('completed')
        ).group_by(Task.category).all()
        
        for category, total, completed in categories:
            completion_rate = (completed/total*100) if total > 0 else 0
            print(f"- {category}: {total} tareas, {completed} completadas ({completion_rate:.1f}%)")
        
        # Análisis de tiempo
        print("\nAnálisis de Tiempo:")
        completed_tasks = Task.query.filter(
            Task.completed_date.isnot(None)
        ).all()
        
        total_estimated = sum(task.estimated_hours for task in completed_tasks)
        total_actual = sum(task.actual_hours for task in completed_tasks)
        
        if total_estimated > 0:
            accuracy = (total_estimated/total_actual*100)
            print(f"- Horas totales estimadas: {total_estimated:.1f}")
            print(f"- Horas totales reales: {total_actual:.1f}")
            print(f"- Precisión de estimación: {accuracy:.1f}%")
        
        # Análisis de prioridades
        print("\nDistribución por Prioridad:")
        priorities = db.session.query(
            Task.priority,
            db.func.count(Task.id)
        ).group_by(Task.priority).all()
        
        for priority, count in priorities:
            percentage = (count/total_tasks*100)
            print(f"- {priority}: {count} tareas ({percentage:.1f}%)")
        
        # Análisis de tendencias por usuario
        print("\nTendencias de Completitud por Usuario (últimos 7 días):")
        last_week = datetime.now() - timedelta(days=7)
        
        for user in users:
            print(f"\nUsuario: {user.username}")
            daily_completed = db.session.query(
                db.func.date(Task.completed_date),
                db.func.count(Task.id)
            ).filter(
                Task.completed_date >= last_week,
                Task.user_id == user.id
            ).group_by(
                db.func.date(Task.completed_date)
            ).all()
            
            for date, count in daily_completed:
                print(f"- {date}: {count} tareas completadas")

if __name__ == "__main__":
    test_database() 