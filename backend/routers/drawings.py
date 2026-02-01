# backend/routers/drawings.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from backend.database import get_db
from backend import models, schemas
from backend.routers.auth import editor_permission
from typing import List

router = APIRouter(tags=["Drawings"])

@router.get("/{project_id}/drawings", response_model=List[schemas.DrawingResponse])
def get_drawings(project_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los dibujos de un proyecto."""
    return db.query(models.Drawing).filter(
        models.Drawing.project_id == project_id
    ).all()

@router.post("/{project_id}/drawings", dependencies=[Depends(editor_permission)])
def add_drawing(project_id: int, drawing: schemas.DrawingCreate, db: Session = Depends(get_db)):
    """Agrega un nuevo dibujo a un proyecto."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    new_drawing = models.Drawing(
        project_id=project_id,
        geojson=json.dumps(drawing.geojson),
        drawing_type=drawing.drawing_type
    )
    db.add(new_drawing)
    db.commit()
    db.refresh(new_drawing)
    return new_drawing

@router.post("/{project_id}/drawings/batch", dependencies=[Depends(editor_permission)])
def save_drawings_batch(project_id: int, batch: schemas.DrawingBatch, db: Session = Depends(get_db)):
    """Reemplaza todos los dibujos de un proyecto con un nuevo set (Batch)."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        # 1. Limpiar dibujos anteriores del proyecto
        db.query(models.Drawing).filter(models.Drawing.project_id == project_id).delete()

        # 2. Insertar los nuevos
        for drawing_data in batch.drawings:
            new_drawing = models.Drawing(
                project_id=project_id,
                geojson=json.dumps(drawing_data.geojson),
                drawing_type=drawing_data.drawing_type
            )
            db.add(new_drawing)

        db.commit()
        return {"message": f"Successfully saved {len(batch.drawings)} drawings"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving batch: {str(e)}")

@router.delete("/{project_id}/drawings/{drawing_id}", dependencies=[Depends(editor_permission)])
def delete_drawing(project_id: int, drawing_id: int, db: Session = Depends(get_db)):
    """Elimina un dibujo específico."""
    drawing = db.query(models.Drawing).filter(
        models.Drawing.id == drawing_id,
        models.Drawing.project_id == project_id
    ).first()

    if not drawing:
        raise HTTPException(404, "Drawing not found")

    db.delete(drawing)
    db.commit()
    return {"message": "Drawing deleted"}