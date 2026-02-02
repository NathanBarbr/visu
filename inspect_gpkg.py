import sqlite3

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"

def inspect_gpkg():
    print(f"Connecting to {gpkg_path}...")
    conn = sqlite3.connect(gpkg_path)
    c = conn.cursor()
    
    # List tables
    print("Tables:")
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    for t in tables:
        print(f" - {t[0]}")
        
    # Pick the likely table (PARCELLES_GRAPHIQUES)
    target_table = "PARCELLES_GRAPHIQUES"
    if (target_table,) in tables:
        print(f"\nColumns in {target_table}:")
        c.execute(f"PRAGMA table_info({target_table})")
        cols = c.fetchall()
        for col in cols:
            print(f"  {col[1]} ({col[2]})")
            
        # Count rows
        print("\nCounting rows...")
        c.execute(f"SELECT Count(*) FROM {target_table}")
        count = c.fetchone()[0]
        print(f"Total rows: {count}")
        
    conn.close()

if __name__ == '__main__':
    inspect_gpkg()
