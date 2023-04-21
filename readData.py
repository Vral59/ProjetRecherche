import json
import pandas as pd
from sklearn.cluster import KMeans

"""
Dans ce fichier nous allons lire les données et créer les dataframe
"""

"""
Ouvre les json en question

:param
pathToTimeRoad : Temps entre chaque arrêt des routes ex: 'firstRoad.json'
pathToRoad : Routes utilisé par le conducteur ex: 'projet recherche/model_build_inputs/route_data.json'
pathToPackage : Chemin vers le fichier contenenant les informations des colis ex: package_data.json

:return
data : Dictionnaire d'informations contenue dans pathToTimeRoad
zoneRoad : Dictionnaire d'informations contenue dans pathToRoad
package : Dictionnaire des informations contenue dans pathToPackage
"""


def openFile(pathToTimeRoad, pathToRoad, pathToPackage):
    with open(pathToTimeRoad, 'r') as f:
        data = json.load(f)

    with open(pathToRoad, 'r') as f:
        zoneRoad = json.load(f)

    with open(pathToPackage, 'r') as f:
        package = json.load(f)

    return data, zoneRoad, package


"""
Créeation du dataframe générale permettant le travail sur l'ensemble des données

:param
road : Route sur lequel on veut travailler ex : "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"
data : Dictionnaire des temps entre chaque arrêt entre chaque stops
zoneRoad : Dictionnaire sur les infos des stops par route

:return
name : Liste des noms des stops
df : le Data frame contenant les temps pour aller de chaque stop à un autre, la latitude, la longitude, le zone,
si c'est une station ou non et son numéro de cluster par kmeans
"""


def creationDataFrame(road, data, zoneRoad):
    # Liste des noms des stop
    name = list(list(data[road].values())[0])
    # Liste des latitudes de chaques point
    listelat = [stop['lat'] for stop in zoneRoad[road]['stops'].values()]

    # Liste des longitudes de chaque point
    listelng = [stop['lng'] for stop in zoneRoad[road]['stops'].values()]

    # Liste des différentes zone_id de chaque point
    zoneList = [zone['zone_id'] for zone in zoneRoad[road]['stops'].values()]

    # Liste de boolean pour savoir si on a une station
    stationList = [station['type'] == "Station" for station in zoneRoad[road]['stops'].values()]

    df = pd.DataFrame(columns=name, index=name)

    for el in name:
        row = data[road][el]
        df.loc[el] = pd.Series(row)
    # Rajout des colonenes
    df["zone_id"] = zoneList
    df["isStation"] = stationList
    df["lat"] = listelat
    df["lng"] = listelng

    # On récupère les prefixes des zone_id
    cluster = [el.split(".")[0] if str(el) != 'nan' else float("NaN") for el in zoneList]
    df["cluster"] = cluster

    # Creation des cluster avec Kmeans, on pose nbCl = le nombre de zone
    # l'algo ne fonctionne pas si y'a que 2 cluster donc on fixe le minimum à 3
    # TODO :  Ameliorer cette partie de creation de cluster avec kmeans
    uniqueCluster = list(set(df["cluster"].tolist()))
    nbCl = len(uniqueCluster) - 1
    if nbCl <= 2:
        nbCl = 3
    station = df.loc[df["isStation"] == True]
    dfWithoutStation = df.drop(columns=[station.index[0], 'isStation', 'lat', 'lng', 'zone_id', 'cluster'],
                               index=[station.index[0]])
    kmeans = KMeans(n_clusters=nbCl, n_init=100, init="k-means++").fit(dfWithoutStation)
    newCluster = kmeans.labels_
    cpt = 0
    df["cluster Kmeans"] = [0] * len(name)
    for el in name:
        if not df.loc[el, "isStation"]:
            lat = df.loc[el, "lat"]
            lng = df.loc[el, "lng"]
            df.at[el, 'cluster Kmeans'] = newCluster[cpt]
            cpt += 1
        else:
            df.at[el, 'cluster Kmeans'] = -1

    return name, df


"""
Récupération du dataframe contenant toutes les informations sur les packages, en particulier les horaires de livraions

:param
package : Dictionnaire contenant les informations du fichier package

:return
dfPackage : dataframe contenant les informations avec RouteID, Stop, PackageID, start_time et end_time
"""


def creationDataframePackage(package):
    # Initialiser un dictionnaire pour stocker les données
    result = {'RouteID': [], 'Stop': [], 'PackageID': [], 'start_time': [], 'end_time': []}

    # Parcourir chaque RouteID
    for route_id in package.keys():
        # Parcourir chaque stop associé à cette route
        for stop, packages in package[route_id].items():
            # Parcourir chaque package associé à ce stop
            for package_id, package_info in packages.items():
                # Extraire les valeurs de start_time et end_time
                start_time = package_info['time_window']['start_time_utc']
                end_time = package_info['time_window']['end_time_utc']
                # Stocker les informations dans le dictionnaire
                result['RouteID'].append(route_id)
                result['Stop'].append(stop)
                result['PackageID'].append(package_id)
                result['start_time'].append(start_time)
                result['end_time'].append(end_time)

    # Convertir le dictionnaire en dataframe
    dfPackage = pd.DataFrame(result)
    return dfPackage
