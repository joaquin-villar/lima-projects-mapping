from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    districts: List[str] = Field(min_length=1)  # must have ≥1 district

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    districts: List[str] = []  # returned as list of district names

    class Config:
        from_attributes = True


class DistrictCreate(BaseModel):
    distrito_name: str
    notes: Optional[str] = None

class DrawingCreate(BaseModel):
    geojson: dict
    drawing_type: str

class DrawingResponse(BaseModel):
    id: int
    geojson: str
    drawing_type: str
    created_at: datetime
    class Config:
        from_attributes = True

class AnnotationCreate(BaseModel):
    distrito_name: str
    title: str
    content: str

class AnnotationResponse(BaseModel):
    id: int
    distrito_name: str
    title: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True
