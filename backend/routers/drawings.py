# backend/routers/drawings.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from backend.database import get_db
from backend import models, schemas
from typing import List

router = APIRouter(prefix="/api/projects", tags=["Drawings"])

@router.get("/{project_id}/drawings", response_model=List[schemas.DrawingResponse])
def get_drawings(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Drawing).filter(models.Drawing.project_id == project_id).all()

@router.post("/{project_id}/drawings")
def add_drawing(project_id: int, drawing: schemas.DrawingCreate, db: Session = Depends(get_db)):
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
    return new_drawing

@router.delete("/{project_id}/drawings/{drawing_id}")
def delete_drawing(project_id: int, drawing_id: int, db: Session = Depends(get_db)):
    drawing = db.query(models.Drawing).filter(
        models.Drawing.id == drawing_id,
        models.Drawing.project_id == project_id
    ).first()

    if not drawing:
        raise HTTPException(404, "Drawing not found")

    db.delete(drawing)
    db.commit()
    return {"message": "Drawing deleted"}