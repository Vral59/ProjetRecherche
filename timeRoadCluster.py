import json
import pandas as pd

road = "RouteID_00143bdd-0a6b-49ec-bb35-36593d303e77"

with open('firstRoad.json', 'r') as f:
    data = json.load(f)


name = list(list(data[road].values())[0])
df = pd.DataFrame(columns=name, index=name)
print(len(name))
for el in name:
    row = data[road][el]
    df.loc[el] = pd.Series(row)

print(df)


