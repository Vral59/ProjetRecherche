import json
import pandas as pd

road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"

with open('firstRoad.json', 'r') as f:
    data = json.load(f)

with open('projet recherche/model_build_inputs/route_data.json', 'r') as f:
    zoneRoad = json.load(f)


name = list(list(data[road].values())[0])

zoneList = [zone['zone_id'] for zone in zoneRoad[road]['stops'].values()]

df = pd.DataFrame(columns=name, index=name)
print(len(name))
for el in name:
    row = data[road][el]
    df.loc[el] = pd.Series(row)
df["zone_id"] = zoneList

print(df)


