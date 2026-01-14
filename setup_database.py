#!/usr/bin/env python
"""
Script de Inicialización de Base de Datos
==========================================
Este script automatiza la configuración inicial de la base de datos:
- Verifica la conexión
- Crea las migraciones
- Aplica las migraciones (crea las tablas)
- Opcionalmente crea un superusuario
- Carga datos iniciales si existen

Uso:
    python setup_database.py
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command, execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model
import subprocess


def print_header(text):
    """Imprime un encabezado decorado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_step(step_num, total_steps, description):
    """Imprime el paso actual"""
    print(f"[{step_num}/{total_steps}] {description}...")


def check_database_connection():
    """Verifica que la conexión a la base de datos funcione"""
    try:
        connection.ensure_connection()
        print(" Conexión a la base de datos exitosa")
        
        # Mostrar información de la BD
        db_settings = connection.settings_dict
        print(f"    Base de datos: {db_settings['NAME']}")
        print(f"    Motor: {db_settings['ENGINE'].split('.')[-1]}")
        if 'HOST' in db_settings and db_settings['HOST']:
            print(f"    Host: {db_settings['HOST']}:{db_settings.get('PORT', 'N/A')}")
        return True
    except Exception as e:
        print(f" Error al conectar con la base de datos:")
        print(f"   {str(e)}")
        print("\n Sugerencias:")
        print("   - Si usas PostgreSQL, asegúrate de que el servidor esté corriendo")
        print("   - Verifica las credenciales en el archivo .env")
        print("   - Si usas PostgreSQL, crea primero la base de datos:")
        print("     CREATE DATABASE cafe_ml_db;")
        return False


def run_makemigrations():
    """Crea los archivos de migración"""
    try:
        print(" Creando archivos de migración...")
        call_command('makemigrations', verbosity=1)
        print(" Migraciones creadas correctamente")
        return True
    except Exception as e:
        print(f" Error al crear migraciones: {e}")
        return False


def run_migrate():
    """Aplica las migraciones (crea las tablas)"""
    try:
        print(" Aplicando migraciones (creando tablas)...")
        call_command('migrate', verbosity=1)
        print(" Tablas creadas correctamente")
        return True
    except Exception as e:
        print(f" Error al aplicar migraciones: {e}")
        return False


def show_created_tables():
    """Muestra las tablas creadas"""
    try:
        with connection.cursor() as cursor:
            # Obtener nombre de todas las tablas
            if 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' 
                    ORDER BY tablename;
                """)
            elif 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    ORDER BY name;
                """)
            else:
                cursor.execute("SHOW TABLES;")
            
            tables = cursor.fetchall()
            
            print("\n Tablas creadas en la base de datos:")
            for table in tables:
                table_name = table[0]
                # Destacar las tablas de nuestra app
                if 'cafe_app' in table_name:
                    print(f"    {table_name}")
                else:
                    print(f"   • {table_name}")
                    
    except Exception as e:
        print(f"  No se pudieron listar las tablas: {e}")


def create_superuser():
    """Pregunta si desea crear un superusuario"""
    User = get_user_model()
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("\n Ya existe al menos un superusuario")
        return
    
    print("\n" + "-"*70)
    response = input("¿Deseas crear un superusuario para acceder al admin? (s/n): ").lower()
    
    if response == 's':
        print("\n Creando superusuario...")
        try:
            call_command('createsuperuser')
            print(" Superusuario creado exitosamente")
        except KeyboardInterrupt:
            print("\n  Creación de superusuario cancelada")
        except Exception as e:
            print(f" Error al crear superusuario: {e}")
    else:
        print("  Saltando creación de superusuario")
        print("   Puedes crearlo después con: python manage.py createsuperuser")


def load_initial_data():
    """Carga datos iniciales si existen fixtures"""
    fixtures_dir = BASE_DIR / 'cafe_app' / 'fixtures'
    
    if fixtures_dir.exists() and any(fixtures_dir.glob('*.json')):
        print("\n" + "-"*70)
        response = input("¿Deseas cargar datos iniciales? (s/n): ").lower()
        
        if response == 's':
            try:
                print(" Cargando datos iniciales...")
                call_command('loaddata', 'initial_data.json', verbosity=1)
                print(" Datos iniciales cargados")
            except Exception as e:
                print(f"  No se pudieron cargar datos iniciales: {e}")
    else:
        print("\n  No hay datos iniciales para cargar")


def main():
    """Función principal"""
    print_header(" CONFIGURACIÓN INICIAL DE BASE DE DATOS")
    print("Este script configurará automáticamente tu base de datos\n")
    
    total_steps = 5
    current_step = 0
    
    # Paso 1: Verificar conexión
    current_step += 1
    print_step(current_step, total_steps, "Verificando conexión a la base de datos")
    if not check_database_connection():
        print("\n No se puede continuar sin conexión a la base de datos")
        sys.exit(1)
    
    # Paso 2: Crear migraciones
    current_step += 1
    print_step(current_step, total_steps, "Creando archivos de migración")
    if not run_makemigrations():
        print("\n  Hubo problemas al crear las migraciones")
    
    # Paso 3: Aplicar migraciones
    current_step += 1
    print_step(current_step, total_steps, "Aplicando migraciones y creando tablas")
    if not run_migrate():
        print("\n No se pudieron crear las tablas")
        sys.exit(1)
    
    # Mostrar tablas creadas
    show_created_tables()
    
    # Paso 4: Crear superusuario
    current_step += 1
    print_step(current_step, total_steps, "Configuración de superusuario")
    create_superuser()
    
    # Paso 5: Cargar datos iniciales (si existen)
    current_step += 1
    print_step(current_step, total_steps, "Carga de datos iniciales")
    load_initial_data()
    
    # Resumen final
    print_header(" CONFIGURACIÓN COMPLETADA")
    print("🎉 La base de datos está lista para usar!\n")
    print(" Próximos pasos:")
    print("   1. Iniciar el servidor: python manage.py runserver")
    print("   2. Acceder al admin: http://127.0.0.1:8000/admin/")
    print("   3. Probar la API: http://127.0.0.1:8000/api/")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
