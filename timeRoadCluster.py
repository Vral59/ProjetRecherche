import json
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

"""
Dans ce fichier nous créons la matrice d'adjacance des temps entres chaque stop d'une route
"""

road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"

with open('firstRoad.json', 'r') as f:
    data = json.load(f)

with open('projet recherche/model_build_inputs/route_data.json', 'r') as f:
    zoneRoad = json.load(f)


def creationDataFrame(data,zoneRoad):
    # Liste des noms des stop
    name = list(list(data[road].values())[0])
    # Liste des latitudes de chaques point
    listelat = [stop['lat'] for stop in zoneRoad[road]['stops'].values()]

    # Liste des longitude de chaque point
    listelng = [stop['lng'] for stop in zoneRoad[road]['stops'].values()]

    # Liste des différentes zone_id de chaque point
    zoneList = [zone['zone_id'] for zone in zoneRoad[road]['stops'].values()]

    # Liste de boolean pour savoir si on a une station
    stationList = [station['type'] == "Station" for station in zoneRoad[road]['stops'].values()]

    df = pd.DataFrame(columns=name, index=name)

    for el in name:
        row = data[road][el]
        df.loc[el] = pd.Series(row)

    # Rajout des colonenes
    df["zone_id"] = zoneList
    df["isStation"] = stationList
    df["lat"] = listelat
    df["lng"] = listelng

    # On récupère les prefixes des zone_id
    cluster = [el.split(".")[0] if str(el) != 'nan' else float("NaN") for el in zoneList]
    df["cluster"] = cluster


    """
    Quelque print pour tester le code
    """
    # On affiche la station
    # print(df.loc[df["isStation"] == True])

    # On suppprime la ligne avec la station
    # dfres = df[df["isStation"] == False]
    # dfres = dfres.loc[dfres["cluster"] == "P-12"]
    # print(dfres)
    # print(df.head())
    return name, df

name, df = creationDataFrame(data, zoneRoad)
uniqueCluster = list(set(df["cluster"].tolist()))
"""
Affichage des points par zone
"""

# Le cluster c'est les zone_id
color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
for el in name:
    if not df.loc[el, "isStation"]:
        lat = df.loc[el, "lat"]
        lng = df.loc[el, "lng"]
        idx = uniqueCluster.index(df.loc[el, "cluster"])
        plt.scatter(lat, lng, c=color[idx])

plt.title("Position point livraison cluster sont les prefixe")
plt.show()

# Affichage avec Kmeans en clustering

# Par exemple 5 cluster : 4 pour égaler les zones ID et 1 pour le point de départ
kmeans = KMeans(n_clusters=len(uniqueCluster), random_state=20, n_init="auto").fit(df[name])
newCluster = kmeans.labels_
#print(newCluster)
#print(len(newCluster))
color = ['b', 'g', 'r', 'c', 'y']
cpt = 0
for el in name:
    if not df.loc[el, "isStation"]:
        lat = df.loc[el, "lat"]
        lng = df.loc[el, "lng"]
        plt.scatter(lat, lng, c=color[newCluster[cpt]])
    cpt += 1

df["cluster Kmeans"] = newCluster
plt.title("Position point livraison les cluster sont kmeans")
plt.show()

# Pour la station on va trouver le point le plus proche

station = df.loc[df["isStation"] == True]

"""
Récupératition du premier point après le départ de la station (point le plus proche)
"""
def findFirstPoint(station, points):
    minTime = sys.maxsize
    minName = ""
    for n in points:
        time = station.loc[station.index[0], n]
        if time < minTime and time != 0:
            minTime = time
            minName = n

    return minName


"""
Récupération du dernier point (point le plus proche de la station qui est dans un cluster différent
"""
def findLastPoint(station, points, firstPoint, df):
    df = df[df["isStation"] == False]
    minTime = sys.maxsize
    minName = ""
    clFirstPoint = df.loc[firstPoint, "cluster Kmeans"]
    for n in points:
        if n != station.index[0]:
            time = df.loc[n, station.index[0]]
            if time < minTime and time != 0 and df.loc[n, "cluster Kmeans"] != clFirstPoint:
                minTime = time
                minName = n

    return minName


firstPoint = findFirstPoint(station, name)
lastPoint = findLastPoint(station, name, firstPoint, df)

"""
Affichage des résultats
"""
print("-------------------------------")
print("Premier point après départ de la station ", firstPoint)
print("Dernier point avant le retour à la station ", lastPoint)
print("Temps entre station -> premier point", df.loc[firstPoint, station.index[0]])
print("Temps entre dernier point -> Station ", df.loc[lastPoint, station.index[0]])
print("Vérification des cluster")
print("Cluster du premier point", df.loc[firstPoint, "cluster Kmeans"])
print("Cluster du denrier point", df.loc[lastPoint, "cluster Kmeans"])

