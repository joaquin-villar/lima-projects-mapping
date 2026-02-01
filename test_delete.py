
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
import sys

def test_delete(project_id):
    db = SessionLocal()
    try:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            print(f"Project {project_id} not found")
            return
        
        print(f"Attempting to delete project: {project.name} (ID: {project.id})")
        db.delete(project)
        db.commit()
        print("Success: Project deleted")
    except Exception as e:
        db.rollback()
        print(f"FAILURE: {type(e).__name__}: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_delete(int(sys.argv[1]))
    else:
        # Try to find a project to test with
        db = SessionLocal()
        p = db.query(models.Project).first()
        db.close()
        if p:
            test_delete(p.id)
        else:
            print("No projects to delete")
