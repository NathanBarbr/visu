import shapefile
import collections

path = r"c:/Users/natha/PycharmProjects/visu/projet/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG_2-2__SHP_LAMB93_R84_2023-01-01/RPG/1_DONNEES_LIVRAISON_2023/RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"

def analyze():
    print("Reading shapefile...")
    sf = shapefile.Reader(path)
    
    cnt_d1 = 0
    cnt_d2 = 0
    total = 0
    
    # Bucketize parcel sizes for histogram
    # Ranges: <1ha, 1-5ha, 5-10ha, 10-20ha, >20ha
    size_ranges = {
        "< 1 ha": 0,
        "1 - 5 ha": 0,
        "5 - 10 ha": 0,
        "10 - 20 ha": 0,
        "> 20 ha": 0
    }
    
    # Check ID structure for geography
    # Usually XXX-YYY... or something. Let's just grab the first few chars of distinct IDs to see potential grouping.
    prefixes = collections.defaultdict(int)
    
    for i, r in enumerate(sf.iterRecords()):
        total += 1
        if i % 100000 == 0: print(f"Processed {i}...")
        
        # r[1] = SURF, r[4] = D1, r[5] = D2, r[0] = ID_PARCEL
        surf = r[1]
        d1 = r[4]
        d2 = r[5]
        id_parc = r[0]
        
        if d1 and d1.strip(): cnt_d1 += 1
        if d2 and d2.strip(): cnt_d2 += 1
        
        if surf is not None:
            s = float(surf)
            if s < 1: size_ranges["< 1 ha"] += 1
            elif s < 5: size_ranges["1 - 5 ha"] += 1
            elif s < 10: size_ranges["5 - 10 ha"] += 1
            elif s < 20: size_ranges["10 - 20 ha"] += 1
            else: size_ranges["> 20 ha"] += 1

        # Check Geography from ID (Department?)
        # ID Format varies, often starts with Dept code if standard RPG
        if id_parc:
            # Try to grab first 2 chars
            prefix = id_parc[:2]
            prefixes[prefix] += 1

    print("-" * 30)
    print(f"Total Parcels: {total}")
    print(f"With Culture D1: {cnt_d1} ({cnt_d1/total*100:.2f}%)")
    print(f"With Culture D2: {cnt_d2} ({cnt_d2/total*100:.2f}%)")
    print("-" * 30)
    print("Parcel Size Distribution:")
    for k, v in size_ranges.items():
        print(f"  {k}: {v}")
    print("-" * 30)
    print("ID Prefixes (Potential Departments?):")
    # Print top 10
    sorted_pref = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10]
    for k, v in sorted_pref:
        print(f"  {k}: {v}")

if __name__ == '__main__':
    analyze()
