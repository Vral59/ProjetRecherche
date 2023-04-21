import json
import numpy as np
from sklearn.cluster import KMeans
import random
import matplotlib.pyplot as plt

# Ouverture du fichier JSON
with open(r'../projet recherche/model_build_inputs/route_data.json') as f:
    data = json.load(f)

# Extract latitude and longitude of stops
coords = [[stop['lat'], stop['lng']] for stop in data['RouteID_15baae2d-bf07-4967-956a-173d4036613f']['stops'].values()]

# Shuffle data
random.shuffle(coords)

# Perform clustering on the first 7 stops
kmeans = KMeans(n_clusters=5, random_state=0).fit(coords[:70])

# Print cluster centers
print(kmeans.cluster_centers_)

# Plot the clusters on a graph
plt.scatter([coord[0] for coord in coords[:70]], [coord[1] for coord in coords[:70]], c=kmeans.labels_)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], marker='x', s=200, linewidths=3, color='r')
plt.show()