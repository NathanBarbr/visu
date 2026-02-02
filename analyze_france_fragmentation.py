import sqlite3

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"

def analyze_fragmentation_france():
    print(f"Connecting to {gpkg_path}...")
    conn = sqlite3.connect(gpkg_path)
    c = conn.cursor()
    
    table = "parcelles_graphiques"
    col_surf = "surf_parc"
    
    print("Computing parcel size distribution buckets (SQL)...")
    
    # Buckets: <1, 1-5, 5-10, 10-20, >20
    query = f"""
        SELECT 
            CASE 
                WHEN {col_surf} < 1 THEN '< 1 ha'
                WHEN {col_surf} >= 1 AND {col_surf} < 5 THEN '1 - 5 ha'
                WHEN {col_surf} >= 5 AND {col_surf} < 10 THEN '5 - 10 ha'
                WHEN {col_surf} >= 10 AND {col_surf} < 20 THEN '10 - 20 ha'
                ELSE '> 20 ha'
            END as bucket,
            COUNT(*)
        FROM {table}
        GROUP BY bucket
    """
    
    c.execute(query)
    results = c.fetchall()
    
    total = sum(r[1] for r in results)
    
    print(f"Total Parcels (France): {total}")
    distribution = {}
    for r in results:
        distribution[r[0]] = r[1]
        
    # Expected order for output
    order = ['< 1 ha', '1 - 5 ha', '5 - 10 ha', '10 - 20 ha', '> 20 ha']
    
    data_js = []
    
    for label in order:
        count = distribution.get(label, 0)
        percent = round((count / total) * 100)
        print(f"  {label}: {count} ({percent}%)")
        
        data_js.append({
            "label": label,
            "count": count,
            "percent": percent
        })
        
    conn.close()
    
    print("\nUse these values to update fragmentation.js")

if __name__ == '__main__':
    analyze_fragmentation_france()
