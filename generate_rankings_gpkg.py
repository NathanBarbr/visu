import sqlite3
import json
from pyproj import Transformer
from shapely.wkb import loads
from shapely.geometry import shape as Shape, Point

# Configuration
gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"
regions_path = "regions.geojson"
output_file = "data_rankings.json"
SAMPLE_SIZE = 1000000  # 1 million parcels for better accuracy

def generate_rankings():
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
    try:
        conn = sqlite3.connect(gpkg_path)
        c = conn.cursor()
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return

    print(f"Sampling {SAMPLE_SIZE} parcels...")
    query = """
        SELECT code_cultu, surf_parc, the_geom
        FROM parcelles_graphiques
        ORDER BY RANDOM()
        LIMIT ?
    """
    try:
        c.execute(query, (SAMPLE_SIZE,))
        rows = c.fetchall()
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
        return
    
    print("Processing & Aggregating...")
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    
    # Structure: Culture -> { Region: Surface }
    culture_stats = {}
    
    hits = 0
    total = len(rows)
    
    for i, r in enumerate(rows):
        if i % 50000 == 0: print(f"Processed {i}/{total} ({int(i/total*100)}%)...")
        
        try:
            cult = r[0]
            surf = r[1]
            blob = r[2]
            
            if not cult or not surf: continue

            # WKB Parsing (GPKG specific header handling)
            if blob[0:2] != b'GP': continue
            # Skip header logic (simplified from generate_regional_data.py)
            # Usually header is fixed size or standard, assuming standard layout from previous working script
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
            
            # Get centroid
            centroid = geom.centroid
            lon, lat = transformer.transform(centroid.x, centroid.y)
            pt = Point(lon, lat)
            
            # Find Region
            found_region = "Autre"
            for name, poly in regions_polys:
                if poly.contains(pt):
                    found_region = name
                    break
            
            if found_region == "Autre": continue

            # Aggregate
            if cult not in culture_stats:
                culture_stats[cult] = {}
            
            if found_region not in culture_stats[cult]:
                culture_stats[cult][found_region] = 0.0
            
            culture_stats[cult][found_region] += surf
            
            hits += 1
            
        except Exception:
            continue

    print(f"Finished processing. Hits: {hits}")
    conn.close()

    # Format output: Culture -> List of {region, surface, rank}
    print("Formatting rankings...")
    final_output = {}
    
    for cult, regions_data in culture_stats.items():
        # Convert dict to list
        ranking = []
        for region, surface in regions_data.items():
            ranking.append({
                "region": region,
                "surface": round(surface, 2)
            })
        
        # Sort by surface desc
        ranking.sort(key=lambda x: x["surface"], reverse=True)
        
        # Keep only cultures with enough data (e.g., > 3 regions or > 10ha total in sample)
        total_surface = sum(r["surface"] for r in ranking)
        if total_surface > 10: 
            final_output[cult] = ranking

    print(f"Saving {len(final_output)} cultures to {output_file}...")
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print("Done.")

if __name__ == '__main__':
    generate_rankings()
