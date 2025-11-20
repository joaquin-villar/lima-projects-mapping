# backend/routers/district_map.py
from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/api", tags=["District Map"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "geojson", "lima_callao_distritos.geojson")

@router.get("/districts-geojson")
def get_districts_geojson():
    if not os.path.exists(GEOJSON_PATH):
        raise HTTPException(404, "GeoJSON file not found")

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
