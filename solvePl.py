import pulp
from kruskal import kruskal_algo
import random

"""
Dans ce fichier nous résolvons le Pl pour des points donné
"""

"""
Résoud le PL pour un cluster donné

:param
stopCluster : Liste des stop en string
df : dataframe des temps de parcours des points entre eux
package : dataframe des heures de livraisons
v0 : String sommet de départ
vf : String sommet d'arrivé
clidx : index du cluster, utilisé pour le print
path_to_cplex : chemin vers le solver cplex

:return
x : matrice binaire x[i,j] = 1 => on va de i à j 
t : temps d'arrivé au sommet i
status : status de la solution (Optimal, Infeasible)
"""


def solvePl(stopCluster, df, package, v0, vf, clidx, path_to_cplex):
    V = [i for i in stopCluster]
    p = {(i, j): df.loc[i, j] for i in V for j in V}
    a = {i: 0 + random.randint(0, 40) for i in V}
    b = {i: 3000 - random.randint(100, 500) for i in V}

    model = pulp.LpProblem('Pl_livraisons', pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(cat=pulp.LpBinary, name="x_{0}_{1}".format(i, j)) for i in V for j in V}

    t = {i: pulp.LpVariable(lowBound=a[i], upBound=b[i], cat=pulp.LpContinuous, name="t_{0}".format(i)) for i in V}

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
        if a[i] is not None and b[i] is not None:
            model += t[i] >= a[i]
            model += t[i] <= b[i]

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
