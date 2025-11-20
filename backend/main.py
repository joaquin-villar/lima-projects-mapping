from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import json

# Backend internal imports
from backend.database import engine, get_db, Base
from backend.routers import projects, drawings, annotations, general_map 

# ---------------------------------------------
# INITIALIZE
# ---------------------------------------------
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Lima Project Mapping Dashboard")

# Add CORS middleware
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
# GEOJSON ENDPOINT (CORE FILE SERVING)
# ---------------------------------------------
@app.get("/api/districts-geojson")
async def get_districts_geojson():
    """Serve the Lima districts GeoJSON file."""
    if not GEOJSON_PATH.exists():
        raise HTTPException(status_code=404, detail="GeoJSON file not found")

    try:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------
# 🟢 CONEXIÓN FINAL DE ROUTERS
# ---------------------------------------------

# Router principal de Proyectos (CRUD, /api/projects, /api/districts/...)
app.include_router(
    projects.router,
    prefix="/api",
    tags=["projects"]
)

# Router para GeoJSON y Estadísticas Generales
app.include_router(
    general_map.router,
    prefix="/api",
    tags=["general_map"]
)

# Routers anidados para Dibujos (e.g., /api/projects/{project_id}/drawings)
app.include_router(
    drawings.router,
    prefix="/api/projects/{project_id}",
    tags=["drawings"]
)

# Routers anidados para Anotaciones (e.g., /api/projects/{project_id}/annotations)
app.include_router(
    annotations.router,
    prefix="/api/projects/{project_id}",
    tags=["annotations"]
)
