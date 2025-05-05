# TRRC GIS Shapefile Processing Pipeline

This Python script automates the extraction, organization, enhancement, merging, and conversion of shapefiles downloaded from the Texas Railroad Commission (TRRC) into a consolidated GeoPackage (`.gpkg`) for Oil & Gas professionals.

---

## 🔍 Features

- **Unzips TRRC shapefile archives** in nested folders
- **Organizes shapefiles** by category (Wells, Roads, Pipelines, etc.) and geometry type (points, lines, polygons)
- **Adds `WELLSTAT` descriptions** using the `SymNum` field in well shapefiles
- **Joins well attribute `.dbf` tables** (by API number) to corresponding well shapefiles
- **Merges shapefiles** by category into unified layers
- **Exports layers to a GeoPackage** with one layer per category

---

## 📦 Requirements

- Python ≥ 3.8  
- Required packages (install via pip):

```bash
pip install geopandas pandas dbfread
