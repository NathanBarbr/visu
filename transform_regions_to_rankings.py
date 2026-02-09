
import json
from collections import defaultdict

def transform():
    try:
        with open('data_regions.json', 'r', encoding='utf-8') as f:
            regions_data = json.load(f)
    except FileNotFoundError:
        print("data_regions.json not found.")
        return

    # Structure: Culture -> List of {region, surface}
    rankings = defaultdict(list)

    for region, data in regions_data.items():
        if region == "Inconnu": continue
        
        # We only have top 5 cultures per region in data_regions.json
        # This is a limitation, but enough for major crops comparison
        for item in data.get('top_cultures', []):
            code = item['code']
            surface = item['surface']
            rankings[code].append({
                "region": region,
                "surface": surface
            })

    # Format output
    final_output = {}
    for code, regions_list in rankings.items():
        # Sort by surface desc
        regions_list.sort(key=lambda x: x['surface'], reverse=True)
        final_output[code] = regions_list

    # Save
    with open('data_rankings.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print(f"Generated rankings for {len(final_output)} cultures from existing regional data.")

if __name__ == '__main__':
    transform()
