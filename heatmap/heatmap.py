# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np
# import pandas as pd
# import geopandas as gpd

# # 시각화 설정
# df = pd.read_csv("./data/수정된 데이터.csv",encoding="EUC-KR")

# cols = list(df.columns)
# cols_short = ["lon", "lat"] + [c.split(" ")[0] for c in cols[2:]]
# df.columns = cols_short

# fig, ax = plt.subplots()
# ax.scatter(df["lat"], df["lon"], c=df["20"])
# print(df.head())

import pandas as pd
import folium
from folium.plugins import HeatMap

# 데이터 불러오기
file_path = './data/수정된 데이터.csv'
data = pd.read_csv(file_path, encoding='euc-kr')

# 필터링 기준 설정
min_irradiance = 500  # 최소 일사량 (사용자 지정 가능)

# 필터링
filtered_data = data[data['합계 일사량(MJ/m2)'] >= min_irradiance]

# 지도 생성
map_center = [filtered_data['위도'].mean(), filtered_data['경도'].mean()]
solar_map = folium.Map(location=map_center, zoom_start=7)

# 히트맵 데이터 생성
heat_data = filtered_data[['위도', '경도', '합계 일사량(MJ/m2)']].values.tolist()
HeatMap(heat_data, radius=15).add_to(solar_map)

# JavaScript 코드 추가 (클릭 이벤트 처리)
click_event_script = """
<script>
    function onMapClick(e) {
        var lat = e.latlng.lat.toFixed(5);
        var lon = e.latlng.lng.toFixed(5);
        var popup = L.popup()
            .setLatLng(e.latlng)
            .setContent("Clicked Location: <br> Latitude: " + lat + "<br> Longitude: " + lon)
            .openOn(map);
    }
    map.on('click', onMapClick);
</script>
"""

# HTML에 JavaScript 추가
solar_map.get_root().add_child(folium.Element(click_event_script))

# 지도 저장
solar_map.save('solar_recommendations_with_click_popup.html')


