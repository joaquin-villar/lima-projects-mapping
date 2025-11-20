import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Cargar variables de entorno (para que funcione en tu laptop con el archivo .env)
load_dotenv()

# 2. Obtener la URL de la base de datos desde el entorno
DATABASE_URL = os.getenv("POSTGRES_URL")

# 3. Configuración del Motor (Engine)
if DATABASE_URL:
    # --- MODO POSTGRES (Nube / Vercel) ---
    # Corrección necesaria: Vercel entrega 'postgres://' pero SQLAlchemy requiere 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Creamos el motor para Postgres
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("✅ Conectado a Postgres")

else:
    # --- MODO ERROR (Si olvidaste el .env) ---
    # Esto es para evitar que la app arranque si no tiene base de datos conectada
    print("❌ ERROR CRÍTICO: No se encontró la variable POSTGRES_URL.")
    print("   - Si estás en Vercel: Revisa que la DB esté conectada en la pestaña Storage.")
    print("   - Si estás en Local: Asegúrate de tener el archivo .env con la URL.")
    
    # Fallback temporal a SQLite solo para que no explote al importar, 
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data", "db", "temp_fallback.db")
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

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