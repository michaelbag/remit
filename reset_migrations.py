#!/usr/bin/env python3
"""
Скрипт для сброса миграций Django
Удаляет все файлы миграций кроме __init__.py
"""

import os
import glob
import shutil
from pathlib import Path

def reset_migrations():
    """Удаляет все файлы миграций кроме __init__.py"""
    
    # Найти все директории migrations
    migrations_dirs = []
    
    # Проверить apps/ директорию
    apps_dir = Path("apps")
    if apps_dir.exists():
        for app_dir in apps_dir.iterdir():
            if app_dir.is_dir() and (app_dir / "migrations").exists():
                migrations_dirs.append(app_dir / "migrations")
    
    # Проверить корневую директорию для других приложений
    for item in Path(".").iterdir():
        if item.is_dir() and not item.name.startswith('.') and (item / "migrations").exists():
            migrations_dirs.append(item / "migrations")
    
    print(f"Найдено директорий migrations: {len(migrations_dirs)}")
    
    for migrations_dir in migrations_dirs:
        print(f"\nОбрабатываем: {migrations_dir}")
        
        # Найти все файлы миграций кроме __init__.py
        migration_files = list(migrations_dir.glob("*.py"))
        migration_files = [f for f in migration_files if f.name != "__init__.py"]
        
        print(f"  Найдено файлов миграций: {len(migration_files)}")
        
        # Создать резервную копию
        backup_dir = migrations_dir.parent / "migrations_backup"
        if not backup_dir.exists():
            backup_dir.mkdir()
            print(f"  Создана резервная копия в: {backup_dir}")
        
        # Скопировать файлы в резервную копию
        for migration_file in migration_files:
            backup_file = backup_dir / migration_file.name
            shutil.copy2(migration_file, backup_file)
            print(f"    Резервная копия: {migration_file.name}")
        
        # Удалить файлы миграций
        for migration_file in migration_files:
            migration_file.unlink()
            print(f"    Удален: {migration_file.name}")
    
    print("\n✅ Сброс миграций завершен!")
    print("📁 Резервные копии сохранены в директориях migrations_backup/")

if __name__ == "__main__":
    print("🔄 Начинаем сброс миграций...")
    reset_migrations()
