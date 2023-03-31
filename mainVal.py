
import pulp
import networkx as nwx
import random
import matplotlib.pyplot as plt
import json

path_to_cplex = r'C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211\\cplex\\bin\\x64_win64\\cplex.exe'

"""
Traitetement des donnees
"""

with open('projet recherche/model_build_inputs/package_data.json', 'r') as f:
  data = json.load(f)



"""
Début algo
"""
n = 6
V = range(1,n)
label = [chr(i+64) for i in V]
G = nwx.DiGraph()
G.add_nodes_from(V,labels = label)
G.add_weighted_edges_from([(i,j,(i+j)/12) for i in V for j in V if i!=j])


p = {}
p = {edge: G.edges[edge]['weight'] for edge in G.edges}
#labels_edges = {edge:'' for edge in G.edges}
# pos = nwx.spring_layout(G, seed=7)
# nwx.draw(G,pos,with_labels=True)
# # pos=nwx.get_node_attributes(G2,'pos')
# edge_labels = nwx.get_edge_attributes(G, "weight")
# nwx.draw_networkx_edge_labels(G, pos, edge_labels)
# plt.savefig('test_graphe_resultat')


a = {i : 8 for i in V}
b = {i : 17 for i in V}
M = 30

v0 = 1
vf = 5


model = pulp.LpProblem('Pl_livraisons', pulp.LpMinimize)

x = {(i,j) : pulp.LpVariable(cat=pulp.LpBinary,name="x_{0}_{1}".format(i,j)) for i in V for j in V}

t = {i : pulp.LpVariable(lowBound=a[i], upBound=b[i],cat=pulp.LpContinuous,name="t_{0}".format(i)) for i in V}

# Objective
model += pulp.lpSum(x[i, j]*p[i, j] for i in V for j in V if j!=i)

#constraints
for i in V:
    if i != vf :
        model += pulp.lpSum(x[i, j] for j in V) == 1

for j in V:
    if j != v0 :
        model += pulp.lpSum(x[i, j] for i in V) == 1

for i in V:
    if i != vf and i != v0:
        model += pulp.lpSum(x[i, j] for j in V) == pulp.lpSum(x[j, i] for j in V)

    model += pulp.lpSum(x[v0, j] for j in V) - pulp.lpSum(x[j, v0] for j in V) == 1
    model += pulp.lpSum(x[vf, j] for j in V) - pulp.lpSum(x[j, vf] for j in V) == -1

#model += x[v0,vf] == 0

for i in V:
    model += x[i, i] == 0

for i in V:
    for j in V:
        if i!=j:
            model += t[i] + p[i, j] - t[j] <= M*(1-x[i, j])




solver = pulp.CPLEX_CMD(path=path_to_cplex)
model.solve(solver)

for i in V :
    for j in V :
        print("Variable x_",i,j," :", x[i,j].varValue)
print("Total Profit: ", pulp.value(model.objective))


n = 6
V = range(1,n)
label = [chr(i+64) for i in V]
G2 = nwx.DiGraph()
G2.add_nodes_from(V,label = label)

G2.add_weighted_edges_from([(i,j,p[i,j]) for i in V for j in V if x[i,j].varValue != 0])
pos = nwx.spring_layout(G2, seed=7)
nwx.draw(G2,pos,with_labels=True)
edge_labels = nwx.get_edge_attributes(G2, "weight")
nwx.draw_networkx_edge_labels(G2, pos, edge_labels)
plt.savefig('test_graphe_resultat')


