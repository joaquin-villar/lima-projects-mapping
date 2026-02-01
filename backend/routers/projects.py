from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend import models, schemas
from datetime import datetime
from typing import List

router = APIRouter(tags=["Projects"])

# -------------------------------------------------------------
# LIST ALL PROJECTS
# -------------------------------------------------------------

@router.get("", response_model=List[schemas.ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    """Obtiene todos los proyectos."""
    # Use joinedload to fetch districts in a single query
    projects = db.query(models.Project).options(joinedload(models.Project.districts)).all()
    
    # Transform districts to list of strings for pydantic
    for p in projects:
        p.districts = [d.distrito_name for d in p.districts]
        
    return projects

# -------------------------------------------------------------
# CREATE PROJECT
# -------------------------------------------------------------

@router.post("", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Crea un nuevo proyecto y sus asociaciones de distrito."""
    new_project = models.Project(
        name=project.name,
        description=project.description,
        status=project.status
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Add districts
    for distrito in project.districts:
        db.add(models.ProjectDistrict(project_id=new_project.id, distrito_name=distrito))

    db.commit()
    db.refresh(new_project)
    
    # Prepare list for response
    new_project.districts = project.districts
    return new_project

# -------------------------------------------------------------
# GET SINGLE PROJECT
# -------------------------------------------------------------

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtiene un proyecto por ID."""
    project = db.query(models.Project).options(joinedload(models.Project.districts)).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Transform districts to list of strings
    project.districts = [d.distrito_name for d in project.districts]
    return project

# -------------------------------------------------------------
# UPDATE PROJECT
# -------------------------------------------------------------

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Actualiza un proyecto y sus distritos asociados."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(404, "Project not found")

    db_project.name = project.name
    db_project.description = project.description
    db_project.status = project.status
    db_project.updated_at = datetime.utcnow()

    # Delete old districts
    db.query(models.ProjectDistrict).filter(
        models.ProjectDistrict.project_id == project_id
    ).delete()

    # Add new districts
    for distrito in project.districts:
        db.add(models.ProjectDistrict(project_id=project_id, distrito_name=distrito))

    db.commit()
    db.refresh(db_project)
    
    # Prepare list for response
    db_project.districts = project.districts
    return db_project

# -------------------------------------------------------------
# DELETE PROJECT
# -------------------------------------------------------------

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Elimina un proyecto y todas sus dependencias."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}
