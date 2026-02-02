import shapefile
import json
import random
from pyproj import Transformer

# Paths
input_shp = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG/1_DONNEES_LIVRAISON_2023/RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"
output_geojson = "parcels_sample.geojson"

SAMPLE_SIZE = 5000  # Number of parcels to show (limit to avoid crash)

def generate_map_data():
    print("Initializing...")
    sf = shapefile.Reader(input_shp)
    total_shapes = len(sf)
    print(f"Total shapes: {total_shapes}")
    
    # Indices to sample
    indices = random.sample(range(total_shapes), min(SAMPLE_SIZE, total_shapes))
    indices.sort() # optimize reading order
    
    # Coordinate Transformer: Lambert93 (2154) -> WGS84 (4326)
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    
    features = []
    
    print("Reading and transforming sample...")
    
    # Iterate with index to pick specific shapes
    # Shapefile random access can be slow, but let's try reading specific shapes using shape() method
    for idx in indices:
        try:
            shp = sf.shape(idx)
            rec = sf.record(idx)
            
            # Record fields: 
            # 0: ID_PARCEL, 1: SURF, 2: CODE_CULTU, 3: GROUP...
            
            culture = rec[2]
            surface = rec[1]
            if culture is None: culture = "?"
            
            # Geometry transformation
            # Shapefile parts logic: if simple polygon, just one part.
            # pyshp stores points as flat list of [x, y]
            
            # Simple conversion for single polygon (ignoring holes for simplicity if complex)
            # We'll just transform all points and reconstruct meaningful rings if possible,
            # or just take the outer ring.
            # Warning: Complex polygons with holes are tricky manually.
            # Let's assume most fields are simple polygons.
            
            raw_points = shp.points
            # Transform all points
            wgs_points = []
            for x, y in raw_points:
                lon, lat = transformer.transform(x, y)
                wgs_points.append([lon, lat])
            
            # Construct GeoJSON Polygon
            # GeoJSON Polygon needs [[[lon, lat], ...]] (list of rings)
            # pyshp shape.parts gives index of start of each part.
            
            parts = shp.parts 
            parts.append(len(raw_points)) # sentinel
            
            poly_coords = []
            for i in range(len(parts) - 1):
                start = parts[i]
                end = parts[i+1]
                ring = wgs_points[start:end]
                poly_coords.append(ring)
                
            feature = {
                "type": "Feature",
                "properties": {
                    "culture": culture,
                    "surface": float(surface) if surface else 0
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": poly_coords
                }
            }
            features.append(feature)
            
        except Exception as e:
            # print(f"Error processing shape {idx}: {e}")
            continue
            
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_geojson, "w") as f:
        json.dump(geojson, f)
        
    print(f"Done. Saved {len(features)} parcels to {output_geojson}")

if __name__ == '__main__':
    generate_map_data()
