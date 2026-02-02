import sqlite3
import json
import random
from pyproj import Transformer
from shapely.wkb import loads
from shapely.geometry import shape, mapping

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"
output_geojson = "parcels_sample_france.geojson"

SAMPLE_SIZE = 50000

def generate_map_data_france():
    print(f"Connecting to {gpkg_path}...")
    conn = sqlite3.connect(gpkg_path)
    # Check max ID to sample efficiently
    c = conn.cursor()
    c.execute("SELECT MAX(rowid) from parcelles_graphiques")
    max_id = c.fetchone()[0]
    print(f"Max RowID: {max_id}")
    
    # Generate random Sample IDs
    indices = sorted(random.sample(range(1, max_id + 1), SAMPLE_SIZE * 2)) # Fetch more to account for holes/errors
    
    print(f"Sampling {SAMPLE_SIZE} parcels...")
    
    # We need to fetch geometries.
    # GPKG stores geom as BLOB in 'the_geom' usually with GPKG header.
    # We can use ST_AsText or similar if SpatiaLite loaded, but standard sqlite3 doesn't have it.
    # Alternatively, parse WKB manually.
    
    # Select rows
    placeholders = ",".join("?" for _ in indices)
    # Too many params? 
    # Let's iterate or use `IN` logic with smaller chunks if needed.
    # Or just select random rows using ORDER BY RANDOM() LIMIT N
    # ORDER BY RANDOM() is slow on large tables but for 9M rows might take 10-20s. Acceptable.
    
    query = """
        SELECT code_cultu, surf_parc, the_geom, id_parcel
        FROM parcelles_graphiques
        ORDER BY RANDOM()
        LIMIT ?
    """
    
    c.execute(query, (SAMPLE_SIZE,))
    rows = c.fetchall()
    
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    
    features = []
    
    for r in rows:
        try:
            cult = r[0]
            surf = r[1]
            blob = r[2]
            id_u = r[3] # id_parcel
            
            # GPKG Geometry Header parsing
            # Debug: Check magic
            magic = blob[0:2]
            if magic != b'GP':
                # print("Invalid Magic")
                continue
                
            flags = blob[3]
            envelope_indicator = (flags >> 1) & 0x07
            envelope_size = 0
            if envelope_indicator == 1: envelope_size = 32
            elif envelope_indicator == 2: envelope_size = 48
            elif envelope_indicator == 3: envelope_size = 48
            elif envelope_indicator == 4: envelope_size = 64
            
            header_size = 8 + envelope_size
            
            wkb_bytes = blob[header_size:]
            
            try:
                geom = loads(wkb_bytes)
            except Exception as wkb_err:
                 print(f"WKB Load Error: {wkb_err}")
                 continue
            
            # Reproject
            new_geom = None
            
            if geom.geom_type == 'Polygon':
                rings = []
                ext = list(geom.exterior.coords)
                new_ext = [transformer.transform(x, y) for x, y in ext]
                rings.append(new_ext)
                for i in geom.interiors:
                    inte = list(i.coords)
                    new_int = [transformer.transform(x, y) for x, y in inte]
                    rings.append(new_int)
                new_geom = {"type": "Polygon", "coordinates": rings}
                
            elif geom.geom_type == 'MultiPolygon':
                 # Use first polygon for simplicity in visualization or all
                 # Converting MultiPolygon to GeoJSON MultiPolygon
                 polys = []
                 for poly in geom.geoms:
                    rings = []
                    ext = list(poly.exterior.coords)
                    new_ext = [transformer.transform(x, y) for x, y in ext]
                    rings.append(new_ext)
                    # Interiors...
                    polys.append(rings)
                 new_geom = {"type": "MultiPolygon", "coordinates": polys}

            if new_geom:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "culture": cult,
                        "surface": float(surf) if surf else 0,
                        "id": id_u
                    },
                    "geometry": new_geom
                }
                features.append(feature)
            
        except Exception as e:
            print(f"Global Error: {e}")
            continue

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_geojson, "w") as f:
        json.dump(geojson, f)
        
    print(f"Done. Saved {len(features)} parcels to {output_geojson}")
    conn.close()

if __name__ == '__main__':
    generate_map_data_france()
