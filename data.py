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

listeCoor = [[stop['lat'], stop['lng']] for stop in
             [list(data['RouteID_15baae2d-bf07-4967-956a-173d4036613f']['stops'].values())[0] ]]

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
    # On prend 1000 ou moins points
    m = min(10000, len(cl))
    X2 = np.array(cl[0:m])
    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    kmeans = KMeans(n_clusters=5, random_state=4, n_init="auto").fit(X2)
    cluster = kmeans.labels_

    for i in range(len(X2)):
        plt.scatter(X2[i, 0], X2[i, 1], c=color[cluster[i]])

    plt.title(labelName)
    plt.show()


# Je me suis planté les couleurs des villes ont changé donc c'est pas totalement vrai comme nom

# Los angeles :

printClVille(32, 35, -125, -110, listeCoor, "Los Angeles")

# Austin :

printClVille(45, 48, -130, -110, listeCoor, "Austin")

# Seatle :

printClVille(29, 32, -100, -90, listeCoor, "Seatle")

# Chicago :

printClVille(40, 45, -100, -80, listeCoor, "Chicago")

# Boston :

printClVille(40, 45, -79, -60, listeCoor, "Boston")

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
