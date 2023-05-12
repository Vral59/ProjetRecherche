import copy

import eval
import clusteringData
import readData
import solvePl
import multiprocessing
import threading


"""
Dans ce fichier main, nous lions tous le projet
"""

"""
Résoud le PL du sous problème proposé 

:param
respath : liste qui va stocker le résultat de ce sous problème
listStatus : liste qui stocke le status de CPLEX sur la résolution
clidx: indice du cluster
firstPoint: premier point après le départ de la station
lastPoint : dernier point à visiter
matriceTime : Matrice d'adjacence des temps de passage entre les clsuter
cheminFinal : ordre de parcours des cluster
df : dataframe avec les temps de trajet entre chaque stop
nbCl : nombre de cluster
path_to_cplex : chemin vers le solveur CPLEX
package : dataframe des informations sur les packages
"""
def findPathCluster(respath, listStatus, clidx, firstPoint, lastPoint, matriceTime, cheminFinal, df, nbCl, path_to_cplex, package):
    useTime = True
    if clidx == 0:
        v0 = firstPoint
    else:
        v0 = matriceTime[cheminFinal[clidx - 1]][cheminFinal[clidx]][1]

    if clidx == nbCl - 1:
        vf = lastPoint
    else:
        vf = matriceTime[cheminFinal[clidx]][cheminFinal[clidx + 1]][0]
    dfaux = df.loc[df["cluster Kmeans"] == cheminFinal[clidx]]
    stopCluster = list(dfaux.index)
    dfaux = dfaux[stopCluster]
    x, t, status = solvePl.solvePl(stopCluster, dfaux, package, v0, vf, useTime, path_to_cplex)
    if status != "Optimal":
        useTime = False
        x, t, status = solvePl.solvePl(stopCluster, dfaux, package, v0, vf, useTime, path_to_cplex)

    res = solvePl.createPath(x, stopCluster, v0, vf)

    respath[clidx] = res
    listStatus[clidx] = status

"""
Fonction principal du projet
"""
def main(num_threads):
    # Définition des chemins
    path_to_cplex = r'C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211\\cplex\\bin\\x64_win64\\cplex.exe'
    # On travaille pour une route fixé pour le moment
    #road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"
    #road = "RouteID_0016bc70-cb8d-48b0-aa55-8ee50bdcdb59"
    #pathToTimeRoad = 'road/firstRoad.json'
    #pathToTimeRoad = 'road/secondRoad.json'
    pathToTimeRoad = 'projet recherche/model_build_inputs/travel_times.json'
    pathToRoad = 'projet recherche/model_build_inputs/route_data.json'
    pathToPackage = 'projet recherche/model_build_inputs/package_data.json'
    pathToSequences = 'projet recherche/model_build_inputs/actual_sequences.json'

    # Lecture des donnnées
    data, zoneRoad, package, sequences = readData.openFile(pathToTimeRoad, pathToRoad, pathToPackage, pathToSequences)
    dfChemin = readData.creationDateframeSequences(sequences)
    roads = dfChemin["route_id"].tolist()
    for road in roads[:20]:
        print("********************* Calcule d'une route *********************")
        name, df = readData.creationDataFrame(road, data, zoneRoad, num_threads, 25)
        dfPackage = readData.creationDataframePackage(package)
        # Récupération de la ligne de la station
        station = df.loc[df["isStation"] == True]
        # Récupération du nombre de cluster, ils sont numerotes de 0 à X donc le nombre est X + 1
        nbCl = df["cluster Kmeans"].max() + 1

        # Récupération du point le plus proche de la station
        firstPoint = clusteringData.findFirstPoint(station, name)

        # Récupération du point le plus proche de la station qui n'est pas dans le même cluster que le 1er
        lastPoint = clusteringData.findLastPoint(station, name, firstPoint, df)


        clfirst = df.loc[firstPoint, "cluster Kmeans"]
        cllast = df.loc[lastPoint, "cluster Kmeans"]

        # Création de la matrice d'adjacence en temps entre chaque cluster
        matriceTime = clusteringData.genPathMatrix(nbCl,df)

        # création du chemin final entre les cluster
        cheminFinal = clusteringData.findPathCluster(clfirst, cllast, nbCl, matriceTime)
        cheminFinal.insert(0, clfirst)
        cheminFinal.append(cllast)

        # Solvons le problème pour chaque sous cluster
        respath = [None]*nbCl
        listStatus = [None] * nbCl
        threads = []
        for clidx in range(nbCl):
            t = threading.Thread(target=findPathCluster, args=(respath, listStatus, clidx, firstPoint, lastPoint, matriceTime, cheminFinal, df, nbCl, path_to_cplex,
                            dfPackage.loc[dfPackage["RouteID"] == road]))
            threads.append(t)
            t.start()

        # Attente de la fin des threads
        for t in threads:
            t.join()

        possible = True
        for clidx in range(nbCl):
            if listStatus[clidx] == "Infeasible":
                possible = False
            print("Status du PL dans le cluster/thread  ", clidx, " : ", listStatus[clidx])
            print("taille du cl : ", len(df.loc[df["cluster Kmeans"] == cheminFinal[clidx]].axes[0]))
            if len(respath[clidx]) != len(df.loc[df["cluster Kmeans"] == cheminFinal[clidx]].axes[0]):
                print("Le graphe résultat n'est pas connexe")
            print("----------------------------------------")

        # creation du chemin final
        finalPath = [station.index[0]]
        for el in respath:
            finalPath += el
        print("résultat finale : ", finalPath)

        # Récupération du chemin de amazon
        amazonPath = dfChemin.loc[dfChemin["route_id"] == road]["chemin"].tolist()[0]
        print("amazon path", amazonPath)

        # Evaluation du chemin
        print("Evaluation des temps : ")
        if possible:
            tempsNous = df.loc[finalPath[-1]][finalPath[0]]
            tempsAmazon = df.loc[amazonPath[-1]][amazonPath[0]]
            for i in range(len(name)-1):
                tempsNous += df.loc[finalPath[i]][finalPath[i+1]]
                tempsAmazon += df.loc[amazonPath[i]][amazonPath[i + 1]]

            print("Temps de nous :", tempsNous)
            print("Temps de Amazon :", tempsAmazon)
        else :
            print("Pas posssible")
    return 0


if __name__ == "__main__":
    num_threads = multiprocessing.cpu_count()
    main(num_threads)
