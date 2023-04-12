import json
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd


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

# dist_mat = matrix.values   # Pour ajouter la station
dist_mat = matrix[type!='Station'].values  # Pour supprimer la station

lat = pd.DataFrame(df.loc['stops',route]).loc['lat',:]
lng = pd.DataFrame(df.loc['stops',route]).loc['lng',:]

matrix = pd.concat([matrix, zone_id,type,lat,lng], axis = 1)  # matrix pas utilisé dans ce clustering


model = KMeans(n_clusters=4, n_init='auto',init='k-means++').fit(dist_mat)  # Diminuer ou augmenter n_cluster
                                                                            # si on ajoute ou pas la station
clusters =model.labels_



N = len(matrix)
col = []
for i in range(N-1):  # range(N) si on ajoute la station
    if clusters[i] == 0 :
        col = col + ['r']
    elif clusters[i] == 1 :
        col = col + ['m']
    elif clusters[i] == 2 : col = col + ['b']
    elif clusters[i] == 3 : col = col + ['g']
    #elif clusters[i] == 4 : col = col + ['y']
    #elif clusters[i] == 5 : col = col + ['c']
    else :  # Pour n_clusters = 4 on aura pas cette couleur
        col = col + ['k']

new_lat = []
new_lng = []
for i in range(N):
    if type[i] != 'Station':
        new_lat= new_lat + [lat[i]]
        new_lng = new_lng + [lng[i]]


plt.figure()
plt.scatter(new_lat,new_lng,color=col)  # lat et lng au lieu de new_lat et new_lng si on ajoute la station
plt.xlim([34.085,34.105])
plt.ylim([-118.2966,-118.2720])
plt.title('Kmeans par temps de parcours (Sans la station)')
#plt.title('Kmeans par temps de parcours (Avec la station)')
plt.show()
