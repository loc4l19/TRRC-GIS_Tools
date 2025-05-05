import os
import sys
import zipfile
import shutil
import geopandas as gpd
import pandas as pd
from glob import glob
from dbfread import DBF


# ---------- Extraction Function ----------
def extract_zip_files(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.zip'):
                file_path = os.path.join(root, file)
                print(f"📦 Extracting: {file_path}")
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    print(f'✅ Extracted: {file}')
                    # os.remove(file_path)
                    # print(f'🗑️ Deleted zip: {file}')
                except zipfile.BadZipFile:
                    print(f'❌ Bad zip file: {file_path} — not deleted')
    print('✅ Extraction phase complete.\n')


# ---------- Organization Function ----------
def organize_shapefiles_by_prefix_and_suffix(root_dir):
    prefix_mapping = {
        'air': 'Airports', 'cem': 'Cemeteries', 'cit': 'Cities', 'cty': 'Counties',
        'gov': 'Government_Lands', 'offs': 'OffshoreSurveys', 'pipe': 'Pipelines',
        'rail': 'Railroads', 'road': 'Roads', 'ship': 'ShipChannels',
        'subd': 'Subdivisions', 'surv': 'Surveys', 'watr': 'Water', 'well': 'Wells'
    }

    suffix_mapping = {
        'l': 'ln', 'p': 'poly', 'g': 'Cnty_poly_named', 'i': 'GulfAreas_poly',
        'k': 'Cnty_poly_unnamed', 'Labpt': 'Label_pts', 'Abspt': 'Abs_pts',
        'b': 'BayTrct_poly', 'a': 'area', 's': 'SHL_pts'
    }

    special_cases = {
        'well': {'s': 'SHLpts', 'b': 'BHLpts', 'l': 'PATHln'},
        'surv': {'l': 'Surv_ln', 'p': 'Surv_poly', 'b': 'BayTrct_poly',
                 'Abspt': 'Abs_pts', 'Labpt': 'Surv_Label_pts'},
        'subd': {'l': 'Subd_ln', 'Labpt': 'Subd_Label_pts'},
        'watr': {'l': 'Wtr_ln', 'a': 'Wtr_area'},
        'offs': {'a': 'OffSh_Surv_poly'}
    }

    shapefile_extensions = ['.shp', '.shx', '.dbf', '.prj', '.sbn', '.sbx', '.cpg', '.shp.xml']
    all_files = os.listdir(root_dir)
    base_names = set()

    for file in all_files:
        file_path = os.path.join(root_dir, file)
        if not os.path.isfile(file_path):
            continue
        if file.endswith('.shp.xml'):
            base = file[:-8]
        else:
            base, ext = os.path.splitext(file)
            if ext.lower() in shapefile_extensions:
                base_names.add(base)

    for base in base_names:
        prefix_match = ''.join(filter(str.isalpha, base[:6])).lower()
        prefix_folder = prefix_mapping.get(prefix_match)
        if not prefix_folder:
            print(f"⚠️ Skipping {base} — unknown prefix '{prefix_match}'")
            continue

        prefix_path = os.path.join(root_dir, prefix_folder)
        os.makedirs(prefix_path, exist_ok=True)

        if 'Labpt' in base:
            suffix = 'Labpt'
        elif 'Abspt' in base:
            suffix = 'Abspt'
        else:
            suffix = base[-1].lower()

        suffix_folder = None
        for key in special_cases:
            if prefix_match.startswith(key):
                suffix_folder = special_cases[key].get(suffix)
                break
        if not suffix_folder:
            suffix_folder = suffix_mapping.get(suffix)
        if not suffix_folder:
            print(f"⚠️ Could not determine suffix folder for: {base}")
            continue

        full_suffix_path = os.path.join(prefix_path, suffix_folder)
        os.makedirs(full_suffix_path, exist_ok=True)

        for ext in shapefile_extensions:
            file_name = base + ext
            file_path = os.path.join(root_dir, file_name)
            if os.path.exists(file_path):
                shutil.move(file_path, os.path.join(full_suffix_path, file_name))
                print(f"✅ Moved {file_name} -> {prefix_folder}/{suffix_folder}")
    print('✅ Organization phase complete.\n')


# --- Apply WellStatus Based on SymNum ---
def apply_well_status_to_shapefiles(root_dir):
    symnum_map = {
    2: "Permitted Location", 3: "Dry Hole", 4: "Oil Well", 5: "Gas Well", 6: "Oil/Gas Well",
    7: "Plugged Oil Well", 8: "Plugged Gas Well", 9: "Canceled Location", 10: "Plugged Oil/Gas Well",
    11: "Injection/Disposal Well", 12: "Core Test", 16: "Sulfur Core Test", 17: "Storage from Oil",
    18: "Storage from Gas", 19: "Shut-In Well (Oil)", 20: "Shut-In Well (Gas)",
    21: "Injection/Disposal from Oil", 22: "Injection/Disposal from Gas", 23: "Injection/Disposal from Oil/Gas",
    36: "Geothermal Well", 73: "Brine Mining Well", 74: "Water Supply Well",
    75: "Water Supply from Oil", 76: "Water Supply from Gas", 77: "Water Supply from Oil/Gas",
    78: "Observation Well", 79: "Observation from Oil", 80: "Observation from Gas",
    81: "Observation from Oil/Gas", 86: "Horizontal Well Surface Location",
    87: "Directional/Sidetrack Well Surface Location", 88: "Storage Well", 89: "Service Well",
    90: "Service from Oil", 91: "Service from Gas", 92: "Service from Oil/Gas",
    103: "Storage from Oil/Gas", 104: "Injection/Disposal from Storage",
    105: "Injection/Disposal from Storage/Oil", 106: "Injection/Disposal from Storage/Gas",
    107: "Injection/Disposal from Storage/Oil/Gas", 108: "Observation from Storage",
    109: "Observation from Storage/Oil", 110: "Observation from Storage/Gas",
    111: "Observation from Storage/Oil/Gas", 112: "Service from Storage",
    113: "Service from Storage/Oil", 114: "Service from Storage/Gas",
    115: "Service from Storage/Oil/Gas", 116: "Plugged Storage", 117: "Plugged Storage/Oil",
    118: "Plugged Storage/Gas", 119: "Plugged Storage/Oil/Gas", 121: "Brine Mining from Oil",
    122: "Brine Mining from Gas", 123: "Brine Mining from Oil/Gas",
    124: "Injection/Disposal from Brine Mining", 125: "Injection/Disposal from Brine Mining/Oil",
    126: "Injection/Disposal from Brine Mining/Gas",
    127: "Injection/Disposal from Brine Mining/Oil/Gas", 128: "Observation from Brine Mining",
    129: "Observation from Brine Mining/Oil", 130: "Observation from Brine Mining/Gas",
    131: "Observation from Brine Mining/Oil/Gas", 132: "Service from Brine Mining",
    133: "Service from Brine Mining/Oil", 134: "Service from Brine Mining/Gas",
    135: "Service from Brine Mining/Oil/Gas", 136: "Plugged Brine Mining",
    137: "Plugged Brine Mining/Oil", 138: "Plugged Brine Mining/Gas",
    139: "Plugged Brine Mining/Oil/Gas", 140: "Storage/Brine Mining",
    141: "Storage/Brine Mining/Oil", 142: "Storage/Brine Mining/Gas",
    143: "Storage/Brine Mining/Oil/Gas", 144: "Inj./Disposal from Storage/Brine Mining",
    145: "Inj./Disposal from Storage/Brine Mining/Oil",
    146: "Inj./Disposal from Storage/Brine Mining/Gas",
    147: "Inj./Disposal from Storage/Brine Mining/Oil/Gas",
    148: "Observation from Storage/Brine Mining",
    149: "Observation from Storage/Brine Mining/Oil",
    150: "Observation from Storage/Brine Mining/Gas",
    151: "Observation from Storage/Brine Mining/Oil/Gas",
    152: "Plugged Storage/Brine Mining", 153: "Plugged Storage/Brine Mining/Oil",
    154: "Plugged Storage/Brine Mining/Gas", 155: "Plugged Storage/Brine Mining/Oil/Gas"
}
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.lower().endswith(".shp") and file.lower().startswith("well"):
                shp_path = os.path.join(dirpath, file)
                try:
                    gdf = gpd.read_file(shp_path)

                    # Print all column names for debug
                    print(f"🔍 Columns in {file}: {list(gdf.columns)}")

                    # Find column matching 'SymNum' (case-insensitive)
                    sym_field = next((col for col in gdf.columns if col.strip().lower() == "symnum"), None)
                    if not sym_field:
                        print(f"⚠️ 'SymNum' not found in {file}, skipping.")
                        continue

                    gdf["Well_Status"] = gdf[sym_field].map(symnum_map)
                    gdf.to_file(shp_path, driver="ESRI Shapefile")
                    print(f"✅ Added 'Well_Status' to {file}")

                except Exception as e:
                    print(f"❌ Failed to process {file}: {e}")


# ---------- DBF Join Function ----------
def join_api_dbf_to_well_shapes(root_dir):
    # Gather all DBFs in the root directory
    root_dbfs = {os.path.splitext(f)[0]: os.path.join(root_dir, f)
                 for f in os.listdir(root_dir)
                 if f.lower().endswith('.dbf') and f.lower().startswith('api')}

    # Walk subfolders and process shapefiles
    for dirpath, _, filenames in os.walk(root_dir):
        for shp_file in filenames:
            if shp_file.lower().endswith('.shp') and shp_file.lower().startswith('well'):
                shp_path = os.path.join(dirpath, shp_file)
                api_digits = ''.join(filter(str.isdigit, shp_file))[:6]  # Adjust if needed

                dbf_key = f"api{api_digits}"
                dbf_path = root_dbfs.get(dbf_key)

                if not dbf_path:
                    print(f"❌ No matching DBF for {shp_file} (expected {dbf_key}.dbf in root)")
                    continue

                try:
                    # Load shapefile
                    gdf = gpd.read_file(shp_path)
                    # Load and prepare DBF
                    df_dbf = pd.DataFrame(iter(DBF(dbf_path, encoding='latin1')))
                    if 'APINUM' not in df_dbf.columns:
                        print(f"⚠️ 'APINUM' not found in {dbf_path}")
                        continue
                    if 'API' not in gdf.columns:
                        print(f"⚠️ 'API' not found in {shp_file}")
                        continue
                    df_dbf = df_dbf.rename(columns={'APINUM': 'API'})

                    # Join and overwrite
                    gdf_joined = gdf.merge(df_dbf, how='left', on='API')
                    gdf_joined.to_file(shp_path, driver='ESRI Shapefile')

                    print(f"🔗 Joined {os.path.basename(dbf_path)} → {shp_file}")
                except Exception as e:
                    print(f"❌ Error processing {shp_file}: {e}")
    print(f"\n✅ API DBF join phase complete." )


# ---------- Merge Function ----------
def merge_shapefiles_by_folder(x_directory):
    """
    Merges all shapefiles in each subdirectory into a single shapefile and 
       saves it in a 'MergedFiles' folder
    """
    for current_dir, _, _ in os.walk(x_directory):
        parent = os.path.basename(os.path.dirname(current_dir))
        last = os.path.basename(os.path.normpath(current_dir))
        combined = parent + "-" + last
        shapefiles = glob(os.path.join(current_dir, "*.shp"))

        if not shapefiles:
            continue

        gdf_list = []
        for shp in shapefiles:
            try:
                gdf = gpd.read_file(shp)
                gdf['source_file'] = os.path.basename(shp)
                gdf_list.append(gdf)
            except Exception as e:
                print(f"Error reading {shp}: {e}")

        if gdf_list:
            try:
                merged = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=gdf_list[0].crs)
                merged_dir = os.path.join(current_dir, "MergedFiles")
                os.makedirs(merged_dir, exist_ok=True)

                output_file = os.path.join(merged_dir, f"{combined}_Merge.shp")
                merged.to_file(output_file)
                print(f"✅ Merged {len(shapefiles)} shapefiles in {current_dir}")
            except Exception as e:
                print(f"❌ Error merging in {current_dir}: {e}")
    print('✅ Merge phase complete.\n')


