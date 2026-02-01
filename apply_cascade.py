
from sqlalchemy import text, inspect
from backend.database import engine
import os
from dotenv import load_dotenv

load_dotenv()

def apply_cascade_constraints():
    print(f"Applying ON DELETE CASCADE constraints to: {engine.url}")
    
    with engine.begin() as conn:
        # List of tables and their project_id foreign keys to projects(id)
        # We need to drop existing FKs and re-add them with CASCADE.
        # Note: In Postgres, constraint names are often auto-generated if not specified.
        # We'll use a dynamic approach to find and drop.
        
        tables_to_fix = [
            "project_districts", 
            "drawings", 
            "annotations", 
            "edit_history", 
            "edit_suggestions"
        ]
        
        for table in tables_to_fix:
            print(f"Fixing table: {table}")
            try:
                # Find the FK constraint name referencing 'projects'
                query = text("""
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = :table::regclass 
                    AND confrelid = 'projects'::regclass 
                    AND contype = 'f';
                """)
                result = conn.execute(query, {"table": table})
                fks = [row[0] for row in result.fetchall()]
                
                for fk_name in fks:
                    print(f"  Dropping and re-adding constraint: {fk_name}")
                    conn.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT {fk_name}"))
                    conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD CONSTRAINT {fk_name} 
                        FOREIGN KEY (project_id) 
                        REFERENCES projects(id) 
                        ON DELETE CASCADE;
                    """))
                
                if not fks:
                    print(f"  No FK to 'projects' found in {table}. Skipping.")
                    
            except Exception as e:
                print(f"  Error fixing {table}: {e}")

if __name__ == "__main__":
    apply_cascade_constraints()
