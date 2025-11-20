# backend/routers/district_map.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import os

router = APIRouter(prefix="/api", tags=["District Map"])

# We define the path from the project root using pathlib for robustness
BASE_DIR = Path(__file__).resolve().parent.parent.parent
GEOJSON_PATH = BASE_DIR / "data" / "geojson" / "lima_callao_distritos.geojson"

@router.get("/districts-geojson")
def get_districts_geojson():
    """Serves the static GeoJSON file containing all district boundaries."""
    # Use Pathlib's exists() method
    if not GEOJSON_PATH.exists():
        raise HTTPException(404, "GeoJSON file not found")

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)