from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend import models, schemas
from typing import List, Dict, Any
from urllib.parse import unquote

router = APIRouter(tags=["General Map & Districts"])

# -------------------------------------------------------------
# Helper function
# -------------------------------------------------------------
def get_district_list_from_param(district_param: str) -> List[str]:
    """Decodifica y divide nombres de distritos del parámetro URL."""
    decoded_param = unquote(district_param)
    return [d.strip() for d in decoded_param.split(',')]

# -------------------------------------------------------------
# Rutas de distritos
# -------------------------------------------------------------

@router.get("/districts/{district_name}/projects", response_model=List[schemas.ProjectResponse])
def get_district_projects(district_name: str, db: Session = Depends(get_db)):
    """Obtiene todos los proyectos de uno o más distritos."""
    district_list = get_district_list_from_param(district_name)
    
    projects = db.query(models.Project).options(joinedload(models.Project.districts)).join(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name.in_(district_list)
    ).distinct().order_by(models.Project.created_at.desc()).all()
    
    return projects

@router.get("/districts/{district_name}/stats", response_model=Dict[str, Any])
def get_district_stats(district_name: str, db: Session = Depends(get_db)):
    """Obtiene estadísticas de proyectos por distrito(s)."""
    district_list = get_district_list_from_param(district_name)
    
    projects = db.query(models.Project).join(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name.in_(district_list)
    ).distinct().all()
    
    total = len(projects)
    active = sum(1 for p in projects if p.status == 'active')
    inactive = sum(1 for p in projects if p.status == 'inactive')
    completed = sum(1 for p in projects if p.status == 'completed')
    archived = sum(1 for p in projects if p.status == 'archived')
    
    display_name = ', '.join(district_list)
    
    return {
        "district": display_name,
        "total": total,
        "active": active,
        "inactive": inactive,
        "completed": completed,
        "archived": archived
    }
