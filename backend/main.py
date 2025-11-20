from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import json
from pathlib import Path

# Backend internal imports
# Asegúrate de que estos imports apunten a tus archivos reales
from backend.database import engine, get_db, Base
from backend.models import Project, ProjectDistrict, Drawing, Annotation
from backend.schemas import (
    ProjectCreate, 
    ProjectResponse, 
    DrawingCreate, 
    DrawingResponse,
    AnnotationCreate, 
    AnnotationResponse
)
from pydantic import BaseModel # Necesario para el BatchDrawings

# ---------------------------------------------
# INITIALIZE
# ---------------------------------------------
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Lima Project Mapping Dashboard")

# Add CORS middleware to allow requests from browser
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
# Asegúrate de que esta estructura de carpetas sea real en tu disco
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
GEOJSON_PATH = BASE_DIR / "data" / "geojson" / "lima_callao_distritos.geojson"

print(f"📂 BASE_DIR: {BASE_DIR}")
print(f"🌍 GEOJSON_PATH: {GEOJSON_PATH}")
print(f"✅ Exists?: {GEOJSON_PATH.exists()}")

# ---------------------------------------------
# STATIC FILES
# ---------------------------------------------
# Montamos la carpeta frontend para servir JS, CSS e imágenes
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="static")

# ---------------------------------------------
# ROOT INDEX.HTML
# ---------------------------------------------
@app.get("/")
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return {"error": f"Index not found at {index_path}"}
    return FileResponse(index_path)

# ---------------------------------------------
# DISTRICTS GEOJSON
# ---------------------------------------------
@app.get("/api/districts-geojson")
async def get_districts_geojson():
    """Serve the Lima districts GeoJSON file."""
    if not GEOJSON_PATH.exists():
        print(f"❌ Error: GeoJSON not found at {GEOJSON_PATH}")
        raise HTTPException(status_code=404, detail="GeoJSON file not found")

    try:
        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading GeoJSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------
# PROJECT ROUTES
# ---------------------------------------------
@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    result = []
    for project in projects:
        districts = [d.distrito_name for d in project.districts]
        result.append(ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            districts=districts
        ))
    return result

# --- NUEVO ENDPOINT IMPORTANTE PARA STATS (SOPORTE MULTIDISTRITO) ---
@app.get("/api/districts/{distrito}/projects", response_model=List[ProjectResponse])
async def get_projects_by_district(distrito: str, db: Session = Depends(get_db)):
    """
    Get projects. Supports single district ("Lima") or multiple ("Lima, Callao").
    """
    # 1. Separar el string por comas y limpiar espacios
    if "," in distrito:
        district_list = [d.strip() for d in distrito.split(",")]
    else:
        district_list = [distrito.strip()]
    
    # 2. Consulta usando el operador IN con join
    # .distinct() evita duplicados si un proyecto pertenece a varios distritos de la lista
    projects = db.query(Project).join(ProjectDistrict).filter(
        ProjectDistrict.distrito_name.in_(district_list)
    ).distinct().all()
    
    result = []
    for project in projects:
        districts = [d.distrito_name for d in project.districts]
        result.append(ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            districts=districts
        ))
    return result

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    districts = [d.distrito_name for d in project.districts]

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        districts=districts
    )

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        name=project.name,
        description=project.description,
        status=project.status,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for distrito in project.districts:
        db.add(ProjectDistrict(project_id=db_project.id, distrito_name=distrito))

    db.commit()
    db.refresh(db_project)

    districts = [d.distrito_name for d in db_project.districts]

    return ProjectResponse(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at,
        districts=districts
    )

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project.name = project.name
    db_project.description = project.description
    db_project.status = project.status
    db_project.updated_at = datetime.utcnow()

    # Clear existing districts and re-add
    db.query(ProjectDistrict).filter(ProjectDistrict.project_id == project_id).delete()

    for distrito in project.districts:
        db.add(ProjectDistrict(project_id=project_id, distrito_name=distrito))

    db.commit()
    db.refresh(db_project)

    districts = [d.distrito_name for d in db_project.districts]

    return ProjectResponse(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at,
        districts=districts
    )

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted"}


# ============================================================
# DRAWINGS
# ============================================================
@app.get("/api/projects/{project_id}/drawings", response_model=List[DrawingResponse])
async def get_project_drawings(project_id: int, db: Session = Depends(get_db)):
    return db.query(Drawing).filter(Drawing.project_id == project_id).all()

@app.post("/api/projects/{project_id}/drawings")
async def add_drawing(project_id: int, drawing: DrawingCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    db_drawing = Drawing(
        project_id=project_id,
        geojson=json.dumps(drawing.geojson),
        drawing_type=drawing.drawing_type
    )
    db.add(db_drawing)
    db.commit()
    db.refresh(db_drawing)
    return db_drawing

# --- Endpoint Batch para guardar múltiples dibujos en una petición ---
class BatchDrawings(BaseModel):
    drawings: List[DrawingCreate]

@app.post("/api/projects/{project_id}/drawings/batch")
async def add_drawings_batch(project_id: int, batch: BatchDrawings, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    new_drawings = []
    for drawing in batch.drawings:
        db_draw = Drawing(
            project_id=project_id,
            geojson=json.dumps(drawing.geojson),
            drawing_type=drawing.drawing_type
        )
        db.add(db_draw)
        new_drawings.append(db_draw)
    
    db.commit()
    return {"message": f"{len(new_drawings)} drawings added"}

@app.delete("/api/projects/{project_id}/drawings/{drawing_id}")
async def delete_drawing(project_id: int, drawing_id: int, db: Session = Depends(get_db)):
    drawing = db.query(Drawing).filter(
        Drawing.id == drawing_id,
        Drawing.project_id == project_id
    ).first()

    if not drawing:
        raise HTTPException(404, "Drawing not found")

    db.delete(drawing)
    db.commit()
    return {"message": "Drawing deleted"}


# ============================================================
# ANNOTATIONS
# ============================================================
@app.get("/api/projects/{project_id}/annotations", response_model=List[AnnotationResponse])
async def get_annotations(project_id: int, db: Session = Depends(get_db)):
    return db.query(Annotation).filter(Annotation.project_id == project_id).all()

@app.post("/api/projects/{project_id}/annotations")
async def add_annotation(project_id: int, annotation: AnnotationCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    db_annotation = Annotation(
        project_id=project_id,
        distrito_name=annotation.distrito_name,
        title=annotation.title,
        content=annotation.content
    )
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

@app.delete("/api/projects/{project_id}/annotations/{annotation_id}")
async def delete_annotation(project_id: int, annotation_id: int, db: Session = Depends(get_db)):
    annotation = db.query(Annotation).filter(
        Annotation.id == annotation_id,
        Annotation.project_id == project_id
    ).first()

    if not annotation:
        raise HTTPException(404, "Annotation not found")

    db.delete(annotation)
    db.commit()
    return {"message": "Annotation deleted"}