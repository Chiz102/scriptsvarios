from datetime import datetime, timedelta
import random
from app import app, db
from models import User, Task

def seed_database():
    print("Iniciando la generación de datos de prueba...")
    
    # Limpiar la base de datos
    print("Limpiando la base de datos...")
    db.drop_all()
    db.create_all()
    
    # Crear usuario de prueba
    print("Creando usuario de prueba...")
    test_user = User(
        username="usuario_prueba",
        email="test@example.com"
    )
    test_user.set_password("password123")
    db.session.add(test_user)
    db.session.commit()

    # Categorías de ejemplo
    categories = ["Desarrollo", "Diseño", "Marketing", "Pruebas", "Documentación", "Soporte"]
    
    # Estados posibles
    statuses = ["pending", "in_progress", "completed"]
    
    # Prioridades
    priorities = ["low", "medium", "high"]
    
    # Etiquetas comunes
    common_tags = [
        "urgente", "bug", "feature", "mejora", "frontend", "backend", 
        "api", "ui", "ux", "testing", "documentación", "reunión"
    ]

    # Generar tareas de ejemplo
    print("Generando tareas de ejemplo...")
    now = datetime.now()
    
    # Lista de títulos y descripciones de ejemplo
    sample_tasks = [
        {
            "title": "Implementar autenticación de usuarios",
            "description": "Desarrollar sistema de login y registro usando JWT",
            "category": "Desarrollo",
            "estimated_hours": 8
        },
        {
            "title": "Diseñar nueva página de inicio",
            "description": "Crear diseño responsive siguiendo la guía de estilos",
            "category": "Diseño",
            "estimated_hours": 6
        },
        {
            "title": "Optimizar rendimiento de la base de datos",
            "description": "Analizar y mejorar las consultas SQL más lentas",
            "category": "Desarrollo",
            "estimated_hours": 4
        },
        {
            "title": "Crear campaña de email marketing",
            "description": "Diseñar y programar campaña para el nuevo lanzamiento",
            "category": "Marketing",
            "estimated_hours": 5
        },
        {
            "title": "Realizar pruebas de integración",
            "description": "Ejecutar suite de pruebas en el módulo de pagos",
            "category": "Pruebas",
            "estimated_hours": 3
        },
        {
            "title": "Actualizar documentación API",
            "description": "Documentar nuevos endpoints y actualizar ejemplos",
            "category": "Documentación",
            "estimated_hours": 4
        },
        {
            "title": "Resolver tickets de soporte pendientes",
            "description": "Atender tickets prioritarios de la última semana",
            "category": "Soporte",
            "estimated_hours": 6
        },
        {
            "title": "Implementar nuevo diseño de dashboard",
            "description": "Aplicar el nuevo diseño de UI al dashboard principal",
            "category": "Diseño",
            "estimated_hours": 7
        },
        {
            "title": "Configurar servidor de staging",
            "description": "Preparar ambiente de pruebas con la última versión",
            "category": "Desarrollo",
            "estimated_hours": 5
        },
        {
            "title": "Análisis de métricas de usuario",
            "description": "Revisar y reportar KPIs del último mes",
            "category": "Marketing",
            "estimated_hours": 4
        },
        {
            "title": "Implementar sistema de notificaciones",
            "description": "Desarrollar sistema de notificaciones en tiempo real",
            "category": "Desarrollo",
            "estimated_hours": 10
        },
        {
            "title": "Actualizar librerías del proyecto",
            "description": "Actualizar dependencias a las últimas versiones estables",
            "category": "Desarrollo",
            "estimated_hours": 3
        },
        {
            "title": "Diseñar iconos personalizados",
            "description": "Crear set de iconos para la nueva funcionalidad",
            "category": "Diseño",
            "estimated_hours": 5
        },
        {
            "title": "Implementar dark mode",
            "description": "Añadir soporte para tema oscuro en toda la aplicación",
            "category": "Desarrollo",
            "estimated_hours": 6
        },
        {
            "title": "Optimizar imágenes del sitio",
            "description": "Comprimir y optimizar todas las imágenes del sitio",
            "category": "Desarrollo",
            "estimated_hours": 2
        }
    ]

    for task_data in sample_tasks:
        # Generar fecha aleatoria en los últimos 30 días
        days_offset = random.randint(-30, 30)
        due_date = now + timedelta(days=days_offset)
        
        # Para tareas completadas, generar fecha de completitud
        status = random.choice(statuses)
        completed_date = None
        if status == "completed":
            completed_date = due_date - timedelta(days=random.randint(0, 3))
        
        # Generar horas reales basadas en las estimadas
        estimated_hours = task_data["estimated_hours"]
        if status == "completed":
            # Variar un poco las horas reales respecto a las estimadas
            actual_hours = estimated_hours + random.uniform(-2, 2)
            actual_hours = max(0.5, round(actual_hours, 1))  # Asegurar que no sea negativo
        else:
            actual_hours = None if status == "pending" else estimated_hours * random.uniform(0.1, 0.9)
            if actual_hours:
                actual_hours = round(actual_hours, 1)

        # Generar tags aleatorios
        num_tags = random.randint(1, 3)
        tags = random.sample(common_tags, num_tags)

        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            status=status,
            priority=random.choice(priorities),
            due_date=due_date,
            completed_date=completed_date,
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            category=task_data["category"],
            tags=tags,
            user_id=test_user.id,
            created_at=now - timedelta(days=random.randint(1, 60)),
            updated_at=now - timedelta(days=random.randint(0, 30))
        )
        db.session.add(task)

    # Guardar todos los cambios
    print("Guardando cambios en la base de datos...")
    db.session.commit()
    print("¡Datos de prueba generados exitosamente!")

if __name__ == "__main__":
    with app.app_context():
        seed_database() 