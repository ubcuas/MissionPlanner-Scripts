import json

coords = [  # Your list of coordinates 
"38.3138848,-76.5499264",
"38.3180233,-76.5576053",
"38.3200772,-76.5527773",
"38.3195385,-76.5394735",
"38.3112889,-76.5240669",
"38.3035098,-76.5376282",
"38.3012197,-76.5467262",
"38.3050253,-76.5667677",
"38.2929007,-76.5730762",
"38.2917892,-76.5388727",
"38.3024995,-76.5376711",
]

waypoint_list = []
for i, coord in enumerate(coords):
    lat, lon = coord.split(",")
    waypoint = {
        "id": i,  # Assign an incrementing ID
        "name": "Alpha",
        "latitude": float(lat),
        "longitude": float(lon),
        "altitude": 100
    }
    waypoint_list.append(waypoint)

# print(waypoint_list)

print(json.dumps(waypoint_list, indent=4))