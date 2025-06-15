import sqlite3
from datetime import datetime

def view_tasks():
    conn = sqlite3.connect('instance/tasks.db')
    cursor = conn.cursor()
    
    # Obtener todas las tareas
    cursor.execute('SELECT * FROM task')
    tasks = cursor.fetchall()
    
    # Obtener nombres de columnas
    cursor.execute('PRAGMA table_info(task)')
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\n=== Contenido de la base de datos ===")
    print(f"\nColumnas: {', '.join(columns)}")
    print("\nTareas:")
    
    for task in tasks:
        print("\n---")
        for i, value in enumerate(task):
            if value is not None:
                print(f"{columns[i]}: {value}")
    
    conn.close()

if __name__ == '__main__':
    view_tasks() 