# backend/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    districts: List[str] = Field(min_length=1)

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    verified: bool
    verified_by: Optional[str]
    created_by: Optional[str]
    source_url: Optional[str]
    scraped_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    districts: List[str] = []

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