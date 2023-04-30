import pulp
from kruskal import kruskal_algo
import random
from datetime import timedelta
import pandas as pd

"""
Dans ce fichier nous résolvons le Pl pour des points donné
"""

"""
Donne l'heure minimum et maximum d'un dataframe, si il n'y a pas d'heure, renvoie un None

:param
df : le dataframe des packages

:return
minTime : le plus grand des temps au plus tot (None sinon)
maxTime : le plus perit des temps au plus tard (None sinon)
"""


def minTimePackage(df):
    min_time = float('inf')
    max_time = float('-inf')

    for _, row in df.iterrows():
        start = row['start_time']
        end = row['end_time']

        if not pd.isna(start):
            start = start.split()
            hh, mm, ss = start[1].split(':')
            start_time = int(hh) * 3600 + int(mm) * 60 + int(ss)
            min_time = min(min_time, start_time)

        if not pd.isna(end):
            end = end.split()
            hh, mm, ss = end[1].split(':')
            end_time = int(hh) * 3600 + int(mm) * 60 + int(ss)
            max_time = max(max_time, end_time)

    if min_time == float('inf'):
        min_time = None

    if max_time == float('-inf'):
        max_time = None

    if min_time is not None and max_time is not None and not pd.isna(row['start_time']) and not pd.isna(row['end_time']):
        if start[0] != end[0] or min_time > max_time:
            return None, None

    return min_time, max_time


"""
Résoud le PL pour un cluster donné

:param
stopCluster : Liste des stop en string
df : dataframe des temps de parcours des points entre eux
package : dataframe des heures de livraisons
v0 : String sommet de départ
vf : String sommet d'arrivé
path_to_cplex : chemin vers le solver cplex

:return
x : matrice binaire x[i,j] = 1 => on va de i à j 
t : temps d'arrivé au sommet i
status : status de la solution (Optimal, Infeasible)
"""


def solvePl(stopCluster, df, package, v0, vf, path_to_cplex):
    V = [i for i in stopCluster]
    p = {(i, j): df.loc[i, j] for i in V for j in V}
    minTimeDic = {}
    maxTimeDic = {}
    for i in V:
        minTime, maxTime = minTimePackage(package.loc[package["Stop"] == i])
        minTimeDic[i] = minTime
        maxTimeDic[i] = maxTime

    model = pulp.LpProblem('Pl_livraisons', pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(cat=pulp.LpBinary, name="x_{0}_{1}".format(i, j)) for i in V for j in V}

    t = {i: pulp.LpVariable(lowBound=minTimeDic[i], upBound=maxTimeDic[i], cat=pulp.LpContinuous, name="t_{0}".format(i)) for i in V}

    # Objective
    model += pulp.lpSum(x[i, j] * p[i, j] for i in V for j in V)

    # constraints

    # kruskal constraints
    model += pulp.lpSum(p[i, j] * x[i, j] for i in V for j in V) >= kruskal_algo(df.to_numpy())

    for i in V:
        if i != vf:
            model += pulp.lpSum(x[i, j] for j in V) == 1

    for j in V:
        if j != v0:
            model += pulp.lpSum(x[i, j] for i in V) == 1

    for i in V:
        aux = pulp.lpSum(x[i, j] for j in V) - pulp.lpSum(x[j, i] for j in V)
        if i == v0:
            model += aux == 1
        elif i == vf:
            model += aux == -1
        else:
            model += aux == 0

    for i in V:
        model += x[i, i] == 0

    for i in V:
        for j in V:
            if i != j:
                model += t[i] + p[i, j] - t[j] <= (df.to_numpy().sum() + df.to_numpy().max()) * (1 - x[i, j])

    for i in V:
        if minTimeDic[i] is not None and maxTimeDic[i] is not None:
            model += t[i] >= minTimeDic[i]
            model += t[i] <= maxTimeDic[i]

    model += pulp.lpSum(x[i, j] for i in V for j in V) == len(stopCluster) - 1

    if len(stopCluster) > 2:
        model += x[v0, vf] == 0
        model += x[vf, v0] == 0

    solver = pulp.CPLEX_CMD(path=path_to_cplex,msg=False)
    model.solve(solver)
    status = pulp.LpStatus[model.status]
    return x, t, status


"""
Fonction qui transforme la matrice binaire x sortie de solverPl en liste des points à parcourir dans l'ordre

:param
x : matrice binaire x[i,j] = 1 => on va de i à j 
stopCluster : liste des stop en string
v0 : sommet de départ en string
vf : sommet final en string

:return
path : liste des sommets dans l'ordre de parcours final
"""


def createPath(x, stopCluster, v0, vf):
    path = [v0]
    dernier = v0
    n = len(stopCluster)
    # On parcourt chaque ligne de la matrice x
    for i in range(n - 1):
        for j in range(n):
            if x[dernier, stopCluster[j]].value() is None:
                return path
            elif x[dernier, stopCluster[j]].value() >= 0.99:
                path.append(stopCluster[j])
                dernier = stopCluster[j]
                if dernier == vf:
                    return path
    return path
