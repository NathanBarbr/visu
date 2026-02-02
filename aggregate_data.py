import shapefile
import json
import collections
import os

path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG/1_DONNEES_LIVRAISON_2023/RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"

def aggregate():
    print(f"Reading {path}...")
    sf = shapefile.Reader(path)
    
    print("Aggregating data into hierarchy...")
    
    # Structure: GroupCode -> { surface: 0, count: 0, cultures: { CultCode: { surface: 0, count: 0 } } }
    hierarchy = collections.defaultdict(lambda: {'surface': 0.0, 'count': 0, 'cultures': collections.defaultdict(lambda: {'surface': 0.0, 'count': 0})})
    
    # Iterate records
    for i, r in enumerate(sf.iterRecords()):
        if i % 100000 == 0:
            print(f"Processed {i} records...")
             
        try:
             # Index 1: SURF_PARC, Index 2: CODE_CULTU, Index 3: CODE_GROUP
             surf = r[1]
             code_cult = r[2]
             code_group = r[3]
             
             if surf is None: surf = 0
             if code_cult is None: code_cult = "UNKNOWN"
             if code_group is None: code_group = "UNKNOWN"
             
             surf = float(surf)
             
             # Update Group Stats
             hierarchy[code_group]['surface'] += surf
             hierarchy[code_group]['count'] += 1
             
             # Update Culture Stats within Group
             hierarchy[code_group]['cultures'][code_cult]['surface'] += surf
             hierarchy[code_group]['cultures'][code_cult]['count'] += 1
             
        except Exception as e:
            continue

    # Convert to D3 Hierarchy format
    # { name: "root", children: [ { name: group, size: ..., children: [ ... ] } ] }
    
    root_children = []
    
    for grp_code, grp_data in hierarchy.items():
        cult_children = []
        for cult_code, cult_data in grp_data['cultures'].items():
            cult_children.append({
                "name": cult_code,
                "value": cult_data['surface'],
                "count": cult_data['count']
            })
        
        # Sort cultures by surface
        cult_children.sort(key=lambda x: x['value'], reverse=True)
        
        root_children.append({
            "name": grp_code,
            "value": grp_data['surface'], # total surface for group
            "children": cult_children
        })
    
    # Sort groups by surface
    root_children.sort(key=lambda x: x['value'], reverse=True)
    
    output = {
        "name": "RPG_REGION",
        "children": root_children
    }
    
    out_path = 'data_hierarchy.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Hierarchical aggregation complete. Saved to {out_path}")

if __name__ == '__main__':
    aggregate()
