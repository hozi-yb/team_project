import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import plotly.express as px
from folium import IFrame

#맵그리기
map = folium.Map(location=[36.864873, 128.016729], zoom_start=7)
#연/월 맵 구분
year_map = folium.FeatureGroup(name="year").add_to(map)
month_map = folium.FeatureGroup(name="month").add_to(map)

#데이터
data = pd.read_csv("./data/insolation_data.csv", encoding="cp949")
data.columns = ["loc_num", "loc_name", "date", "insolation", "latitude", "longitude"]

#############################연 지도 그리기 ################################
df = data.groupby("loc_name").agg({"insolation" : "sum","latitude" : "mean", "longitude" : "mean"})
sun_data = [[row['latitude'], row['longitude'], row['insolation']] for index, row in df.iterrows()]
#연지도
for d in range(len(df)) :
    #차트
    categories = df.columns[0]
    values = df.iloc[d]["insolation"]
    fig = px.bar(x=[categories], y=[values], title="detail")
    html = fig.to_html(include_plotlyjs="cdn")
    iframe = IFrame(html, width=300, height=300)
    popup = folium.Popup(iframe, max_width=300).add_to(year_map)

    table = pd.DataFrame(data = [[df.iloc[d]["latitude"], df.iloc[d]["longitude"]]],
                  columns = ['latitude', 'longitude'])
    html = table.to_html(classes='table')

    folium.Marker(
       location= [df.iloc[d]["latitude"], df.iloc[d]["longitude"]],
       tooltip = f'<div style="width:140px"><strong><b>{df.index[d]}</b></strong><br>\
        관측년도 : 2024<br>\
        {html}<br>\
        </div>',
    ).add_to(year_map)
HeatMap(sun_data).add_to(year_map)
#############################연 지도 그리기 ################################

#############################월 지도 그리기 ################################
m = {
    "loc_name" : [],
    "date" : [],
    "insolation" : [],
    "latitude" : [],
    "longitude" : []
}

m_df = pd.DataFrame(m)

for d in range(len(data)) :
    if data.loc[d]["date"] == "24-4" :
        new_row = {
            "loc_name" : [data.loc[d]["loc_name"]],
            "date" : [data.loc[d]["date"]],
            "insolation" : [data.loc[d]["insolation"]],
            "latitude" : [data.loc[d]["latitude"]],
            "longitude" : [data.loc[d]["longitude"]]
        }
        m_df  = pd.concat([m_df, pd.DataFrame(new_row)], ignore_index=True)

m_df

m_sun_data = [[row['latitude'], row['longitude'], row['insolation']] for index, row in m_df.iterrows()]

for d in range(len(m_df)) :
    #차트
    categories = [m_df.columns[0]]
    values = [m_df.iloc[d]["insolation"]]
    plt.figure(f"{d+len(m_df)+1}", figsize=(2,2))
    chart = plt.barh(categories, values, color="r")
    plt.savefig(f'm_img{d+len(m_df)+1}.png')
    #표
    m_table = pd.DataFrame(data = [[m_df.iloc[d]["latitude"], m_df.iloc[d]["longitude"]]],
                  columns = ['latitude', 'longitude'])
    m_html = m_table.to_html(classes='table')

    folium.Marker(
       location= [m_df.iloc[d]["latitude"], m_df.iloc[d]["longitude"]],
       popup = f'<div style="width:120px"><strong><b>{m_df.iloc[d]["loc_name"]}</b></strong><br>\
        관측월 : 24-4<br>\
        {m_html}<br>\
        <a href="https://www.naver.com/"><img width="80px" src="m_img{d+len(m_df)+1}.png"></a><br>\
        </div>'
    ).add_to(month_map)
HeatMap(m_sun_data).add_to(month_map)

#####'''########################월 지도 그리기 ################################

# folium.LayerControl(collapsed=False).add_to(map)
# map.save('heatmap.html')