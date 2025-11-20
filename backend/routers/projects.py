from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from datetime import datetime
from typing import List

router = APIRouter(tags=["Projects"])

# -------------------------------------------------------------
# LIST ALL PROJECTS
# -------------------------------------------------------------

@router.get("", response_model=List[schemas.ProjectResponse])  # Remove the "/"
def get_all_projects(db: Session = Depends(get_db)):
    """Obtiene todos los proyectos."""
    projects = db.query(models.Project).all()
    
    # 🔧 FIX: Build response list properly
    result = []
    for p in projects:
        response = schemas.ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            districts=[pd.distrito_name for pd in p.districts]  # Extract district names
        )
        result.append(response)
    
    return result

# -------------------------------------------------------------
# CREATE PROJECT
# -------------------------------------------------------------

@router.post("", response_model=schemas.ProjectResponse)  # Remove the "/"
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
    
    # Build response manually
    response = schemas.ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        status=new_project.status,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
        districts=project.districts
    )
    return response

# -------------------------------------------------------------
# GET SINGLE PROJECT
# -------------------------------------------------------------

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtiene un proyecto por ID."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    # 🔧 FIX: Build response manually
    response = schemas.ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        districts=[pd.distrito_name for pd in project.districts]
    )
    return response

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
    
    # 🔧 FIX: Build response manually
    response = schemas.ProjectResponse(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at,
        districts=project.districts
    )
    return response

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