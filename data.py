import json
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import random

"""
Dans ce script nous récupérons la liste des coordonnées de tous les arrêts
"""

with open('projet recherche/model_build_inputs/route_data.json', 'r') as f:
    data = json.load(f)

# listeCoor contriendra toutes les coordonées
listeCoor = []
element = []
for way in data.items():
    for stop in data[way[0]].items():
        element.append([stop])

for it in range(5, len(element), 6):
    a, b = element[it][0]
    for el in b:
        lat, lng = b[el]["lat"], b[el]["lng"]
        listeCoor.append([lat, lng])

"""
Trie et affiche pour une ville donnee les différents cluster
"""
def printClVille(latmin, latmax, lngmin, lngmax, listeCoor, labelName):
    cl = []
    for coor in listeCoor:
        if latmin <= coor[0] <= latmax and lngmin <= coor[1] <= lngmax:
            cl.append(coor)

    # print(len(cl))
    random.shuffle(cl)
    X2 = np.array(cl[0:1000])
    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    kmeans = KMeans(n_clusters=8, random_state=4, n_init="auto").fit(X2)
    cluster = kmeans.labels_

    for i in range(len(X2)):
        plt.scatter(X2[i, 0], X2[i, 1], c=color[cluster[i]])

    plt.title(labelName)
    plt.show()


# Ville Verte :

printClVille(32, 35, -125, -110, listeCoor, "Green city")

# Ville Bleu clair :

printClVille(45, 48, -130, -110, listeCoor, "Cyan city")

# Ville Bleu :

printClVille(29, 32, -100, -90, listeCoor, "Blue city")

# Ville Violet :

printClVille(40, 45, -100, -80, listeCoor, "Violet city")

# Ville Rouge :

printClVille(40, 45, -79, -60, listeCoor, "Red city")

# On va print une parties pour voir ce que ça donne, on devrait recuperer les 5 villes

random.shuffle(listeCoor)
X = np.array(listeCoor[0:100])
color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
kmeans = KMeans(n_clusters=5, random_state=4, n_init="auto").fit(X)
cluster = kmeans.labels_

for i in range(len(X)):
    plt.scatter(X[i, 0], X[i, 1], c=color[cluster[i]])

plt.title("5 differents cities")
plt.show()
