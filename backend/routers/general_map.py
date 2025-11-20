from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from typing import List, Dict, Any
from urllib.parse import unquote
from sqlalchemy import distinct
from pathlib import Path # 👈 Importación faltante
import os # 👈 FIX: Importación crítica faltante
import json # 👈 FIX: Importación faltante

router = APIRouter(prefix="/api", tags=["General Map & Districts"])

# -------------------------------------------------------------
# Helper para obtener la lista de distritos desde el URL (Multiselect)
# -------------------------------------------------------------
def get_district_list_from_param(district_param: str) -> List[str]:
    """Decodifica el string y lo convierte en una lista de distritos."""
    decoded_param = unquote(district_param)
    return [d.strip() for d in decoded_param.split(',')]

# -------------------------------------------------------------
# Rutas de Proyectos (Multiselect)
# -------------------------------------------------------------
@router.get("/districts/{district_name}/projects", response_model=List[schemas.ProjectResponse])
def get_district_projects(district_name: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los proyectos para el/los distritos seleccionados.
    Soporta multiselección (ej: 'Ate, Breña').
    """
    district_list = get_district_list_from_param(district_name)
    
    # Consulta: Proyectos que tengan AL MENOS una asociación con CUALQUIERA de los distritos en la lista
    projects = db.query(models.Project).join(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name.in_(district_list)
    ).distinct().order_by(models.Project.created_at.desc()).all()
    
    # Nota: ProjectResponse debe tener from_orm activado
    return [schemas.ProjectResponse.from_orm(p) for p in projects]

# -------------------------------------------------------------
# Rutas de Estadísticas (Multiselect)
# -------------------------------------------------------------
@router.get("/districts/{district_name}/stats", response_model=Dict[str, Any])
def get_district_stats(district_name: str, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas combinadas para el/los distritos seleccionados.
    """
    district_list = get_district_list_from_param(district_name)
    
    # Obtenemos los proyectos relevantes
    projects_query = db.query(models.Project).join(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name.in_(district_list)
    ).distinct()
    
    projects = projects_query.all()
    
    # Calcular estadísticas en Python (FastAPI)
    total = len(projects)
    active = sum(1 for p in projects if p.status == 'active')
    inactive = sum(1 for p in projects if p.status == 'inactive')
    completed = sum(1 for p in projects if p.status == 'completed')
    archived = sum(1 for p in projects if p.status == 'archived')
    
    # Crear el título para el frontend (ej: "Lima, Callao" o "2 Distritos Seleccionados")
    display_name = ', '.join(district_list)
    
    return {
        "district": display_name,
        "total": total,
        "active": active,
        "inactive": inactive,
        "completed": completed,
        "archived": archived
    }

# -------------------------------------------------------------
# Ruta de GeoJSON (Se queda aquí, no en main.py)
# -------------------------------------------------------------
# 🟢 FIX: Usamos Pathlib para una gestión de rutas más robusta
BASE_DIR = Path(__file__).resolve().parent.parent.parent
GEOJSON_PATH = BASE_DIR / "data" / "geojson" / "lima_callao_distritos.geojson"

@router.get("/districts-geojson")
def get_districts_geojson():
    if not GEOJSON_PATH.exists(): # Usamos .exists() de Pathlib
        raise HTTPException(404, "GeoJSON file not found")
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)