import pulp
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
path_to_cplex : chemin vers le solver cplex

:return
x : matrice binaire x[i,j] = 1 => on va de i à j 
t : temps d'arrivé au sommet i
"""


def solvePl(stopCluster, df, package, v0, vf, path_to_cplex):
    V = [i for i in stopCluster]
    p = {(i, j): df.loc[i, j] for i in V for j in V if i != j}
    a = {i: 0 for i in V}
    b = {i: 5000 for i in V}
    M = 1000

    model = pulp.LpProblem('Pl_livraisons', pulp.LpMinimize)

    x = {(i, j): pulp.LpVariable(cat=pulp.LpBinary, name="x_{0}_{1}".format(i, j)) for i in V for j in V}

    t = {i: pulp.LpVariable(lowBound=a[i], upBound=b[i], cat=pulp.LpContinuous, name="t_{0}".format(i)) for i in V}

    # Objective
    model += pulp.lpSum(x[i, j] * p[i, j] for i in V for j in V if j != i)

    # constraints
    for i in V:
        if i != vf:
            model += pulp.lpSum(x[i, j] for j in V) == 1

    for j in V:
        if j != v0:
            model += pulp.lpSum(x[i, j] for i in V) == 1

    for i in V:
        if i != vf and i != v0:
            model += pulp.lpSum(x[i, j] for j in V) == pulp.lpSum(x[j, i] for j in V)

    model += pulp.lpSum(x[v0, j] for j in V) - pulp.lpSum(x[j, v0] for j in V) == 1
    model += pulp.lpSum(x[vf, j] for j in V) - pulp.lpSum(x[j, vf] for j in V) == -1

    for i in V:
        model += x[i, i] == 0

    for i in V:
        for j in V:
            if i != j:
                model += t[i] + p[i, j] - t[j] <= M * (1 - x[i, j])

    solver = pulp.CPLEX_CMD(path=path_to_cplex)
    model.solve(solver)
    return x, t


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
    n = len(stopCluster)
    # On parcourt chaque ligne de la matrice x
    for i in range(n - 1):
        for j in range(n):
            if x[path[-1], stopCluster[j]].value() == 1.0:
                path.append(stopCluster[j])
                # Sachant qu'il y a un seul 1 on peut break la boucle si on tombe dessus
                break
    return path
