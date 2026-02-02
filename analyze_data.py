import shapefile

path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG/1_DONNEES_LIVRAISON_2023/RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"

try:
    sf = shapefile.Reader(path)
    print("Fields:")
    # Fields are lists [name, type, length, decimal]
    for field in sf.fields:
        print(field)
    
    print("\nFirst record:")
    print(sf.record(0))
    
    print(f"\nNumber of shapes: {len(sf)}")

except Exception as e:
    print(f"Error reading shapefile: {e}")
