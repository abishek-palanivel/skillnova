#!/usr/bin/env python3
"""
Database Migration Runner
Applies all pending migrations in order
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import app, db
from sqlalchemy import text

def get_migration_files():
    """Get all migration files in order"""
    migrations_dir = Path(__file__).parent / 'migrations'
    if not migrations_dir.exists():
        print("❌ Migrations directory not found")
        return []
    
    migration_files = sorted(migrations_dir.glob('*.sql'))
    return migration_files

def run_migration(filepath):
    """Run a single migration file"""
    print(f"\n📝 Running migration: {filepath.name}")
    
    try:
        with open(filepath, 'r') as f:
            sql = f.read()
        
        with app.app_context():
            db.session.execute(text(sql))
            db.session.commit()
        
        print(f"✅ Migration {filepath.name} completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration {filepath.name} failed: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("Database Migration Runner")
    print("=" * 70)
    
    migration_files = get_migration_files()
    
    if not migration_files:
        print("\n⚠️  No migration files found")
        return 0
    
    print(f"\n📋 Found {len(migration_files)} migration(s):")
    for mf in migration_files:
        print(f"  - {mf.name}")
    
    print("\n🚀 Starting migrations...")
    
    success_count = 0
    failed_count = 0
    
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
        else:
            failed_count += 1
            print("\n⚠️  Stopping migrations due to error")
            break
    
    print("\n" + "=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print("=" * 70)
    
    if failed_count == 0:
        print("\n🎉 All migrations completed successfully!")
        return 0
    else:
        print("\n⚠️  Some migrations failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
