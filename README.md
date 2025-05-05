# TRRC GIS Shapefile Processing

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

## 📦 Software Requirements

- Python ≥ 3.8 (https://www.python.org/downloads/)  
- Required packages (install via pip): geopandas, pandas, dbfread

---

## 🗂 Required Data Downloads

Shapefile Data (All Layers by County):
https://mft.rrc.texas.gov/link/f9112008-ab1f-4550-94c9-e2546d1bbb59

Well Attribute Data (API join):
https://mft.rrc.texas.gov/link/1eb94d66-461d-4114-93f7-b4bc04a70674

✔ Use the checkbox in the top-left to select all shapefiles at once, then download using the "Download" button in the bottom-left.



## 🛠 How to Use

1. Extract the .zip files from TRRC into a directory of your choice.
2. Run the script:  python trrc_gis_pipeline.py
3. When prompted, enter the path to the directory where shapefiles were extracted.


The script will:
    
    A. Extract any remaining .zip files, then cleanup the extracted .zip files
    
    B. Organize the shapefiles into folders.
    
    C. Applies well status translation.
    
    D. Updates well attributes data from .dbf
    
    E. Creates merged shapefiles by folder
    
    F. Outputs a TRRC_MergedLayers.gpkg GeoPackage

## 🗂 Available TRRC Shapefile Types

The Texas Railroad Commission (TRRC) provides a wide range of GIS shapefiles related to oil and gas infrastructure, environmental boundaries, and regulatory data. These shapefiles are organized by file name prefixes that correspond to specific feature categories. This script automatically sorts and organizes them using the following classification:

| Prefix | Category           | Description                                                                 |
|--------|--------------------|-----------------------------------------------------------------------------|
| `air`  | Airports           | Public and private airstrip locations                                       |
| `cem`  | Cemeteries         | Cemetery boundaries and locations                                           |
| `cit`  | Cities             | Incorporated and unincorporated municipal boundaries                        |
| `cty`  | Counties           | County boundary polygons across Texas                                       |
| `gov`  | Government_Lands   | Lands owned or administered by state or federal agencies                    |
| `offs` | OffshoreSurveys    | Gulf of Mexico lease block boundaries and offshore survey data              |
| `pipe` | Pipelines          | Oil, gas, and product pipeline routes and systems                           |
| `rail` | Railroads          | Railroad corridors and right-of-way features                                |
| `road` | Roads              | Road networks including highways and local roads                            |
| `ship` | ShipChannels       | Navigation channels and shipping lanes, mostly near ports and coastal areas |
| `subd` | Subdivisions       | Subdivision boundaries and label points                                     |
| `surv` | Surveys            | Land surveys, abstracts, and survey block boundaries                        |
| `watr` | Water              | Water bodies such as lakes, rivers, and bay tracts                          |
| `well` | Wells              | Well surface and bottom hole locations, paths and starightline paths        |

Each prefix may appear in multiple shapefiles with different geometry types — such as points, lines, or polygons. This script further classifies files by suffixes like:

- `l` = Line features (e.g., roads, paths)
- `p` = Polygon features (e.g., survey boundaries)
- `Labpt`, `Abspt` = Label or abstract points
- `s`, `b` = SHL (surface) or BHL (bottom hole) well points

Example shapefile filename:  
`wellsl.shp` → Wells, line geometry (well paths)  
`survLabpt.shp` → Surveys, label point geometry

The script recognizes these patterns and sorts files accordingly into subfolders to make the dataset more navigable and ready for GIS analysis.

---
## ⚠️ Note on Well Attributes

TRRC well shapefiles do not include detailed well information such as operator, field name, permit number, or completion date.

These attributes are stored in separate .dbf files, which must be joined using the API or APINUM field. This script automates that join process, enriching well shapefiles with key metadata from the API-based .dbf files.

## 📁 What is the `1-SourceData` Folder?

During processing, this script creates a folder named `1-SourceData` inside your input directory. It serves as a holding area for:

- All original `.zip` files after successful extraction
- All `.dbf` files used during API joins

This helps maintain a clean workspace by separating source data from processed shapefiles and merged outputs. You can use this folder for:
- Archiving downloaded TRRC files
- Verifying original inputs used in your workflow
- Sharing source material separately from GIS-ready layers

