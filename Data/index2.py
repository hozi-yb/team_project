import pandas as pd
import folium
from folium.plugins import HeatMap

data = pd.read_csv("./Data/new.csv", encoding="EUC-KR")
data.columns = ["loc_num", "loc_name", "date", "insolation", "latitude", "longitude"]

df = data.groupby("loc_name").agg({"insolation" : "mean","latitude" : "mean", "longitude" : "mean"})
print(df)

map = folium.Map(location=[36.5, 127.5], zoom_start=7)
sun_data = [[row['latitude'], row['longitude'], row['insolation']] for index, row in df.iterrows()]

HeatMap(sun_data).add_to(map)
map.save('heatmap.html')