import sqlite3
import json
import random
from pyproj import Transformer
from shapely.wkb import loads
from shapely.geometry import shape, mapping, Point, shape as Shape
import time

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"
regions_path = "regions.geojson"
output_file = "data_regions.json"

SAMPLE_SIZE = 200000  # Large sample for statistical significance per region

def generate_regional_data():
    print("Loading Regions...")
    with open(regions_path, 'r', encoding='utf-8') as f:
        regions_data = json.load(f)
    
    # Prepare Regions Polygons
    regions_polys = []
    for feat in regions_data['features']:
        name = feat['properties']['nom']
        poly = Shape(feat['geometry'])
        regions_polys.append((name, poly))
        
    print(f"Loaded {len(regions_polys)} regions.")

    print(f"Connecting to GPKG...")
    conn = sqlite3.connect(gpkg_path)
    c = conn.cursor()
    
    print(f"Sampling {SAMPLE_SIZE} parcels...")
    query = """
        SELECT code_cultu, surf_parc, the_geom
        FROM parcelles_graphiques
        ORDER BY RANDOM()
        LIMIT ?
    """
    c.execute(query, (SAMPLE_SIZE,))
    rows = c.fetchall()
    
    print("Processing & Aggregating...")
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    
    # Data structure: Region -> { TotalSurf: 0, Cultures: { Code: surf } }
    region_stats = {r[0]: {"total_surf": 0, "cultures": {}} for r in regions_polys}
    region_stats["Inconnu"] = {"total_surf": 0, "cultures": {}}
    
    hits = 0
    
    for i, r in enumerate(rows):
        if i % 10000 == 0: print(f"Processed {i}...")
        
        try:
            cult = r[0]
            surf = r[1]
            blob = r[2]
            
            # WKB Parsing (Skip Header)
            if blob[0:2] != b'GP': continue
            flags = blob[3]
            envelope_indicator = (flags >> 1) & 0x07
            envelope_size = 0
            if envelope_indicator == 1: envelope_size = 32
            elif envelope_indicator == 2: envelope_size = 48
            elif envelope_indicator == 3: envelope_size = 48
            elif envelope_indicator == 4: envelope_size = 64
            header_size = 8 + envelope_size
            
            wkb_bytes = blob[header_size:]
            geom = loads(wkb_bytes)
            
            # Get centroid in Lamb93 (faster than transforming polygon)
            centroid = geom.centroid
            # Transform centroid to WGS84 for GeoJSON matching
            lon, lat = transformer.transform(centroid.x, centroid.y)
            pt = Point(lon, lat)
            
            # Find Region
            found_region = "Inconnu"
            for name, poly in regions_polys:
                if poly.contains(pt):
                    found_region = name
                    break
            
            # Aggregation
            stats = region_stats[found_region]
            stats["total_surf"] += surf
            if cult not in stats["cultures"]:
                stats["cultures"][cult] = 0
            stats["cultures"][cult] += surf
            
            hits += 1
            
        except Exception:
            continue

    print(f"Finished processing. Hits: {hits}")
    
    # Finalize JSON
    # Convert cultures dict to sorted list
    final_output = {}
    for reg, data in region_stats.items():
        sorted_cults = sorted(
            [{"code": k, "surface": v} for k, v in data["cultures"].items()], 
            key=lambda x: x["surface"], 
            reverse=True
        )
        final_output[reg] = {
            "total_surface": data["total_surf"],
            "top_cultures": sorted_cults[:5] # Keep Top 5
        }
        
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {output_file}")
    conn.close()

if __name__ == '__main__':
    generate_regional_data()
