import pandas as pd
import folium
from folium.plugins import HeatMap

data = pd.read_csv("./data/수정된 데이터.csv", encoding="cp949")
data.columns = ["loc_num", "loc_name", "date", "insolation", "latitude", "longitude"]

df = data.groupby("loc_name").agg({"insolation" : "mean","latitude" : "mean", "longitude" : "mean"})

map = folium.Map(location=[-23.0813, -67.8098], zoom_start=5)
sun_data = [[row['latitude'], row['longitude'], row['insolation']] for index, row in df.iterrows()]

HeatMap(sun_data).add_to(map)
map.save('heatmap.html')