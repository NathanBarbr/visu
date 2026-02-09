"""
Generate regional ranking data for each culture
Creates data showing which regions produce the most of each culture
"""
import shapefile
import json
from collections import defaultdict

# Department to Region mapping
DEPT_TO_REGION = {
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France", 
    "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
    "94": "Île-de-France", "95": "Île-de-France",
    "45": "Centre-Val de Loire", "28": "Centre-Val de Loire", "41": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "36": "Centre-Val de Loire", "18": "Centre-Val de Loire",
    "21": "Bourgogne-Franche-Comté", "58": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
    "89": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté", "39": "Bourgogne-Franche-Comté",
    "70": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",
    "14": "Normandie", "50": "Normandie", "61": "Normandie", "27": "Normandie", "76": "Normandie",
    "59": "Hauts-de-France", "62": "Hauts-de-France", "80": "Hauts-de-France",
    "60": "Hauts-de-France", "02": "Hauts-de-France",
    "54": "Grand Est", "55": "Grand Est", "57": "Grand Est", "88": "Grand Est",
    "67": "Grand Est", "68": "Grand Est", "51": "Grand Est", "52": "Grand Est",
    "08": "Grand Est", "10": "Grand Est",
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire",
    "72": "Pays de la Loire", "85": "Pays de la Loire",
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
    "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
    "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
    "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
    "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
    "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie", "82": "Occitanie",
    "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
    "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
    "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
    "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",
    "04": "Provence-Alpes-Côte d'Azur", "05": "Provence-Alpes-Côte d'Azur",
    "06": "Provence-Alpes-Côte d'Azur", "13": "Provence-Alpes-Côte d'Azur",
    "83": "Provence-Alpes-Côte d'Azur", "84": "Provence-Alpes-Côte d'Azur",
    "2A": "Corse", "2B": "Corse"
}

def generate_regional_culture_ranking():
    shapefile_path = "PARCELLES_GRAPHIQUES"
    
    print("Loading shapefile...")
    sf = shapefile.Reader(shapefile_path, encoding='utf-8')
    
    # Get field indices
    fields = [f[0] for f in sf.fields[1:]]
    surf_idx = fields.index('SURF_PARC')
    code_idx = fields.index('CODE_CULTU')
    dept_idx = fields.index('CODE_DEPT')
    
    # Structure: {culture_code: {region: {surface: X, count: Y}}}
    culture_by_region = defaultdict(lambda: defaultdict(lambda: {"surface": 0.0, "count": 0}))
    
    print("Processing records...")
    total = len(sf)
    for i, rec in enumerate(sf.iterRecords()):
        if i % 500000 == 0:
            print(f"  Progress: {i}/{total} ({100*i/total:.1f}%)")
        
        try:
            surface = float(rec[surf_idx]) if rec[surf_idx] else 0
            code = str(rec[code_idx]).strip()
            dept = str(rec[dept_idx]).strip().zfill(2)
            
            region = DEPT_TO_REGION.get(dept, "Autre")
            if region == "Autre" or not code:
                continue
                
            culture_by_region[code][region]["surface"] += surface
            culture_by_region[code][region]["count"] += 1
            
        except Exception as e:
            continue
    
    print("Building rankings...")
    
    # Build final structure with rankings
    result = {
        "cultures": {},
        "regions": list(set(DEPT_TO_REGION.values()))
    }
    
    for culture_code, regions_data in culture_by_region.items():
        # Sort regions by surface for this culture
        rankings = []
        for region, data in regions_data.items():
            rankings.append({
                "region": region,
                "surface": round(data["surface"], 2),
                "count": data["count"]
            })
        
        # Sort by surface descending
        rankings.sort(key=lambda x: x["surface"], reverse=True)
        
        # Only keep cultures with significant data
        total_surface = sum(r["surface"] for r in rankings)
        if total_surface > 100:  # At least 100 hectares total
            result["cultures"][culture_code] = {
                "total_surface": round(total_surface, 2),
                "total_count": sum(r["count"] for r in rankings),
                "rankings": rankings
            }
    
    # Save to JSON
    output_path = "data_culture_rankings.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_path}")
    print(f"Total cultures: {len(result['cultures'])}")

if __name__ == "__main__":
    generate_regional_culture_ranking()