def write_merged_shapefiles_to_gpkg(root_dir: str, output_gpkg: str):
    """
    Searches for 'MergedFiles' folders, merges all shapefiles inside, and
    writes each group to a unique layer in a GeoPackage.
    """
    merged_count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        if os.path.basename(dirpath).lower() == "mergedfiles":
            print(f"🔍 Found MergedFiles: {dirpath}")
            shapefiles = [f for f in os.listdir(dirpath) if f.lower().endswith(".shp")]

            if not shapefiles:
                print(f"⚠️  No shapefiles in {dirpath}")
                continue

            gdf_list = []
            for shp in shapefiles:
                full_path = os.path.join(dirpath, shp)
                try:
                    gdf = gpd.read_file(full_path)
                    gdf["source_file"] = shp
                    gdf_list.append(gdf)
                except Exception as e:
                    print(f"❌ Error reading {shp}: {e}")

            if gdf_list:
                try:
                    merged = pd.concat(gdf_list, ignore_index=True)
                    gdf_merged = gpd.GeoDataFrame(merged, geometry="geometry", crs=gdf_list[0].crs)

                    parts = os.path.relpath(dirpath, root_dir).split(os.sep)[:-1]  # Remove 'MergedFiles'
                    layer_name = "_".join(parts).replace("-", "_")

                    gdf_merged.to_file(output_gpkg, layer=layer_name, driver="GPKG")
                    print(f"✅ Saved: {layer_name} ({len(gdf_merged)} features)")
                    merged_count += 1
                except Exception as e:
                    print(f"❌ Failed to save layer from {dirpath}: {e}")

    print(f"\n🎉 Finished. {merged_count} layers written to {output_gpkg}\n")


