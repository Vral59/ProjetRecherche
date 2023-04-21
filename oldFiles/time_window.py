import json
import pandas as pd
import numpy as np

with open(r"C:\Users\hp\PycharmProjects\pythonProject\new_package_data.json") as f:
  data = json.load(f)

# Initialiser un dictionnaire pour stocker les données
result = {'RouteID': [], 'Stop': [], 'PackageID': [], 'start_time': [], 'end_time': []}

# Parcourir chaque RouteID
for route_id in data.keys():
    # Parcourir chaque stop associé à cette route
    for stop, packages in data[route_id].items():
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
df = pd.DataFrame(result)
print(df)