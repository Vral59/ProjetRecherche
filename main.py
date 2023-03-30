import pulp as pl
import networkx as nx
import random
import matplotlib.pyplot as plt

path_to_cplex = r'C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211\\cplex\\bin\\x64_win64\\cplex.exe'
solver = pl.CPLEX_CMD(path=path_to_cplex)
"""
Déclaration des variables
"""

V = 10
# Pas utile
#E = 15
M = 15
p = [[random.randint(1, M) for i in range(V)] for j in range(V)]

# Création des bornes de temps
borne_a_b = [[8, 17] for i in range(V)]
v0 = 0
vf = 0

"""
Création du graphe
"""
G = nx.Graph()

G.add_nodes_from([i for i in range(V)])
G.add_edges_from([(random.randint(0, V), random.randint(0, V)) for _ in range(V)])

# print de vérification
print(G.number_of_nodes())
print(G.number_of_edges())
print(list(G.edges))
print(list(G.nodes))
# nx.draw(G,with_labels=True)
# plt.savefig("filename.png")

"""
Création du PL
"""
# # Variable
# x_i_j = pl.LpVariable.dicts("if_i_in_group_j", ((i, j) for i in range(E) for j in range(E)), cat='binary')
# t_i = pl.LpVariable.dicts("time_in_i", (i for i in range(V) ), cat='binary')
# # Objectif
# model = pl.LpProblem("Project", pl.LpMinimize)
# model += pl.lpSum([p[i][j] * x_i_j[i][j] for i in range(E) for j in range(E)])
#
# # Contrainte 1
# for i in range(V): # On devra virer le vf
#     if i != vf:
#         model += (
#                 pl.lpSum(x_i_j[i][j] for j in range(E)) == 1,
#         )
#
# # Contrainte 2
# for j in range(V): # On devra virer le vo
#     if i != v0:
#         model += (
#                 pl.lpSum(x_i_j[i][j] for i in range(E)) == 1,
#         )
#
# # Contrainte 3
# for i in range(V): # On devra virer le vf et vo
#     if i != vf and i != v0:
#         model += (
#                 pl.lpSum(x_i_j[i][j] for j in range(E)) == pl.lpSum(x_i_j[j][i] for j in range(E)),
#         )
#
# # Contrainte 4
#
# model += (
#     pl.lpSum(x_i_j[v0][j] for j in range(E)) - pl.lpSum(x_i_j[j][v0] for j in range(E)) == 1,
# )
#
# # Contrainte 5
# model += (
#     pl.lpSum(x_i_j[vf][j] for j in range(E)) - pl.lpSum(x_i_j[j][vf] for j in range(E)) == -1,
# )
#
# # Contrainte 6
# for i in range(V):
#     model += (
#         x_i_j[i][i] == 0
#     )
#
# # Contrainte 7
# for i in range(V):
#     for j in range(V):
#         model += (
#             t_i[i]+ p[i][j]- t_i[j] <= M * (1 - x_i_j[i][j])
#         )
#
# # Contrainte 8
# for i in range(V):
#     model += (
#         t_i[i] <= borne_a_b[i][1]
#     )
#     model += (
#         t_i[i] >= borne_a_b[i][0]
#     )
# # Contrainte 9
# for i in range(V):
#     for j in range(V):
#         x in {0;1}
# model.solve(solver)


