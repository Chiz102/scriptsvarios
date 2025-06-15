# Task Manager

Una aplicación web para gestionar tareas, similar a ClickUp, que permite crear, editar, eliminar y organizar tareas con diferentes prioridades y estados.

## Características

- Creación de tareas con título, descripción, fecha de vencimiento y prioridad
- Filtrado de tareas por estado (Todas, Pendientes, En Progreso, Completadas)
- Marcado de tareas como completadas
- Eliminación de tareas
- Interfaz responsiva y moderna
- Indicadores visuales de prioridad y estado
- Alertas para tareas vencidas

## Requisitos

- Python 3.7+
- pip (gestor de paquetes de Python)
- Navegador web moderno

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd task-manager
```

2. Instalar las dependencias del backend:
```bash
pip install -r requirements.txt
```

## Ejecución

1. Iniciar el servidor backend:
```bash
cd backend
python app.py
```

2. Abrir el archivo `frontend/index.html` en tu navegador web.

## Uso

1. Para crear una nueva tarea:
   - Completa el formulario en el panel izquierdo
   - Haz clic en "Crear Tarea"

2. Para filtrar tareas:
   - Usa los botones en la parte superior de la lista de tareas
   - Selecciona el estado que deseas ver

3. Para marcar una tarea como completada:
   - Haz clic en el botón de check (✓) en la tarea

4. Para eliminar una tarea:
   - Haz clic en el botón de papelera (🗑️) en la tarea

## Tecnologías utilizadas

- Backend:
  - Flask (Python)
  - SQLAlchemy
  - SQLite

- Frontend:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)
  - Bootstrap 5
  - Font Awesome
