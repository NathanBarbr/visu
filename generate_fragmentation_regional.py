import shapefile
import json
from collections import defaultdict

# Path to shapefile - adjust if needed
input_shp = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG/1_DONNEES_LIVRAISON_2023/RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"
output_json = "data_fragmentation_regional.json"

# Size categories (in hectares)
SIZE_CATEGORIES = [
    ("micro", 0, 0.5),        # < 0.5 ha
    ("petite", 0.5, 2),       # 0.5 - 2 ha
    ("moyenne", 2, 10),       # 2 - 10 ha
    ("grande", 10, 50),       # 10 - 50 ha
    ("tres_grande", 50, float('inf'))  # > 50 ha
]

# Region mapping (department code -> region name)
DEPT_TO_REGION = {
    # Île-de-France
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France", 
    "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
    "94": "Île-de-France", "95": "Île-de-France",
    # Centre-Val de Loire
    "18": "Centre-Val de Loire", "28": "Centre-Val de Loire", "36": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",
    # Bourgogne-Franche-Comté
    "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté", "39": "Bourgogne-Franche-Comté",
    "58": "Bourgogne-Franche-Comté", "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
    "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",
    # Normandie
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    # Hauts-de-France
    "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France",
    "62": "Hauts-de-France", "80": "Hauts-de-France",
    # Grand Est
    "08": "Grand Est", "10": "Grand Est", "51": "Grand Est", "52": "Grand Est",
    "54": "Grand Est", "55": "Grand Est", "57": "Grand Est", "67": "Grand Est", "68": "Grand Est", "88": "Grand Est",
    # Pays de la Loire
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire",
    "72": "Pays de la Loire", "85": "Pays de la Loire",
    # Bretagne
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    # Nouvelle-Aquitaine
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
    "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
    "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
    "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    # Occitanie
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
    "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
    "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie", "82": "Occitanie",
    # Auvergne-Rhône-Alpes
    "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
    "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
    "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
    "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",
    # Provence-Alpes-Côte d'Azur
    "04": "Provence-Alpes-Côte d'Azur", "05": "Provence-Alpes-Côte d'Azur",
    "06": "Provence-Alpes-Côte d'Azur", "13": "Provence-Alpes-Côte d'Azur",
    "83": "Provence-Alpes-Côte d'Azur", "84": "Provence-Alpes-Côte d'Azur",
    # Corse
    "2A": "Corse", "2B": "Corse",
}

def get_size_category(surface_ha):
    """Return the category name for a given surface in hectares."""
    for name, min_val, max_val in SIZE_CATEGORIES:
        if min_val <= surface_ha < max_val:
            return name
    return "tres_grande"

def generate_fragmentation_data():
    print("Loading shapefile...")
    sf = shapefile.Reader(input_shp)
    total = len(sf)
    print(f"Total records: {total}")
    
    # Structure: {region: {category: {"count": 0, "surface": 0}}}
    regional_data = defaultdict(lambda: {cat[0]: {"count": 0, "surface": 0} for cat in SIZE_CATEGORIES})
    
    print("Processing records...")
    for i, rec in enumerate(sf.iterRecords()):
        if i % 500000 == 0:
            print(f"  {i}/{total} ({100*i/total:.1f}%)")
        
        try:
            # Record fields: 0: ID_PARCEL, 1: SURF, 2: CODE_CULTU, 3: GROUP...
            id_parcel = rec[0] if rec[0] else ""
            surface = float(rec[1]) if rec[1] else 0
            
            # Extract department code from ID_PARCEL (format: DEPT-XXX-XXXX)
            dept_code = id_parcel[:2] if len(id_parcel) >= 2 else ""
            
            # Handle Corsica (2A, 2B)
            if len(id_parcel) >= 2 and id_parcel[:2] in ["2A", "2B"]:
                dept_code = id_parcel[:2]
            elif len(id_parcel) >= 2 and id_parcel[0] == "0":
                dept_code = id_parcel[:2]
            
            # Get region
            region = DEPT_TO_REGION.get(dept_code, "Autre")
            
            # Get size category
            category = get_size_category(surface)
            
            # Aggregate
            regional_data[region][category]["count"] += 1
            regional_data[region][category]["surface"] += surface
            
        except Exception as e:
            continue
    
    # Convert to regular dict and calculate percentages
    result = {}
    for region, categories in regional_data.items():
        total_count = sum(c["count"] for c in categories.values())
        total_surface = sum(c["surface"] for c in categories.values())
        
        if total_count == 0:
            continue
            
        avg_size = total_surface / total_count if total_count > 0 else 0
        
        result[region] = {
            "total_count": total_count,
            "total_surface": round(total_surface, 2),
            "avg_size": round(avg_size, 2),
            "categories": {}
        }
        
        for cat_name, data in categories.items():
            pct_count = (data["count"] / total_count * 100) if total_count > 0 else 0
            pct_surface = (data["surface"] / total_surface * 100) if total_surface > 0 else 0
            result[region]["categories"][cat_name] = {
                "count": data["count"],
                "surface": round(data["surface"], 2),
                "pct_count": round(pct_count, 1),
                "pct_surface": round(pct_surface, 1)
            }
    
    # Sort by average size (descending)
    result = dict(sorted(result.items(), key=lambda x: x[1]["avg_size"], reverse=True))
    
    # Save
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone! Saved to {output_json}")
    print(f"Regions processed: {len(result)}")
    
    # Preview
    print("\nPreview (avg parcel size):")
    for region, data in list(result.items())[:5]:
        print(f"  {region}: {data['avg_size']:.2f} ha")

if __name__ == "__main__":
    generate_fragmentation_data()
