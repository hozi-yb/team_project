import pandas as pd
import geopandas as gpd
import fiona

import folium
from folium import IFrame
from folium.plugins import GroupedLayerControl

from shapely.geometry import Point
from matplotlib.colors import Normalize, rgb2hex
from matplotlib import colormaps 
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots


#----------------------------------데이터프레임
# 시/도 데이터프레임
facility_df = pd.read_csv("./fa_data/2023_신규_발전소_설치.csv", encoding="euc-kr")
e_power_df = pd.read_csv("./fa_data/2023_신규_발전량.csv", encoding="euc-kr")
sido_area = pd.read_csv("./fa_data/시도별_면적.csv", encoding="euc-kr")
power_usage = pd.read_csv("./fa_data/2020-08 시도별 산업용 전력사용량.csv",encoding="euc_kr")

facility_df.columns = ["loc_nm", "facility_capacity","facility_count", "latitude", "longitude"]
e_power_df.columns = ["loc_nm", "insolation_capacity", "electric", "latitude", "longitude"]
sido_area.columns = ["loc_nm", "area", "electric_capacity", "latitude", "longitude"]
power_usage.columns = ["date","loc_nm","category","unit_pu(kwh/count)","unit_pu(%)"]

# 행정동 데이터프레임
df = pd.read_csv(r".\Data\2020-08.csv", encoding="EUC-KR")
df.columns = ["latitude", "longitude","insolation per day (kmh/m^2)"]
#일평균 일사량을 월 합계 일사량으로 바꾼 column 추가하기
df["insolation per month (kmh/m^2)"] = df["insolation per day (kmh/m^2)"] * 31



#---------------------------------행정동geojson

#관측 지점의 좌표가 Geojson 데이터의 어느 도시에 속하는지 확인하는 코드
geojson_path = r"./data/HangJeongDong_ver20241001.geojson"

gdf = gpd.read_file(geojson_path)

#확인할 좌표 리스트
df['coord'] = list(zip(df['latitude'], df["longitude"]))

#해당 도시 없는 좌표의 데이터들을 삭제 (바다, 북한 등)
df = pd.read_csv(r".\Data\2020-08_insol_filtered.csv")

df = df[df["city"] != "해당 도시 없음"]
#df.to_csv("2020-08_insol_filtered.csv")

#df에서 "insolation per month (kmh/m^2)" 행과 "city" 행만 남기기

insol_df = df[["city", "insolation per month (kmh/m^2)"]]
insol_df = insol_df.reset_index(drop=True)

#같은 도시에 있는 8월 합계 일사량끼리 평균하기

city_insol_df = insol_df.groupby("city")["insolation per month (kmh/m^2)"].mean().reset_index()


#일사량을 컬러맵으로 매핑

min_insol = city_insol_df['insolation per month (kmh/m^2)'].min()
max_insol = city_insol_df['insolation per month (kmh/m^2)'].max()
colormap = colormaps["coolwarm"]



norm = Normalize(vmin = min_insol, vmax = max_insol)
print(min_insol, max_insol) #최소, 최대 일사량 값 확인

city_insol_df["Color(hex)"] = city_insol_df["insolation per month (kmh/m^2)"].apply(lambda insol: rgb2hex(colormap(norm(insol)))) 
# 일사량 값을 정규화 하여 컬러맵으로 변환

#GeoJSON 데이터 읍, 면, 동 삭제하고 시 단위로 이름 단순화

def simplify_city_name(full_name):
    if " " in full_name:
        return full_name.split()[0] + " " + full_name.split()[1]
    return full_name

gdf['simple_name'] = gdf["adm_nm"].apply(simplify_city_name) #시 단위로 이름 단순화

#GeoJSON 데이터를 시 단위로 묶기

gdf_grouped = gdf.dissolve(by = "simple_name", as_index=False)


#Folium에 사용할 데이터 준비: gdf_grouped데이터와 city_insol_df 병합

merged = gdf_grouped.merge(city_insol_df, left_on="simple_name", right_on="city", how = "left")
#print(aug_df.info())
# print(merged.info())



#--------------------------------facility_df

