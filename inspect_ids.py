import sqlite3

gpkg_path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01.7z/RPG_2-0__GPKG_LAMB93_FXX_2022-01-01/RPG/1_DONNEES_LIVRAISON_2023-08-01/RPG_2-0_GPKG_LAMB93_FXX-2022/PARCELLES_GRAPHIQUES.gpkg"

def inspect():
    try:
        conn = sqlite3.connect(gpkg_path)
        c = conn.cursor()
        c.execute("SELECT id_parcel FROM parcelles_graphiques LIMIT 10")
        rows = c.fetchall()
        for r in rows:
            print(r)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
