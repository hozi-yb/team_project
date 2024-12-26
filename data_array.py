import pandas as pd
import folium
from folium.plugins import HeatMap, marker_cluster

# datas = pd.read_csv("./data/한국에너지기술연구원_신재생자원지도데이터_태양자원_천리안2호_수평면전일사량_20200831.csv", encoding="cp949")

# datas.columns = ["위도","경도","2019-09","2019-10","2019-11","2019-12","2020-01","2020-02","2020-03","2020-04","2020-05","2020-06","2020-07","2020-08"]
# for col in datas.columns[2:13]:
#     datas = datas.drop(columns=col)

# datas.to_csv("./data/2020-08_1.csv",encoding="EUC-KR",index=False)
# data call
file_path = './data/2020-08.csv'
data = pd.read_csv(file_path, encoding='cp949')
data.columns = ["위도","경도","2020-08"]
filtered_data = data[(data['2020-08'] >= 2.89) & (data['2020-08'] <= 4.4)]
# data.sort_values("2020-08")
# data Normalization
# data.to_csv("./data/2020-08.csv",encoding="EUC-KR",index=False)
# 해안선 정리
# idx_lon = data[(data["위도"]>=36.09235624359383) & (data["위도"]<=37.27578688222246)&(data["경도"]>=129.48570288602764)].index
# print(idx_lon)

for i in range(681529):
    filtered_data = filtered_data[i][2] * 3.2 * 31
    print(filtered_data)

# for id in filtered_data.columns[2]:
#     filtered_data= filtered_data.drop(index=id)

# filtered_data.to_csv("./data/2020-08.csv",encoding="EUC-KR",index=False)



# Cneter location
# map_center =[filtered_data['위도'].mean(),filtered_data['경도'].mean()]
# solar_map = folium.Map(location=map_center, zoom_start=7)

# # created Heatmap data
# heat_data = filtered_data[['위도', '경도', '2020-08']].values.tolist()
# HeatMap(heat_data, radius=12).add_to(solar_map)

# solar_map.save('solar_recommendations_with_click_popup.html')






























# 필터링 기준 설정
# min_irradiance = 3.0788717764918605 # 최소 일사량 (사용자 지정 가능)
# max_irradiance = 4.0788717764918605
# min_irradiance = [data['2020-08'].mean()]
# 필터링


# idx_lat = data[(data["위도"]<= 38.462)].index
# print(idx_lat)
# data.sort_values("경도")

# data.to_csv("./data/2020-08.csv",encoding="EUC-KR",index=False)

# # 단위도 바꿔야 합니다.
# # 1kwh/m^2 단위 day 이므로 MJ/m^2 단위 month는 (kwh/m^2 x 3.6MJ/m^2 x 31day) 입니다.