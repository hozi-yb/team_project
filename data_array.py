import pandas as pd
import folium
from folium.plugins import HeatMap

# datas = pd.read_csv("./data/한국에너지기술연구원_신재생자원지도데이터_태양자원_천리안2호_수평면전일사량_20200831.csv", encoding="cp949")

# datas.columns = ["위도","경도","2019-09","2019-10","2019-11","2019-12","2020-01","2020-02","2020-03","2020-04","2020-05","2020-06","2020-07","2020-08"]
# for col in datas.columns[2:13]:
#     datas = datas.drop(columns=col)

# datas.to_csv("./data/2020-08_1.csv",encoding="EUC-KR",index=False)
# # 데이터 불러오기
file_path = './data/2020-08.csv'
data = pd.read_csv(file_path, encoding='cp949')

# 필터링 기준 설정
# min_irradiance = 500  # 최소 일사량 (사용자 지정 가능)

data.columns = ["위도","경도","2020-08"]
# 필터링
# filtered_data = data[data['합계 일사량(MJ/m2)'] >= min_irradiance]

# 해안선 정리
idx_lon = data[(data["경도"]>=129.9) & (data["경도"]<133)].index
print(idx_lon)

# for id in idx_lon:
#     data = data.drop(index=id)

data.columns = ["위도","경도","2020-08"]
# idx_lat = data[(data["위도"]<= 38.462)].index
# print(idx_lat)
# data.sort_values("경도")

# data.to_csv("./data/2020-08.csv",encoding="EUC-KR",index=False)

# # 단위도 바꿔야 합니다.
# # 1kwh/m^2 단위 day 이므로 MJ/m^2 단위 month는 (kwh/m^2 x 3.6MJ/m^2 x 31day) 입니다.


map_center = [data['위도'].mean(),data['경도'].mean()]
solar_map = folium.Map(location=map_center, zoom_start=7)

# 히트맵 데이터 생성
heat_data = data[['위도', '경도', '2020-08']].values.tolist()
HeatMap(heat_data, radius=15).add_to(solar_map)
solar_map.save('solar_recommendations_with_click_popup.html')