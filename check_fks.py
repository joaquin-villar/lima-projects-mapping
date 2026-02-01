
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

def check_all_constraints():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("--- DATABASE CONSTRAINTS CHECK ---")
    for table in tables:
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            if fk['referred_table'] == 'projects':
                print(f"Table '{table}' has FK {fk['constrained_columns']} referencing 'projects'")

if __name__ == "__main__":
    check_all_constraints()
