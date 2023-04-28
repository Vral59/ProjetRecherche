import eval
import clusteringData
import readData
import solvePl

"""
Dans ce fichier main, nous lions tous le projet
"""

def main():
    # Définition des chemins
    path_to_cplex = r'C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio2211\\cplex\\bin\\x64_win64\\cplex.exe'
    # On travaille pour une route fixé pour le moment
    road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"
    # road = "RouteID_0016bc70-cb8d-48b0-aa55-8ee50bdcdb59"
    pathToTimeRoad = 'road/firstRoad.json'
    pathToRoad = 'projet recherche/model_build_inputs/route_data.json'
    pathToPackage = 'projet recherche/model_build_inputs/package_data.json'

    # Lecture des donnnées
    data, zoneRoad, package = readData.openFile(pathToTimeRoad, pathToRoad, pathToPackage)
    name, df = readData.creationDataFrame(road, data, zoneRoad)
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
    # TODO : Appliquer un PL la dessus au lieu de l'algo utilise, le temps de calcule explose
    cheminFinal = clusteringData.findPathCluster(clfirst, cllast, nbCl, matriceTime)
    cheminFinal.insert(0, clfirst)
    cheminFinal.append(cllast)

    # Solvons le problème pour chaque sous cluster
    respath = []
    for clidx in range(nbCl):
        print("Pour cl = ", clidx)
        if clidx == 0:
            v0 = firstPoint
        else:
            v0 = matriceTime[cheminFinal[clidx-1]][cheminFinal[clidx]][1]

        if clidx == nbCl - 1:
            vf = lastPoint
        else:
            vf = matriceTime[cheminFinal[clidx]][cheminFinal[clidx+1]][0]
        dfaux = df.loc[df["cluster Kmeans"] == cheminFinal[clidx]]
        stopCluster = list(dfaux.index)
        print("nb points : ", len(stopCluster))

        # TODO : Vérifier les boucles
        dfaux = dfaux[stopCluster]
        x, t = solvePl.solvePl(stopCluster, dfaux, package, v0, vf, path_to_cplex)
        res = solvePl.createPath(x, stopCluster, v0, vf)
        respath.append(res)

    print("résultat finale : ", respath)
    return 0


if __name__ == "__main__":
    main()
