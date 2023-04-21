from pulp import *

# Création des variables de décision xi,j
x = LpVariable.dicts("x", [(i,j) for (i,j) in E], lowBound=0, upBound=1, cat=LpBinary)

# Création des variables de temps de passage ti
t = LpVariable.dicts("t", V, lowBound=0)

# Création du problème d'optimisation
prob = LpProblem("Problème de livraison", LpMinimize)

# Ajout de la fonction objectif
prob += lpSum([x[(i,j)] * pi[(i,j)] for (i,j) in E])

# Contrainte : chaque point de livraison est visité une fois
for i in V:
    if i != vf:
        prob += lpSum([x[(i,j)] for j in V if (i,j) in E]) == 1

# Contrainte : symétrie du graphe
for i in V:
    if i not in [v0, vf]:
        prob += lpSum([x[(i,j)] for j in V if (i,j) in E]) == lpSum([x[(j,i)] for j in V if (j,i) in E])

# Contrainte pour v0
prob += lpSum([x[(v0,j)] for j in V if (v0,j) in E]) - lpSum([x[(j,v0)] for j in V if (j,v0) in E]) == 1

# Contrainte pour vf
prob += lpSum([x[(i,vf)] for i in V if (i,vf) in E]) - lpSum([x[(vf,j)] for j in V if (vf,j) in E]) == -1

# Contrainte : chaque arc partant et arrivant à un même point de livraison doit être inutilisé
for i in V:
    prob += x[(i,i)] == 0

# Contrainte : temps de passage
for (i,j) in E:
    prob += t[i] + pi[(i,j)] - t[j] <= M * (1 - x[(i,j)])
    prob += a[(i,j)] <= t[i]
    prob += t[i] <= b[(i,j)]

# Contrainte : xi,j ∈ {0, 1}
for (i,j) in E:
    prob += x[(i,j)] in [0, 1]

# Résolution du problème d'optimisation
prob.solve()