#두 라이브러리를 불러옵니다

# import pandas as pd
# import netCDF4 as nc
# #이후에 데이터를 불러오고 .nc파일의 변수를 확인해 줍니다

# # NetCDF 파일 열기
# file_path = "./data/KMAPP_solar_FWS_total_mean.nc"
# dataset = nc.Dataset(file_path, "r")

# # 파일 내의 변수 이름 확인
# variables = dataset.variables.keys()
# print(variables)
# #sealab image
# #변수로 'lons', 'lats', 'times', 'drifter', 'time' 이렇게 5개의 변수가 존재하고 각각을 데이터프레임으로 바꾸는 코드를 소개합니다

# a = dataset["X"]
# b = dataset["Y"]
# c = dataset["SWDN_flat_with_shading"]


# df_long = pd.DataFrame(a[:])
# df_lat = pd.DataFrame(b[:])
# df_swdn = pd.DataFrame(c[:])

# #이렇게 하면 안에 들어있던 파일들을 전부 해체해서 쉽게 사용할 수 있게 볼 수 있습니다.

# #이것을 csv로 저장할려면

# df_long.to_csv("./data/long.csv", index = False)
# df_lat.to_csv("./data/lat.csv", index = False)
# df_swdn.to_csv("./data/swdn.csv", index = False)

# #이렇게 저장 하면 됩니다. 코드중에 index = False를 쓰지 않으면 index가 추가로 생성되니까 잊지 말아 주세요
import folium
from folium.plugins import HeatMap
import pandas as pd

# 데이터 준비 (위도, 경도, 일사량)
data = [
    {"latitude": 36.9985, "longitude": 127.7047, "radiation": 315.9},
    {"latitude": 37.5665, "longitude": 126.9780, "radiation": 290.2},
    {"latitude": 35.1796, "longitude": 129.0756, "radiation": 320.5},
    # 필요한 데이터를 추가하세요
]

# DataFrame으로 변환
df = pd.DataFrame(data)

# 중심 위치 설정 (지도 중심 좌표)
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

# Folium 지도 생성
m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

# 히트맵 추가
heat_data = [[row['latitude'], row['longitude'], row['radiation']] for index, row in df.iterrows()]
HeatMap(heat_data, radius=15).add_to(m)

# 팝업 및 마커 추가
for index, row in df.iterrows():
    popup_text = f"위도: {row['latitude']}<br>경도: {row['longitude']}<br>일사량: {row['radiation']} W/m²"
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=folium.Popup(popup_text, max_width=300),
    ).add_to(m)

# 지도를 HTML 파일로 저장하거나 Jupyter Notebook에서 렌더링
m.save("heatmap.html")
m