# ---------- Single Main Entry Point ----------
if __name__ == "__main__":
 # ---- System Requirements ----
    print("\nScript Requirements")
    print("-------------------------------------")
    print(f"Python Version: 3.8 or higher (you are using: {sys.version.split()[0]})")
    print("Required pip packages:")
    print("pip install geopandas pandas dbfread\n\n")

    # ---- TRRC Download Instructions ----
    print("Required TRRC GIS Data Downloads")
    print("-------------------------------------")
    print("Shapefile Data (wells, roads, pipelines, etc.):")
    print("https://mft.rrc.texas.gov/link/f9112008-ab1f-4550-94c9-e2546d1bbb59\n")
    
    print("Well Attribute Data (used for API joins):")
    print("https://mft.rrc.texas.gov/link/1eb94d66-461d-4114-93f7-b4bc04a70674\n\n")

    print("The check boxs in the upper right hand corner of the pages will allow you to select all shapefiles at once.")
    print("Download buttons will appear in the lower right hand corner of the page.\n\n")
    print("Extract downloaded .zip files into the desired folder before running this script.\n\n")


    input_dir = input('📂 Enter the directory to extract and organize shapefiles: ').strip()
    ...

    if not os.path.isdir(input_dir):
        print(f"❌ Invalid directory: {input_dir}")
    else:
        # Extract zip files
        extract_zip_files(input_dir)
        
        # Organize shapefiles by prefix and suffix
        organize_shapefiles_by_prefix_and_suffix(input_dir)
        
        # Apply well status based on SymNum
        apply_well_status_to_shapefiles(input_dir)

        # Join API DBF files to well shapefiles
        print("🔗 Starting DBF joins...")
        join_api_dbf_to_well_shapes(input_dir)

        # Merge shapefiles by folder
        print("🧩 Starting shapefile merges...")
        merge_shapefiles_by_folder(input_dir)

        # Write to GeoPackage after merges
        print(f"📦 Writing merged layers to: {output_gpkg}")

        output_gpkg = os.path.join(input_dir, "TRRC_MergedLayers.gpkg")
        write_merged_shapefiles_to_gpkg(input_dir, output_gpkg)

        print('🎉 All operations completed successfully!')
