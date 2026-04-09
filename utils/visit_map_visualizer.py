import json
import numpy as np
import matplotlib.pyplot as plt

with open("data/visit_map/visit_map.json") as f:
    visit_map = json.load(f)

coords = []
values = []

for key, value in visit_map.items():
    x, y = map(int, key.split("_"))
    coords.append((x, y))
    values.append(value)

xs = [c[0] for c in coords]
ys = [c[1] for c in coords]

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

grid = np.zeros((max_y-min_y+1, max_x-min_x+1))

for (x, y), v in zip(coords, values):
    grid[y-min_y][x-min_x] = v

plt.imshow(grid, cmap="hot", origin="lower")
plt.colorbar(label="Visit Count")
plt.title("HAWK Exploration Map")
plt.xlabel("X")
plt.ylabel("Y")

plt.show()