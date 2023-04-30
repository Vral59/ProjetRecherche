import json
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from math import *

"""
Dans ce fichier nous allons lire les données et créer les dataframe
"""

"""
Ouvre les json en question

:param
pathToTimeRoad : Temps entre chaque arrêt des routes ex: 'firstRoad.json'
pathToRoad : Routes utilisé par le conducteur ex: 'projet recherche/model_build_inputs/route_data.json'
pathToPackage : Chemin vers le fichier contenenant les informations des colis ex: package_data.json

:return
data : Dictionnaire d'informations contenue dans pathToTimeRoad
zoneRoad : Dictionnaire d'informations contenue dans pathToRoad
package : Dictionnaire des informations contenue dans pathToPackage
"""


def openFile(pathToTimeRoad, pathToRoad, pathToPackage):
    with open(pathToTimeRoad, 'r') as f:
        data = json.load(f)

    with open(pathToRoad, 'r') as f:
        zoneRoad = json.load(f)

    with open(pathToPackage, 'r') as f:
        package = json.load(f)

    return data, zoneRoad, package


"""
Algorithme d'équilibrage des kmeans, crée des cluster équilibré

:param
X : le dataset, un tableau numpy
k : le nombre de cluster que l'on veut 
max_iter : le nombre d'itération pour l'équilibrage

:return 
label : liste des cluster 
"""


def balancedKmeans(X, k, max_iters=150):
    # calcule les cluster initiaux des kmeans++
    kmeans = KMeans(n_clusters=k, n_init=10, init='k-means++')
    kmeans.fit(X)
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    num_points = X.shape[0]
    num_dims = X.shape[1]

    # Créer la taille du cluster que l'on veut
    cluster_sizes = np.ones(k) * (num_points // k)

    for it in range(max_iters):
        # Assigner chaque point à son cluster le plus proche
        distances = np.zeros((num_points, k))
        for i in range(num_points):
            for j in range(k):
                distances[i, j] = np.linalg.norm(X[i, :] - centers[j, :])
        new_labels = np.argmin(distances, axis=1)

        # Réassigner les points à chaque cluster pour équilibrer
        for i in range(num_points):
            old_label = labels[i]
            new_label = new_labels[i]
            if cluster_sizes[new_label] < num_points // k:
                labels[i] = new_label
                cluster_sizes[old_label] -= 1
                cluster_sizes[new_label] += 1

        # Mettre à jour le centre des cluster
        for j in range(k):
            if cluster_sizes[j] > 0:
                centers[j, :] = np.mean(X[labels == j, :], axis=0)

    return labels


"""
Créeation du dataframe générale permettant le travail sur l'ensemble des données

:param
road : Route sur lequel on veut travailler ex : "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"
data : Dictionnaire des temps entre chaque arrêt entre chaque stops
zoneRoad : Dictionnaire sur les infos des stops par route
num_treads : nombre de threads dispo sur le pc
maxClSize :  taille des clusters voulu

:return
name : Liste des noms des stops
df : le Data frame contenant les temps pour aller de chaque stop à un autre, la latitude, la longitude, le zone,
si c'est une station ou non et son numéro de cluster par kmeans
"""


def creationDataFrame(road, data, zoneRoad, num_threads, maxClSize):
    # Liste des noms du stop
    name = list(list(data[road].values())[0])

    # Liste des latitudes de chaques point
    listelat = [stop['lat'] for stop in zoneRoad[road]['stops'].values()]

    # Liste des longitudes de chaque point
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

    station = df.loc[df["isStation"] == True]
    dfWithoutStation = df.drop(columns=[station.index[0], 'isStation', 'lat', 'lng', 'zone_id', 'cluster'],
                               index=[station.index[0]]).to_numpy()

    if ceil(dfWithoutStation.shape[0]/maxClSize) < num_threads:
        numberCl = ceil(dfWithoutStation.shape[0]/maxClSize)
    else:
        numberCl = num_threads

    newCluster = balancedKmeans(dfWithoutStation, numberCl)
    cpt = 0
    df["cluster Kmeans"] = [0] * len(name)
    for el in name:
        if not df.loc[el, "isStation"]:
            df.at[el, 'cluster Kmeans'] = newCluster[cpt]
            cpt += 1
        else:
            df.at[el, 'cluster Kmeans'] = -1

    return name, df


"""
Récupération du dataframe contenant toutes les informations sur les packages, en particulier les horaires de livraions

:param
package : Dictionnaire contenant les informations du fichier package

:return
dfPackage : dataframe contenant les informations avec RouteID, Stop, PackageID, start_time et end_time
"""


def creationDataframePackage(package):
    # Initialiser un dictionnaire pour stocker les données
    result = {'RouteID': [], 'Stop': [], 'PackageID': [], 'start_time': [], 'end_time': []}
    # Parcourir chaque RouteID
    for route_id in package.keys():
        # Parcourir chaque stop associé à cette route
        for stop, packages in package[route_id].items():
            # Parcourir chaque package associé à ce stop
            for package_id, package_info in packages.items():
                # Extraire les valeurs de start_time et end_time
                start_time = package_info['time_window']['start_time_utc']
                end_time = package_info['time_window']['end_time_utc']
                # Stocker les informations dans le dictionnaire
                result['RouteID'].append(route_id)
                result['Stop'].append(stop)
                result['PackageID'].append(package_id)
                result['start_time'].append(start_time)
                result['end_time'].append(end_time)

    # Convertir le dictionnaire en dataframe
    dfPackage = pd.DataFrame(result)
    return dfPackage
