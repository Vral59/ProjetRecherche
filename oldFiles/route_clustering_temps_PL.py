import json
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd
import pulp
import networkx as nwx

path_to_cplex = r'/opt/ibm/ILOG/CPLEX_Studio2211/cplex/bin/x86-64_linux/cplex'



with open('model_build_inputs/model_build_inputs/travel_times2.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

route = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"

df2 = df.loc[:,route]
names = df2.index

matrix = pd.DataFrame(columns = names, index = names)

for n in names :
    for m in names :
        matrix.loc[n,m] = df.loc[n,route][m]

with open('model_build_inputs/model_build_inputs/route_data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
zone_id = pd.DataFrame(df.loc['stops',route]).loc['zone_id',:]
type = pd.DataFrame(df.loc['stops',route]).loc['type',:]

dist_mat = matrix   # Pour ajouter la station
dist_mat2 = matrix[type!='Station'] # Pour supprimer la station

lat = pd.DataFrame(df.loc['stops',route]).loc['lat',:]
lng = pd.DataFrame(df.loc['stops',route]).loc['lng',:]

matrix = pd.concat([matrix, zone_id,type,lat,lng], axis = 1)  # matrix pas utilisé dans ce clustering
N = len(matrix)

K=10
model = KMeans(n_clusters=K,n_init='auto',init='k-means++').fit(dist_mat2)  # Diminuer ou augmenter n_cluster
                                                                            # si on ajoute ou pas la station
labels =model.labels_

station = dist_mat[type == 'Station'].index.tolist()[0]
for i in range(N):
    if names[i]==station:
        k=i
        break

clusters = [0]*N
clusters[k] = K
for i in range(N):
    if i<k :
        clusters[i] = labels[i]
    elif i>k:
        clusters[i] = labels[i-1]

col = []
for i in range(N):  # range(N) si on ajoute la station

    if clusters[i] % K == 0 :
        col = col + ['g']
    elif clusters[i] % K == 1 :
        col = col + ['m']
    elif clusters[i] % K== 2 : col = col + ['k']
    elif clusters[i] % K== 3 : col = col + ['c']
    elif clusters[i] % K== 4 : col = col + ['b']
    elif clusters[i] % K== 5 : col = col + ['y']
    else :  # Pour n_clusters = 4 on aura pas cette couleur
        col = col + ['r']


new_lat = []
new_lng = []
for i in range(N-1):
    if type[i] != 'Station':
        new_lat= new_lat + [lat[i]]
        new_lng = new_lng + [lng[i]]



plt.scatter(lat,lng,color=col)  # lat et lng au lieu de new_lat et new_lng si on ajoute la station
# plt.title('Kmeans par temps de parcours (Sans la station)')
plt.title('Kmeans par temps de parcours (Avec la station)')

clusters = pd.DataFrame(clusters,index=names, columns=['cluster']).loc[:,'cluster']


actual_stop = dist_mat[clusters != clusters[station]][station].astype(float).idxmin()
plt.plot([lat[station], lat[actual_stop]], [lng[station], lng[actual_stop]], color='y')

lst_stops = [station, actual_stop]
last_stop = dist_mat[~clusters.isin([clusters[s] for s in lst_stops])][station].astype(float).idxmin()
plt.plot([lat[last_stop], lat[station]], [lng[last_stop], lng[station]], color='y')
lst_stops2 = [station, actual_stop,last_stop]
for i in range(K-2):

    previous_stop = dist_mat[~clusters.isin([clusters[s] for s in lst_stops2])].transpose()[(clusters == clusters[actual_stop]) & (names != actual_stop)].transpose().astype(float).min().idxmin()
    actual_stop = dist_mat[~clusters.isin([clusters[s] for s in lst_stops2])].transpose()[(clusters == clusters[actual_stop]) & (names != actual_stop)].astype(float).min().idxmin()
    lst_stops = lst_stops + [previous_stop,actual_stop]
    lst_stops2 = lst_stops2[0:(len(lst_stops2)-1)] + [previous_stop,actual_stop] + [last_stop]

    plt.plot([lat[previous_stop], lat[actual_stop]], [lng[previous_stop], lng[actual_stop]], color='y')

last_actual = dist_mat[(clusters == clusters[last_stop]) & (names != last_stop)].transpose()[(clusters == clusters[actual_stop]) & (names != actual_stop)].transpose().astype(float).min().idxmin()
last_preview = dist_mat[(clusters == clusters[last_stop]) & (names != last_stop)].transpose()[(clusters == clusters[actual_stop]) & (names != actual_stop)].astype(float).min().idxmin()
plt.plot([lat[last_actual], lat[last_preview]], [lng[last_actual], lng[last_preview]], color='y')

lst_stops2 = lst_stops2[0:(len(lst_stops2)-1)] + [last_actual, last_preview] + [last_stop]
lst_stops = lst_stops2







clusters_n = [[]]*K

for j in range(N-1):
        if j<k:
            clusters_n[labels[j]] = clusters_n[labels[j]] + [names[j]]

        elif j>=k:
            clusters_n[labels[j]] = clusters_n[labels[j]] + [names[j+1]]

P = []
for m in range(K):
    V= [i for i in clusters_n[m]]
    p = {(i,j): dist_mat.loc[i,j] for i in V for j in V if i != j}
    a = {i: 0 for i in V}
    b = {i: 5000 for i in V}

    M = 1000

    for j in range(N):
        if lst_stops[j] in V:
            v0 = lst_stops[j]
            vf = lst_stops[j+1]
            break

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

    for i in V:
        for j in V:
            if x[i, j].varValue == 1:
                plt.plot([lat[i], lat[j]], [lng[i], lng[j]], color='c')
            


plt.xlim([34.085, 34.105])
plt.ylim([-118.2966, -118.2720])
plt.show()

