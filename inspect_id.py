import json

with open("parcels_sample_france.geojson") as f:
    data = json.load(f)
    print(data['features'][0]['properties'])
