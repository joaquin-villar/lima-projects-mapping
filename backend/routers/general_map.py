# backend/routers/general_map.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from typing import List
from urllib.parse import unquote

router = APIRouter(prefix="/api", tags=["General Map & Districts"])

@router.get("/general/status")
def general_status():
    """
    Basic test endpoint to confirm the general map router works.
    """
    return {"message": "General map router is active"}


# ============================================================
# DISTRICT-SPECIFIC ROUTES
# ============================================================

@router.get("/districts/{district_name}/projects", response_model=List[schemas.ProjectResponse])
def get_district_projects(district_name: str, db: Session = Depends(get_db)):
    """
    Get all projects for a specific district.
    URL: /api/districts/{district_name}/projects
    """
    decoded_name = unquote(district_name)
    
    print(f"📍 Fetching projects for district: {decoded_name}")
    
    # Query projects through the many-to-many relationship
    project_districts = db.query(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name == decoded_name
    ).all()
    
    project_ids = [pd.project_id for pd in project_districts]
    
    projects = db.query(models.Project).filter(
        models.Project.id.in_(project_ids)
    ).order_by(models.Project.created_at.desc()).all()
    
    print(f"✅ Found {len(projects)} projects for {decoded_name}")
    
    # Format response
    result = []
    for project in projects:
        districts = [d.distrito_name for d in project.districts]
        result.append(schemas.ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            districts=districts
        ))
    
    return result


@router.get("/districts/{district_name}/stats")
def get_district_stats(district_name: str, db: Session = Depends(get_db)):
    """
    Get statistics for a specific district.
    URL: /api/districts/{district_name}/stats
    """
    decoded_name = unquote(district_name)
    
    print(f"📊 Fetching stats for district: {decoded_name}")
    
    # Get all projects for this district
    project_districts = db.query(models.ProjectDistrict).filter(
        models.ProjectDistrict.distrito_name == decoded_name
    ).all()
    
    project_ids = [pd.project_id for pd in project_districts]
    
    projects = db.query(models.Project).filter(
        models.Project.id.in_(project_ids)
    ).all()
    
    # Calculate statistics
    total = len(projects)
    active = sum(1 for p in projects if p.status == 'active')
    completed = sum(1 for p in projects if p.status == 'completed')
    archived = sum(1 for p in projects if p.status == 'archived')
    
    stats = {
        "district": decoded_name,
        "total": total,
        "active": active,
        "completed": completed,
        "archived": archived
    }
    
    print(f"✅ Stats for {decoded_name}:", stats)
    
    return stats