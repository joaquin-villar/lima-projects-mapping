import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path # Importar para manejo robusto de rutas

# 1. Cargar variables de entorno
load_dotenv()

# 2. Obtener la URL de la base de datos desde el entorno
DATABASE_URL = os.getenv("POSTGRES_URL")

# ---------------------------------------------
# 3. Configuración del Motor (Engine)
# ---------------------------------------------
if DATABASE_URL:
    # --- MODO POSTGRES (Nube / Vercel) ---
    # Corrección necesaria: Vercel entrega 'postgres://' pero SQLAlchemy requiere 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Creamos el motor para Postgres
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("✅ MODO: Producción (Postgres en la Nube)")

else:
    # --- MODO FALLBACK (Desarrollo Local / SQLite) ---
    # Creamos un archivo DB local para desarrollo offline
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "lima_local_dev.db" # Archivo SQLite persistente
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        # Requerido por SQLite con FastAPI
        connect_args={"check_same_thread": False} 
    )
    print(f"⚠️ MODO: Local Fallback (SQLite en {DB_PATH})")
    print("   Los proyectos creados aquí NO se sincronizan con la nube.")
    print("   Para usar la nube, crea un archivo .env con la variable POSTGRES_URL.")


# 4. Configuración de Sesión y Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 5. Dependencia para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()