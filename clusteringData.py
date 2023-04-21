import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.spatial import KDTree
import itertools

"""
Récupératition du premier point après le départ de la station (point le plus proche)
"""

"""
Donne le point le plus proche de la station en temps

:param
station : Ligne du dataframe contenant les informations en partant de la station
points : Liste des points de stops

:return
minName : revoit le point en question en string ex: "VE"
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
Récupération du dernier point (point le plus proche de la station qui est dans un cluster différent du premier)

:param
station : Ligne du dataframe contenant les informations en partant de la station
points : Liste des points de stops
firstPoint : Indice du premier parcouru en partant de la station
df : dataframe contenant toutes les informations de temps

:return
minName : revoit le point en question en string ex: "VE"
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

:param
nbCl : Est le nombre de cluster
df : DataFrame des temps entre chaque point

:return
matrixRes : Matrice d'adjacence en temps des différents cluster ex
    A B C
A : 0 4 5
B : 3 0 3
C : 5 3 0

Temps pour passer du cluster B à C = 3
Sauf que ici on a [index1, index2, distance_min] information par position dans la matrice 
distance_min est le temps et index1 le point dnas le 1er cluster et index2 le point d'arrivé dans le cluster suivant
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

:param 
firstCl : numéro du 1er cluster
lastCl : numéro du dernier cluster
nbCl : nombre de cluster
matriceTime : matrice d'adjacence en temps entre les cluster

:return
permuMin : une liste contenant l'ordre de parcours des cluster
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

