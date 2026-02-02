import sqlite3
import json
import os

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"

def aggregate_france():
    print(f"Connecting to {gpkg_path}...")
    conn = sqlite3.connect(gpkg_path)
    c = conn.cursor()
    
    table = "parcelles_graphiques"
    
    # Check coords columns
    print("Checking columns...")
    c.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in c.fetchall()]
    print(f"Columns: {cols}")
    
    # Identify surface and culture columns
    # Usually: surface_parcelle or surf_parc, code_cultu
    col_surf = next((x for x in cols if 'surf' in x.lower()), None)
    col_cult = next((x for x in cols if 'code_cult' in x.lower()), None)
    
    if not col_surf or not col_cult:
        print("ERROR: Could not identify Surface or Culture columns.")
        return

    print(f"Using columns: Surface='{col_surf}', Culture='{col_cult}'")
    
    print("Aggregating data via SQL (this might take a few seconds)...")
    # Query: Code, Sum(Surface), Count(*)
    query = f"""
        SELECT {col_cult}, SUM({col_surf}), COUNT(*)
        FROM {table}
        GROUP BY {col_cult}
    """
    
    c.execute(query)
    results = c.fetchall()
    
    print(f"Aggregation done. Found {len(results)} distinct cultures.")
    
    # Python Mappings for Groups (same as before)
    # Define groups
    CULTURE_GROUPS = {
        "1": ["BTH", "BTP"], "2": ["MIS", "MID"], "3": ["ORH", "ORP"],
        "4": ["AVH", "AVP", "TTH", "SGH", "SEH", "CGO"], # etc... simplified
        "5": ["CZH", "CZP"], "6": ["TRN"], "18": ["PPH"], "19": ["PTR"]
    }
    # Reverse mapping
    CODE_TO_GROUP = {}
    for grp, codes in CULTURE_GROUPS.items():
        for code in codes:
            CODE_TO_GROUP[code] = grp
            
    # Process results into JSON
    culture_summary = []
    group_summary_map = {}
    
    for row in results:
        code = row[0]
        surf = row[1]
        count = row[2]
        
        if not code: continue
        if not surf: surf = 0
         
        # By Culture
        culture_summary.append({
            "code": code,
            "surface": surf,
            "count": count
        })
        
        # By Group (Simple heuristic if map missing: First digit? No, aggregater logic needed)
        # Using basic reverse mapping or fallback
        # Let's try to infer group from previous logic or just lump remaining into '28' (Divers)
        grp = CODE_TO_GROUP.get(code, "28") 
        # Actually RPG usually has 'CODE_GROUP' column too. Let's check columns again in runtime.
        # If CODE_GROUP exists, use it.
        
    # Check if 'CODE_GROUP' exists
    col_group = next((x for x in cols if 'code_group' in x.lower()), None)
    
    if col_group:
        print(f"Found Group column: {col_group}. Re-aggregating by group...")
        query_grp = f"""
            SELECT {col_group}, SUM({col_surf}), COUNT(*)
            FROM {table}
            GROUP BY {col_group}
        """
        c.execute(query_grp)
        res_grp = c.fetchall()
        group_summary = []
        for r in res_grp:
            if r[0]:
                group_summary.append({"code": r[0], "surface": r[1], "count": r[2]})
    else:
        # manual agg
        print("Manual grouping aggregation...")
        # ... (simplified)
        group_summary = [] 
        
    # Hierarchy Query
    print("Generating Hierarchy Data...")
    query_hier = f"""
        SELECT {col_group}, {col_cult}, SUM({col_surf}), COUNT(*)
        FROM {table}
        GROUP BY {col_group}, {col_cult}
    """
    c.execute(query_hier)
    res_hier = c.fetchall()
    
    # Build tree
    # root -> group -> culture
    tree = {"name": "RPG_FRANCE", "children": []}
    groups = {} # code -> {name: code, children: []}
    
    for row in res_hier:
        grp_code = row[0]
        cult_code = row[1]
        surf = row[2]
        count = row[3]
        
        if not grp_code: grp_code = "UNKNOWN"
        if not surf: surf = 0
        
        if grp_code not in groups:
            groups[grp_code] = {"name": grp_code, "children": [], "value": 0}
            
        groups[grp_code]["children"].append({
            "name": cult_code,
            "value": surf,
            "count": count
        })
        groups[grp_code]["value"] += surf
        
    tree["children"] = list(groups.values())
    
    with open('data_hierarchy_france.json', 'w') as f:
        json.dump(tree, f)
        
    print("Saved to data_hierarchy_france.json")
    
    # Save to data_summary_france.json
    final_data = {
        "culture": sorted(culture_summary, key=lambda x: x['surface'], reverse=True),
        "group": sorted(group_summary, key=lambda x: x['surface'], reverse=True)
    }
    
    with open('data_summary_france.json', 'w') as f:
        json.dump(final_data, f)
        
    conn.close()
    print("Saved to data_summary_france.json")

if __name__ == '__main__':
    aggregate_france()
