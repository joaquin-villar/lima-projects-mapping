# backend/routers/annotations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from typing import List

router = APIRouter(tags=["Annotations"])

@router.get("/{project_id}/annotations", response_model=List[schemas.AnnotationResponse])
def get_annotations(project_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las anotaciones de un proyecto."""
    return db.query(models.Annotation).filter(
        models.Annotation.project_id == project_id
    ).all()

@router.post("/{project_id}/annotations")
def add_annotation(project_id: int, annotation: schemas.AnnotationCreate, db: Session = Depends(get_db)):
    """Agrega una nueva anotación a un proyecto."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    db_annotation = models.Annotation(project_id=project_id, **annotation.dict())
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

@router.delete("/{project_id}/annotations/{annotation_id}")
def delete_annotation(project_id: int, annotation_id: int, db: Session = Depends(get_db)):
    """Elimina una anotación específica."""
    annotation = db.query(models.Annotation).filter(
        models.Annotation.id == annotation_id,
        models.Annotation.project_id == project_id
    ).first()

    if not annotation:
        raise HTTPException(404, "Annotation not found")

    db.delete(annotation)
    db.commit()
    return {"message": "Annotation deleted"}