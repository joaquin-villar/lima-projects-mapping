from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/projects", tags=["Projects"])

# -------------------------------------------------------------
# Funciones CRUD principales
# -------------------------------------------------------------

@router.get("/", response_model=List[schemas.ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    # Nota: Renombrada a get_all_projects para evitar confusión con get_project
    return db.query(models.Project).all()

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # 1. Crear el proyecto base (sin distritos)
    new_project = models.Project(
        name=project.name, 
        description=project.description, 
        status=project.status
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # 2. 🟢 AÑADIR DISTRITOS A LA TABLA DE ASOCIACIÓN
    for distrito in project.districts:
        db.add(models.ProjectDistrict(project_id=new_project.id, distrito_name=distrito))

    db.commit()
    db.refresh(new_project)
    return new_project

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(404, "Project not found")

    # 1. Actualizar campos principales
    db_project.name = project.name
    db_project.description = project.description
    db_project.status = project.status
    db_project.updated_at = datetime.utcnow()

    # 2. 🟢 ELIMINAR VIEJOS DISTRITOS y RE-AÑADIR NUEVOS
    db.query(models.ProjectDistrict).filter(models.ProjectDistrict.project_id == project_id).delete()

    for distrito in project.districts:
        db.add(models.ProjectDistrict(project_id=project_id, distrito_name=distrito))

    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    # ... (Se mantiene igual, no necesita tocar distritos directamente)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    # SQLAlchemy manejará la eliminación en cascada de ProjectDistrict si está configurado en models.py,
    # pero para mayor seguridad, la lógica de eliminación de distritos debería ir aquí.
    db.query(models.ProjectDistrict).filter(models.ProjectDistrict.project_id == project_id).delete()
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}