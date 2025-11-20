# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# 1. Cargar variables de entorno
load_dotenv()

# 2. Obtener la URL de la base de datos
DATABASE_URL = os.getenv("POSTGRES_URL")

# ---------------------------------------------
# 3. Configuración del Motor (Engine)
# ---------------------------------------------
if DATABASE_URL:
    # --- MODO POSTGRES (Nube / Vercel) ---
    
    # Corrección de protocolo
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Configuración de seguridad
    connect_args = {"sslmode": "require"}

    engine = create_engine(
        DATABASE_URL, 
        pool_pre_ping=True,
        connect_args=connect_args
    )
    print("✅ MODO: Producción (Postgres en la Nube)")

else:
    # --- MODO SQLITE (Fallback Local) ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "lima_local_dev.db"
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    print(f"\n ⚠️  MODO: Desarrollo Local (SQLite en {DB_PATH.name})")
    print("   Los datos NO se sincronizarán con la nube. \n")

# 4. Configuración de Sesión y Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_all_tables():
    """Ejecuta la creación de todas las tablas definidas en Base.metadata."""
    Base.metadata.create_all(bind=engine)

# 5. Dependencia para FastAPI
def get_db():
    db = SessionLocal()
    try:
        db.connection()
        yield db
    finally:
        db.close()