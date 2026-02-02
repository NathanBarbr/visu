import json

def analyze_sizes():
    with open('data_summary.json', 'r') as f:
        data = json.load(f)
    
    cultures = data['culture']
    
    # Calculate avg size
    stats = []
    for c in cultures:
        avg = c['surface'] / c['count'] if c['count'] > 0 else 0
        stats.append({
            'code': c['code'],
            'avg': avg,
            'total_surf': c['surface'],
            'count': c['count']
        })
    
    # Sort by Avg Size
    stats.sort(key=lambda x: x['avg'], reverse=True)
    
    print("Largest Average Parcels:")
    for s in stats[:10]:
        print(f"  {s['code']}: {s['avg']:.2f} ha (Total: {s['total_surf']:.0f} ha, N={s['count']})")
        
    print("\nSmallest Average Parcels (with N>100):")
    stats_filtered = [s for s in stats if s['count'] > 100]
    stats_filtered.sort(key=lambda x: x['avg'])
    for s in stats_filtered[:10]:
        print(f"  {s['code']}: {s['avg']:.2f} ha (Total: {s['total_surf']:.0f} ha, N={s['count']})")

if __name__ == '__main__':
    analyze_sizes()