# geojson 읽어오기
geojson = gpd.read_file("./fa_data/법정구역_시군구.geojson", encoding="utf-8")

# 발전소 포인트 찍기
geo_point = []
for _, data in facility_df.iterrows():
    # data = pd.DataFrame(data)
    # print(data)
    facility_point = Point(data["longitude"], data["latitude"])
    # 포인트 포함된 지역
    zone_point = geojson[geojson.contains(facility_point)]

    # zone_point에 포인트지역 넣기
    if not zone_point.empty:
        zone_name = zone_point.iloc[0]['CTP_KOR_NM']
    else:
        zone_name = None
    
    # geo_point 리스트에 append
    geo_point.append(zone_name)



# 색상데이터를 위한 count 노멀라이즈
facility_df["facility_count"] = facility_df["facility_count"].str.replace(",", "").astype(float)
norm = Normalize(vmin=facility_df["facility_count"].min(), vmax=facility_df["facility_count"].max())
facility_df['normalized_count'] = facility_df['facility_count'].apply(norm)

# 발전소 데이터에 새로 컬럼 추가해서 해당하는 지역이름 넣기
facility_df["CTP_KOR_NM"] = geo_point
sido_area["CTP_KOR_NM"] = geo_point
# merge~
merge_geojson = geojson.merge(facility_df, left_on="CTP_KOR_NM", right_on="CTP_KOR_NM", how="left")



#------------------------------ 맵 생성/저장

m = folium.Map(location=[37.56, 126.98], zoom_start=7, tiles="cartoDB Positron")  # 기준지역 맵 생성


# 레이어 컨트롤
fg1 = folium.FeatureGroup(name="2020년 8월 일사량", show=True)
m.add_child(fg1)
fg2 = folium.FeatureGroup(name="시/도 별 태양광발전 설비현황", show=False)
m.add_child(fg2)
fg3 = folium.FeatureGroup(name="전력사용량 대비 태양광발전량", show=False)
m.add_child(fg3)
fg4 = folium.FeatureGroup(name="시/도 별 면적대비 설비용량", show=False)
m.add_child(fg4)

folium.LayerControl(collapsed=False).add_to(m)

# 레이어 그룹만들기
GroupedLayerControl(
    groups={'행정동별': [fg1],'시/도': [fg2, fg3, fg4]},
    exclusive_groups=False
).add_to(m)


# 색상

# 스타일함수
def colormap(value):
    return rgb2hex((value, 1 - value, 0))

# 스타일 1
def style_function(x):
    facility_count = x["properties"].get("normalized_count", 0)
    print(facility_count)
    return {
        "fillColor": colormap(facility_count),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.4,
    }

# 행정동 스타일
def style_function_2(feature):
    color = feature['properties'].get('Color(hex)', None)
    if color: #색상이 있는 경우 
        return {
            "fillColor" : color,
            "color" : "black", #경계선 색
            "weight": 1, #경계선 두께
            "fillOpacity": 0.7
        }
    else: #색상 데이터가 없는 경우 투명 처리
        return {
            "fillColor" : "transparent",
            "color" : "black", #경계선 색
            "weight": 1, #경계선 두께
            "fillOpacity": 0
        }




# geojson 저장 / 툴팁, 스타일, 팝업

# ---- 행정동 geojson 저장
folium.GeoJson(
    merged,
    style_function = style_function_2,
    tooltip = folium.GeoJsonTooltip(fields=["simple_name", "insolation per month (kmh/m^2)"])
).add_to(fg1)


# ---- 시/도 태양광설비 geojson 저장
folium.GeoJson(
    merge_geojson,
    tooltip=folium.GeoJsonTooltip(fields=["CTP_KOR_NM", "facility_capacity", "facility_count"],
                                   aliases=["지역명:", "설비 용량 (KW) :", "설비 개수:"],),
    style_function=style_function,
    popup= folium.Popup("2023년 기준 시설 정보", max_width=300)
).add_to(fg2)


#--------------------바플롯

e_power_bar_plot = []
gm1 = folium.GeoJson(
    merge_geojson,
    style_function=style_function
)

