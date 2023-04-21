import eval
import clusteringData
import readData
import solvePl

"""
Dans ce fichier main, nous lions tous le projet
"""

def main():
    # Définition des chemins

    # On travail pour une route fixé pour le moment
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
    cheminFinal = clusteringData.findPathCluster(clfirst, cllast, nbCl, matriceTime)
    cheminFinal.insert(0, clfirst)
    cheminFinal.append(cllast)

    # TODO : utiliser eval.py et le solvePl.py
    return 0


if __name__ == "__main__":
    main()
