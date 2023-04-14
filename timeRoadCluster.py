import json
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial import KDTree
import itertools

"""
Dans ce fichier nous créons la matrice d'adjacance des temps entres chaque stop d'une route
"""

def openFile():

    with open('firstRoad.json', 'r') as f:
        data = json.load(f)

    with open('projet recherche/model_build_inputs/route_data.json', 'r') as f:
        zoneRoad = json.load(f)
    return data,zoneRoad


def creationDataFrame(road, data, zoneRoad):
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

    return name, df

# Pour la station on va trouver le point le plus proche

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



"""
Fonction  permettant de récupérer les 2 points les plus proches dans 2 nuages de points (un point dans chaque nuage)

:param
nuage1 : les indexs des points dans le nuage 1
nuage2 : les indexs des points dans le nuage 2
X : matrice d'adjacence des points du nuage1 et 2

:return
index1 : l'indice du point dans le nuage1
index2 : l'indice du point dans le nuage2
distanceMin : la distance minimal (en temps ici)
"""


def trouver_points_proches(nuages1, nuages2, X):
    # Création des nuages de points à partir des indices
    nuage1 = X.loc[nuages1, :].to_numpy()
    nuage2 = X.loc[nuages2, :].to_numpy()

    # Création de l'arbre KDTree pour le deuxième nuage de points
    tree2 = KDTree(nuage2)

    # Initialisation des variables pour stocker les indices et la distance des deux points les plus proches
    index1 = None
    index2 = None
    distance_min = np.inf

    # Boucle sur tous les points dans le premier nuage
    for i in range(len(nuage1)):
        # Calcul de la distance entre ce point et tous les points dans le deuxième nuage
        distances, indices = tree2.query(nuage1[i], k=len(nuage2))

        # Boucle sur les indices des points dans le deuxième nuage
        for j in range(len(nuage2)):
            # Calcul de la distance entre les deux points
            distance = X.loc[nuages1[i], nuages2[indices[j]]]

            # Mise à jour des variables si la distance est plus petite que la distance minimale actuelle
            if distance < distance_min:
                index1 = nuages1[i]
                index2 = nuages2[indices[j]]
                distance_min = distance

    # Renvoi des indices des deux points les plus proches et de leur distance
    return index1, index2, distance_min

"""
Générère la matrice d'adjacence de chaque cluster en terme de temps minimal
"""
def genPathMatrix(nbCl,df):
    matrixRes = [[[0, 0, 0] for _ in range(nbCl)] for _ in range(nbCl)]
    for cl1 in range(nbCl):
        for cl2 in range(nbCl):
            if cl1 != cl2:
                points1 = df.loc[df["cluster Kmeans"] == cl1].index.tolist()
                points2 = df.loc[df["cluster Kmeans"] == cl2].index.tolist()
                a_garder = points1 + points2
                colonnes_a_supprimer = [colonne for colonne in df.columns if colonne not in a_garder]
                ligne_a_supprimer = [ligne for ligne in df.index if ligne not in a_garder]
                X = df.drop(columns=colonnes_a_supprimer, index=ligne_a_supprimer)
                index1, index2, distance_min = trouver_points_proches(points1, points2, X)
                matrixRes[cl1][cl2] = [index1, index2, distance_min]
    return matrixRes

"""
Trouve le parcours des cluster minimisant les temps entre elles
"""
def findPathCluster(firstCl, lastCl, nbCl, matriceTime):
    clusterIdxList = [i for i in range(0, nbCl) if (i != firstCl and i != lastCl)]
    permuClusterList = list(map(list, itertools.permutations(clusterIdxList)))
    distMin = np.inf
    permuMin = []
    for permu in permuClusterList:
        dist = 0
        # -3 car on a retiré 2 éléments à la liste (début et fin) + on fait un +1 dans la boucle
        for i in range(nbCl - 3):
            if i == 0:
                dist += matriceTime[firstCl][permu[i]][2]
            else:
                dist += matriceTime[permu[i]][permu[i + 1]][2]
        dist += matriceTime[permu[-1]][lastCl][2]
        if dist < distMin:
            distMin = dist
            permuMin = permu
    return permuMin

def main():

    # Définition de la clé de route
    road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"
    #road = "RouteID_0016bc70-cb8d-48b0-aa55-8ee50bdcdb59"
    # Récupération des donénes
    data, zoneRoad = openFile()

    # création du dataFrame
    name, df = creationDataFrame(road, data, zoneRoad)

    # Récupération des préfixe afin de créer un nombre de clsuter égal
    uniqueCluster = list(set(df["cluster"].tolist()))
    nbCl = len(uniqueCluster) - 1
    # l'algo ne fonctionne pas si y'a que 2 cluster
    if nbCl <= 2:
        nbCl = 3
    # Affichage avec Kmeans en clustering
    station = df.loc[df["isStation"] == True]
    dfWithoutStation = df.drop(columns=[station.index[0], 'isStation', 'lat', 'lng', 'zone_id', 'cluster'],
                               index=[station.index[0]])
    kmeans = KMeans(n_clusters=nbCl, n_init=100, init="k-means++").fit(dfWithoutStation)
    newCluster = kmeans.labels_
    color = ['b', 'g', 'r', 'c', 'y']
    cpt = 0
    df["cluster Kmeans"] = [0] * len(name)
    for el in name:
        if not df.loc[el, "isStation"]:
            lat = df.loc[el, "lat"]
            lng = df.loc[el, "lng"]
            plt.scatter(lat, lng, c=color[newCluster[cpt]])
            df.at[el, 'cluster Kmeans'] = newCluster[cpt]
            cpt += 1
        else:
            df.at[el, 'cluster Kmeans'] = -1

    plt.title("Position point livraison les cluster sont kmeans avec chemin les reliant")

    # Récupération du point le plus proche de la station
    firstPoint = findFirstPoint(station, name)

    # Récupération du point le plus proche de la station qui n'est pas dans le même cluster que le 1er
    lastPoint = findLastPoint(station, name, firstPoint, df)


    clfirst = df.loc[firstPoint, "cluster Kmeans"]
    cllast = df.loc[lastPoint, "cluster Kmeans"]

    # Création de la matrice d'adjacence en temps entre chaque cluster
    matriceTime = genPathMatrix(nbCl,df)

    # création du chemin final entre les cluster
    cheminFinal = findPathCluster(clfirst, cllast, nbCl, matriceTime)
    cheminFinal.insert(0, clfirst)
    cheminFinal.append(cllast)

    # Ajout des segments sur le plot
    for i in range(nbCl - 1):
        index1 = matriceTime[cheminFinal[i]][cheminFinal[i + 1]][0]
        index2 = matriceTime[cheminFinal[i]][cheminFinal[i + 1]][1]
        x1 = [df.loc[index1, "lat"], df.loc[index1, "lng"]]
        y1 = [df.loc[index2, "lat"], df.loc[index2, "lng"]]
        plt.plot([x1[0], y1[0]], [x1[1], y1[1]])

    plt.show()


# Lancement du programme
main()