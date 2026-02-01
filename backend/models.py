# backend/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class UserRole(enum.Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    VERIFIED = "verified"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # from Neon Auth
    email = Column(String, unique=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")
    verified = Column(Boolean, default=False)
    verified_by = Column(String, ForeignKey('users.id'), nullable=True)
    created_by = Column(String, ForeignKey('users.id'), nullable=True)
    source_url = Column(String, nullable=True)
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    districts = relationship("ProjectDistrict", back_populates="project", cascade="all, delete-orphan")
    drawings = relationship("Drawing", back_populates="project", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="project", cascade="all, delete-orphan")
    edit_history = relationship("EditHistory", back_populates="project", cascade="all, delete-orphan")
    edit_suggestions = relationship("EditSuggestion", back_populates="project", cascade="all, delete-orphan")

class ProjectDistrict(Base):
    __tablename__ = "project_districts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    distrito_name = Column(String, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="districts")

    __table_args__ = (
        UniqueConstraint('project_id', 'distrito_name', name='_project_district_uc'),
    )

class Drawing(Base):
    __tablename__ = "drawings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    geojson = Column(Text, nullable=False)
    drawing_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="drawings")

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    distrito_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="annotations")

class EditHistory(Base):
    __tablename__ = "edit_history"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="CASCADE"))
    edited_by = Column(String, ForeignKey('users.id'))
    field_changed = Column(String)
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=None)  # None = pending
    
    project = relationship("Project", back_populates="edit_history")

class EditSuggestion(Base):
    """For handling conflicts and pending edits"""
    __tablename__ = "edit_suggestions"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete="CASCADE"))
    suggested_by = Column(String, ForeignKey('users.id'))
    changes = Column(JSON)  # Store proposed changes
    status = Column(String, default='pending')  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="edit_suggestions")