for i in range(len(e_power_df)) :
    # 신규 발전량 값
    name = e_power_df.columns[1:3]
    value = e_power_df.iloc[i, 1:3]
    # 산업용 전력 사용량 값
    region_data = power_usage[power_usage["loc_nm"]==e_power_df.iloc[i,0]]



    fig = make_subplots(rows=2, cols=2,
                specs=[[{"type": "bar", "rowspan": 2}, {"type": "table"}],
                        [None, {"type": "domain"}]],
                           )
    # 제목
    fig.update_layout(title_text= f"{e_power_df.iloc[i, 0]} 발전량 및 전력 사용량",
                       title_x = 0.5,
                       legend_y=0.5,
                       legend_x=-0.15)
    # bar plot 추가
    fig.add_trace(go.Bar( y=value ,x=name),
                  row=1, col=1)
    fig.add_annotation(x=0, y=10,
            text=f"{(value.iloc[0] / value.iloc[1] * 100):.2f}%",
            showarrow=True,
            arrowhead=1)
    
    fig.add_annotation(x=1, y=10,
            text=f"{100 - (value.iloc[0] / value.iloc[1] * 100):.2f}%",
            showarrow=True,
            arrowhead=1)
    
    # 테이블 추가
    fig.add_trace(
        go.Table(
            header=dict(values=name),
            cells=dict(values=value)
            ),row=1, col=2
        )

    if not region_data.empty:
        fig.add_trace(
            go.Pie(
                labels=region_data["category"],
                values = region_data["unit_pu(%)"],
                name = "산업용 전력 비율(%)",
            ),row=2, col=2 
        )
        fig.update_layout(showlegend = False)


    fig.update_yaxes(title_text='단위: KW')

    html = fig.to_html(include_plotlyjs="cdn")
    iframe = IFrame(html, width=700, height=600)
    popup = folium.Popup(iframe, max_width=700)

    e_power_bar_plot.append(popup)


    # # 바플롯에 퍼센트 출력
    # fig.add_annotation(x=0, y=10,
    #         text=f"{(value.iloc[0] / value.iloc[1] * 100):.2f}%",
    #         showarrow=True,
    #         arrowhead=1)

    # fig.add_annotation(x=1, y=10,
    #         text=f"{100 - (value.iloc[0] / value.iloc[1] * 100):.2f}%",
    #         showarrow=True,
    #         arrowhead=1)

    # # html로 플롯 내보내기
    # html = fig.to_html(include_plotlyjs="cdn")
    # iframe = IFrame(html, width=400, height=600)
    # popup = folium.Popup(iframe, max_width=500)

    # e_power_bar_plot.append(popup)


# 플롯 마커에 추가 후 맵으로
for i in range(len(e_power_bar_plot)):
    location = [e_power_df.loc[i, 'latitude'], e_power_df.loc[i, 'longitude']]
    marker = folium.Marker(location=location)
    marker.add_child(e_power_bar_plot[i])
    gm1.add_child(marker)

gm1.add_to(fg3)


# 시/도 geojson 병합 후 맵에 저장
merge_geojson = geojson.merge(sido_area, left_on="CTP_KOR_NM", right_on="CTP_KOR_NM", how="left")

gm2 = folium.GeoJson(
    merge_geojson,
    tooltip=folium.GeoJsonTooltip(fields=["loc_nm", "area", "electric_capacity"],
                                  aliases=["지역명:", "지역면적:", "설비 용량(KW):"])
    # style_function=style_function
)

# 각 위치에 마커 추가
for i in range(len(sido_area)):
    location = [sido_area.loc[i, 'latitude'], sido_area.loc[i, 'longitude']]
    electric_capacity_per_area = sido_area.loc[i, 'electric_capacity'] / sido_area.loc[i, 'area']
    tooltip_text = f"지역명: {sido_area.loc[i, 'loc_nm']}<br>지역면적: {sido_area.loc[i, 'area']}<br>설비 용량(KW): {sido_area.loc[i, 'electric_capacity']}<br>설비 용량 / 면적: {electric_capacity_per_area:.2f}"
    marker = folium.Marker(location=location, tooltip=tooltip_text)
    gm2.add_child(marker)

gm2.add_to(fg4)

m.save("./Visualization/insolation_facility_map.html")
print("맵 생성 완료")