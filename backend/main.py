# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import json

# Importar routers
from backend.routers import projects, drawings, annotations, general_map 
from backend.database import engine, get_db, Base 

# ---------------------------------------------
# INITIALIZE
# ---------------------------------------------
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Lima Project Mapping Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------
# PATH SETUP
# ---------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
GEOJSON_PATH = BASE_DIR / "data" / "geojson" / "lima_callao_distritos.geojson"

# ---------------------------------------------
# STATIC FILES & ROOT
# ---------------------------------------------
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="static")

@app.get("/")
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return {"error": f"Index not found at {index_path}"}
    return FileResponse(index_path)

# ---------------------------------------------
# GEOJSON ENDPOINT (ÚNICO)
# ---------------------------------------------
@app.get("/api/districts-geojson")
def get_districts_geojson():
    """Serve the Lima districts GeoJSON file."""
    if not GEOJSON_PATH.exists():
        raise HTTPException(status_code=404, detail="GeoJSON file not found")
    try:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading GeoJSON file: {e}")

# ---------------------------------------------
# ROUTERS - ORDEN CRÍTICO: MÁS ESPECÍFICO PRIMERO
# ---------------------------------------------

# 1️⃣ PRIMERO: Routers con rutas más específicas (/api/projects/...)
app.include_router(
    projects.router,
    prefix="/api/projects",
    tags=["projects"]
)

app.include_router(
    drawings.router,
    prefix="/api/projects",
    tags=["drawings"]
)

app.include_router(
    annotations.router,
    prefix="/api/projects",
    tags=["annotations"]
)

# 2️⃣ ÚLTIMO: Router general con /api (incluye GET /api/projects y /api/districts)
app.include_router(
    general_map.router,
    prefix="/api",
    tags=["general_map"]
)