#!/usr/bin/env python3
"""
One-time script to add key_document_type column to document table.
Use this if alembic upgrade fails or hasn't been run.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    from src.app import create_app
    from src.app import db
    from sqlalchemy import text

    app = create_app()
    with app.app_context():
        dialect = db.engine.dialect.name
        conn = db.engine.connect()

        # Check if column exists
        if dialect == 'sqlite':
            result = conn.execute(text("PRAGMA table_info(document)"))
            cols = [row[1] for row in result.fetchall()]
            has_col = 'key_document_type' in cols
        else:
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'document' AND column_name = 'key_document_type'
            """))
            has_col = result.fetchone() is not None

        if has_col:
            print("Column key_document_type already exists. Nothing to do.")
            conn.close()
            return 0

        print("Adding key_document_type column to document table...")
        conn.execute(text("ALTER TABLE document ADD COLUMN key_document_type VARCHAR(50)"))
        conn.commit()

        # Create index (skip if exists - SQLite will error on duplicate index name)
        try:
            conn.execute(text("CREATE INDEX ix_document_key_type_room ON document (room_id, key_document_type)"))
            conn.commit()
            print("Index ix_document_key_type_room created.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("Index already exists, skipping.")
            else:
                raise

        conn.close()
        print("Done. key_document_type column has been added.")

    return 0

if __name__ == '__main__':
    sys.exit(main())
