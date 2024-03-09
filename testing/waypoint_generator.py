import random

start = "\t{\n"
base = """\t\t"id": 0,
\t\t"name": "string",
\t\t"latitude": {:},
\t\t"longitude": {:},
\t\t"altitude": {:}
"""
end = """\t},\n"""

def to_string(lat, lng, alt):
    return start + base.format(lat, lng, alt) + end

centerlat = 38.3267098
centerlng = -76.6528130
alt = 100

wplist = []
for i in range(0, 300):
    wplist.append((centerlat + random.random() * 0.02 - 0.01, centerlng + random.random() * 0.02 - 0.01, alt))

with open("generated.txt", "w") as f:
    f.write("[\n")

    for tup in wplist:
        f.write(to_string(tup[0], tup[1], tup[2]))

    f.write("]\n")
