from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend import models, schemas
from backend.routers.auth import editor_permission
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
    projects = db.query(models.Project).options(
        joinedload(models.Project.districts),
        joinedload(models.Project.drawings)
    ).all()
    
    return projects

# -------------------------------------------------------------
# CREATE PROJECT
# -------------------------------------------------------------

@router.post("", response_model=schemas.ProjectResponse, dependencies=[Depends(editor_permission)])
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
    
    return new_project

# -------------------------------------------------------------
# GET SINGLE PROJECT
# -------------------------------------------------------------

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtiene un proyecto por ID."""
    project = db.query(models.Project).options(
        joinedload(models.Project.districts),
        joinedload(models.Project.drawings)
    ).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    return project

# -------------------------------------------------------------
# UPDATE PROJECT
# -------------------------------------------------------------

@router.put("/{project_id}", response_model=schemas.ProjectResponse, dependencies=[Depends(editor_permission)])
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
    
    return db_project

# -------------------------------------------------------------
# DELETE PROJECT
# -------------------------------------------------------------

@router.delete("/{project_id}", dependencies=[Depends(editor_permission)])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Elimina un proyecto y todas sus dependencias de forma robusta."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        # 1. Pruning manual (Garantiza borrado incluso si falla el cascade de SQLAlchemy)
        db.query(models.ProjectDistrict).filter(models.ProjectDistrict.project_id == project_id).delete()
        db.query(models.Drawing).filter(models.Drawing.project_id == project_id).delete()
        db.query(models.Annotation).filter(models.Annotation.project_id == project_id).delete()
        db.query(models.EditHistory).filter(models.EditHistory.project_id == project_id).delete()
        db.query(models.EditSuggestion).filter(models.EditSuggestion.project_id == project_id).delete()

        # 2. Borrar proyecto padre
        db.delete(project)
        db.commit()
        return {"message": f"Project {project_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"ERROR deleting project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error during deletion: {str(e)}"
        )
