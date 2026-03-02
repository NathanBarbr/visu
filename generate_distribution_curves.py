"""
Generate fine-grained parcel size distribution data per region.
Uses spatial join (point-in-polygon) with regions.geojson to correctly
assign each parcel to its region based on its centroid coordinates.
"""
import json
import math
from collections import defaultdict

# Fine-grained bins (in hectares) - logarithmic-ish spacing
BIN_EDGES = [0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0,
             6.0, 8.0, 10.0, 15.0, 20.0, 30.0, 50.0, 100.0]


def point_in_polygon(px, py, polygon):
    """Ray casting algorithm to check if point is inside polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_multipolygon(px, py, multipolygon_coords):
    """Check if point is in a MultiPolygon geometry."""
    for polygon in multipolygon_coords:
        # polygon[0] is the outer ring
        if point_in_polygon(px, py, polygon[0]):
            return True
    return False


def get_centroid(geometry):
    """Get approximate centroid of a geometry."""
    gtype = geometry["type"]
    coords = geometry["coordinates"]

    if gtype == "Polygon":
        ring = coords[0]
    elif gtype == "MultiPolygon":
        # Use the largest polygon
        largest = max(coords, key=lambda p: len(p[0]))
        ring = largest[0]
    else:
        return None, None

    cx = sum(p[0] for p in ring) / len(ring)
    cy = sum(p[1] for p in ring) / len(ring)
    return cx, cy


def main():
    print("Loading regions GeoJSON...")
    with open("regions.geojson", encoding="utf-8") as f:
        regions_geo = json.load(f)

    # Build region lookup structures
    regions = []
    for feat in regions_geo["features"]:
        name = feat["properties"]["nom"]
        geom = feat["geometry"]
        # Pre-compute bounding box for fast rejection
        all_coords = []
        if geom["type"] == "Polygon":
            all_coords = geom["coordinates"][0]
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                all_coords.extend(poly[0])

        if all_coords:
            xs = [c[0] for c in all_coords]
            ys = [c[1] for c in all_coords]
            bbox = (min(xs), min(ys), max(xs), max(ys))
        else:
            bbox = None

        regions.append({
            "name": name,
            "geometry": geom,
            "bbox": bbox
        })

    print(f"Loaded {len(regions)} regions")

    # Load parcels
    print("Loading parcels...")
    input_file = "parcels_sample_france.geojson"
    try:
        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        input_file = "parcels_sample_france_5000.geojson"
        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)

    features = data["features"]
    print(f"Loaded {len(features)} parcels from {input_file}")

    # Assign each parcel to a region via spatial join
    region_surfaces = defaultdict(list)
    unmatched = 0

    for idx, feat in enumerate(features):
        if idx % 5000 == 0:
            print(f"  Processing parcel {idx}/{len(features)}...")

        surface = feat["properties"].get("surface", 0)
        cx, cy = get_centroid(feat["geometry"])
        if cx is None:
            unmatched += 1
            continue

        assigned = False
        for reg in regions:
            # Quick bbox check
            if reg["bbox"]:
                bx0, by0, bx1, by1 = reg["bbox"]
                if cx < bx0 or cx > bx1 or cy < by0 or cy > by1:
                    continue

            geom = reg["geometry"]
            if geom["type"] == "Polygon":
                if point_in_polygon(cx, cy, geom["coordinates"][0]):
                    region_surfaces[reg["name"]].append(surface)
                    assigned = True
                    break
            elif geom["type"] == "MultiPolygon":
                if point_in_multipolygon(cx, cy, geom["coordinates"]):
                    region_surfaces[reg["name"]].append(surface)
                    assigned = True
                    break

        if not assigned:
            unmatched += 1

    print(f"\nUnmatched parcels: {unmatched}")
    print(f"Regions found: {len(region_surfaces)}")
    for r, surfs in sorted(region_surfaces.items(), key=lambda x: -len(x[1])):
        print(f"  {r}: {len(surfs)} parcels, avg={sum(surfs)/len(surfs):.2f} ha, "
              f"median={sorted(surfs)[len(surfs)//2]:.2f} ha")

    # Build histogram per region
    result = {
        "bins": [],
        "regions": {}
    }

    # Bin labels
    for i in range(len(BIN_EDGES) - 1):
        mid = (BIN_EDGES[i] + BIN_EDGES[i+1]) / 2
        result["bins"].append({
            "min": BIN_EDGES[i],
            "max": BIN_EDGES[i+1],
            "mid": round(mid, 2),
            "label": f"{BIN_EDGES[i]}-{BIN_EDGES[i+1]} ha"
        })

    # Compute histogram percentages per region
    for region, surfaces in sorted(region_surfaces.items()):
        if len(surfaces) < 50:
            continue

        total = len(surfaces)
        counts = [0] * (len(BIN_EDGES) - 1)

        for s in surfaces:
            for i in range(len(BIN_EDGES) - 1):
                if BIN_EDGES[i] <= s < BIN_EDGES[i+1]:
                    counts[i] += 1
                    break
            else:
                counts[-1] += 1

        percentages = [round(c / total * 100, 2) for c in counts]

        result["regions"][region] = {
            "total_parcels": total,
            "avg_size": round(sum(surfaces) / total, 2),
            "median_size": round(sorted(surfaces)[total // 2], 2),
            "percentages": percentages
        }

    # Save
    output_file = "data_distribution_curves.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_file}")
    print(f"Bins: {len(result['bins'])}, Regions: {len(result['regions'])}")


if __name__ == "__main__":
    main()
