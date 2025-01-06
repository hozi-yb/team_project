import pandas as pd
import geopandas as gpd

import branca.colormap as cm
import folium
from folium import IFrame
from folium.plugins import GroupedLayerControl

from shapely.geometry import Point
from matplotlib.colors import Normalize

import plotly.graph_objects as go
from plotly.subplots import make_subplots


#----------------------------------데이터프레임
# 시/도 데이터프레임
facility_df = pd.read_csv("./fa_data/2023_누적_발전소_설치.csv", encoding="euc-kr")
e_power_df = pd.read_csv("./fa_data/2020년_8월_발전량.csv", encoding="euc-kr")
sido_area = pd.read_csv("./fa_data/시도별_면적.csv", encoding="euc-kr")
power_usage = pd.read_csv("./fa_data/2020-08 시도별 산업용 전력사용량.csv", encoding="euc-kr")

facility_df.columns = ["loc_nm", "facility_capacity","facility_count", "latitude", "longitude"]
e_power_df.columns = ["loc_nm", "insolation_capacity", "electric", "latitude", "longitude"]
sido_area.columns = ["loc_nm", "area", "electric_capacity", "latitude", "longitude"]
power_usage.columns = ["date","loc_nm","category","unit_pu(kwh/count)","unit_pu(%)"]


# 행정동 데이터프레임
df = pd.read_csv(r".\Data\2020-08_insol_filtered.csv", encoding="UTF-8")
hangjeong_insolation_df = pd.read_csv(r".\Data\2020-08.csv", encoding="EUC-KR")
hangjeong_insolation_df.columns = ["latitude", "longitude","insolation per day (kmh/m^2)"]
#일평균 일사량을 월 합계 일사량으로 바꾼 column 추가하기
hangjeong_insolation_df["insolation per month (kmh/m^2)"] = hangjeong_insolation_df["insolation per day (kmh/m^2)"] * 31

# New
solar_plant_df = pd.read_csv("./Data/solar_power_plant.csv", encoding="EUC-KR")
solar_plant_df.columns = ["city", "the number of solar generator","power generation capacity(kWh)"]

# 시/ 도 일사량
insol_df = df[["city", "insolation per month (kmh/m^2)"]]
insol_df = insol_df.reset_index(drop=True)
insol_df["SiDo"] = insol_df["city"].str.split().str[0]
sido_insol_df = insol_df.groupby("SiDo")["insolation per month (kmh/m^2)"].mean().reset_index()



#---------------------------------행정동geojson

#관측 지점의 좌표가 Geojson 데이터의 어느 도시에 속하는지 확인하는 코드
geojson_path = r".\Data\HangJeongDong_ver20241001.geojson"
gdf = gpd.read_file(geojson_path)

#확인할 좌표 리스트
hangjeong_insolation_df['coord'] = list(zip(hangjeong_insolation_df['latitude'], hangjeong_insolation_df["longitude"]))
#해당 도시 없는 좌표의 데이터들을 삭제 (바다, 북한 등)
hangjeong_insolation_df = pd.read_csv(r".\Data\2020-08_insol_filtered.csv")
hangjeong_insolation_df = hangjeong_insolation_df[hangjeong_insolation_df["city"] != "해당 도시 없음"]

#df에서 "insolation per month (kmh/m^2)" 행과 "city" 행만 남기기
insol_df = hangjeong_insolation_df[["city", "insolation per month (kmh/m^2)"]]
insol_df = insol_df.reset_index(drop=True)

#같은 도시에 있는 8월 합계 일사량끼리 평균하기
city_insol_df = insol_df.groupby("city")["insolation per month (kmh/m^2)"].mean().reset_index()



#----------------------------------일사량을 컬러맵으로 매핑
colormap1 = cm.LinearColormap(["green", "yellow" ,"red"])

# 컬러맵을 위한 데이터 정규화 / 컬러맵 적용
def norm_color(x, y):
    norm_min = x[y].min()
    norm_max = x[y].max()
    norm = Normalize(vmin= norm_min, vmax= norm_max)
    x["for_Norm_color"] = x[y].apply(lambda color: colormap1(norm(color)))
    return x["for_Norm_color"]

# 설비개수, 설비용량 컬러맵을 df에 따로 저장하기 위한..
def norm_color_2(x, y):
    norm_min = x[y].min()
    norm_max = x[y].max()
    norm = Normalize(vmin= norm_min, vmax= norm_max)
    x["for_Norm_color_2"] = x[y].apply(lambda color: colormap1(norm(color)))
    return x["for_Norm_color_2"]
#--------------------------------------------------------



# 일사량 값을 정규화 하여 컬러맵으로 변환
norm_color(city_insol_df, 'insolation per month (kmh/m^2)')



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



#--------------------행정동으로 시/도 geojson

# 일사량 값을 정규화 하여 컬러맵으로 변환
norm_color(sido_insol_df, 'insolation per month (kmh/m^2)')

#GeoJSON 데이터 읍, 면, 동, 시 삭제하고 광역시/도 단위로 묶기
gdf_sido_grouped = gdf.dissolve(by = "sidonm", as_index=False)

#Folium에 사용할 데이터 준비: gdf_sido_grouped데이터와 sido_insol_df 병합
sido_merged = gdf_sido_grouped.merge(sido_insol_df, left_on="sidonm", right_on="SiDo", how = "left")



#-------------------solar_plant_df

geojson_cities = set(gdf["sidonm"] + " " + gdf["sggnm"]) #GeoJSON 데이터에서의 시군구 도시명 추출
df_cities = set(solar_plant_df["city"]) # 시군구별 태양광 설비 용량 데이터에서의 시군구 도시명 추출

#불일치 요소 찾기
only_in_geojson = sorted(geojson_cities - df_cities)
only_in_df = sorted(df_cities - geojson_cities)

#불일치 비교 표 만들기
comparison_df = pd.DataFrame({
    "only_in_geojson": pd.Series(only_in_geojson),
    "only_in_df": pd.Series(only_in_df)
})


#df 수정하기
solar_plant_df.loc[ solar_plant_df['city'] =="강원특별자치도 횡선군", "city"] ="강원특별자치도 횡성군" #시군구명 오타 수정

keyword = "세종특별자치시"   #세종 특별 자치시의 값들 합산하여 한 열로 통합하기

filtered_rows = solar_plant_df[solar_plant_df["city"].str.contains(keyword)] #세종특별자치시에 포함되는 행 필터링

new_row = {  #GeoJSON 기준으로 맞춰주기
    'city': '세종특별자치시 세종시', 
    'the number of solar generator': filtered_rows['the number of solar generator'].sum(),
    "power generation capacity(kWh)": filtered_rows["power generation capacity(kWh)"].sum()
}

#필터링된 행 제거
solar_plant_df = solar_plant_df[~solar_plant_df["city"].str.contains(keyword)].reset_index(drop=True)

#새로운 행 추가
solar_plant_df = pd.concat([solar_plant_df, pd.DataFrame([new_row])], ignore_index=True)

#도시명 불일치 중간 점검
df_cities = set(solar_plant_df["city"]) # 시군구별 태양광 설비 용량 데이터에서의 시군구 도시명 추출


#불일치 요소 찾기
only_in_geojson = sorted(geojson_cities - df_cities)
only_in_df = sorted(df_cities - geojson_cities)

#불일치 비교 표 만들기
comparison_df = pd.DataFrame({
    "only_in_geojson": pd.Series(only_in_geojson),
    "only_in_df": pd.Series(only_in_df)
})


#GeoJSON에서 시 이름 옆에 군구가 붙은 도시 폴리곤 모두 시 기준으로 통합해주기

def create_group_name(city_name): #여기서 city_name은 gdf["sggnm"]
    if '시' in city_name and city_name != "시흥시":
        return city_name.split('시')[0] + '시' #gdf["sggnm"]에 '시'가 포함되는지 여부
    return city_name

#시 기준으로 GeoJSON 데이터의 그룹 이름 생성
gdf["city_group"] = gdf["sidonm"] + " " + gdf["sggnm"].apply(create_group_name)

#그룹별 폴리곤 통합
edited_gdf = gdf.dissolve(by = 'city_group')

#통합된 폴리곤의 이름을 다시 설정
edited_gdf['city_name'] = edited_gdf.index

#GeoJSON 과 df 간의 도시명 불일치 중간체크
df_cities = set(solar_plant_df["city"]) # 시군구별 태양광 설비 용량 데이터에서의 시군구 도시명 추출

geojson_cities2 = set(edited_gdf["city_name"]) #GeoJSON 데이터에서의 시군구 도시명 추출


#불일치 요소 찾기

only_in_geojson = sorted(geojson_cities2 - df_cities)
only_in_df = sorted(df_cities - geojson_cities2)

#불일치 비교 표 만들기
comparison_df = pd.DataFrame({
    "only_in_geojson": pd.Series(only_in_geojson),
    "only_in_df": pd.Series(only_in_df)
})


#df에서 같은 지역명을 갖는 데이터끼리 합산 처리해주기
grouped_df = solar_plant_df.groupby('city', as_index=False).sum()
solar_plant_df = grouped_df

#태양광 발전 설비용량을 정규화하여 컬러맵적용
norm_color(solar_plant_df, 'power generation capacity(kWh)')

#Folium에 사용할 데이터 준비: edited_gdf데이터와 df 병합
solar_plant_merged = edited_gdf.merge(solar_plant_df, left_on="city_name", right_on="city", how = "left")


print("solar_plant_df")
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


# 색상데이터를 위한 count, capacity 노멀라이즈
norm_color(facility_df, 'facility_count')
norm_color_2(facility_df, 'facility_capacity')

# 발전소 데이터에 새로 컬럼 추가해서 해당하는 지역이름 넣기
facility_df["CTP_KOR_NM"] = geo_point
sido_area["CTP_KOR_NM"] = geo_point
# merge~
merge_geojson = geojson.merge(facility_df, left_on="CTP_KOR_NM", right_on="CTP_KOR_NM", how="left")


print("facility_df")
#------------------------------ 맵 생성/저장

m = folium.Map(location=[37.56, 126.98], zoom_start=7, tiles="cartoDB Positron")  # 기준지역 맵 생성


# 컬러바 맵에 추가
# colormap1.caption = "컬러바"
colormap1.add_to(m)

# 레이어 컨트롤
fg1 = folium.FeatureGroup(name="2020년 8월 일사량", show=True)
fg2 = folium.FeatureGroup(name="행정동 태양광발전 설비용량 현황 (2024년 기준) ", show=False, lazy=True)
fg1.add_to(m)
fg2.add_to(m)


fg4 = folium.FeatureGroup(name="전력사용량 대비 태양광발전량 (2020년 기준)", show=False, lazy=True)
fg5 = folium.FeatureGroup(name="2020년 8월 일사량", show=False,lazy=True)
fg4.add_to(m)
fg5.add_to(m)


fg3 = folium.FeatureGroup(name="태양광발전 설비현황 (컬러맵 : 개수)", show=False, lazy=True)
fg6 = folium.FeatureGroup(name="태양광발전 설비현황 (컬러맵 : 설비용량)", show=False, lazy=True)
fg3.add_to(m)
fg6.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# 레이어 그룹만들기
GroupedLayerControl(
    groups={'행정동별': [fg1,fg2],'시/도': [fg5, fg4], '시/도 별 태양광발전 설비현황(2023년 기준)' : [fg3, fg6]},
    exclusive_groups=False
).add_to(m)

# 스타일 함수 (지도 단계구분도 색상)

# 시/도 설비현황 count 스타일 
def style_function(feature):
    facility_count = feature["properties"].get("for_Norm_color", None)
    return {
        "fillColor": facility_count,
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.5,
    }

# 시/도 설비현황 capacity 스타일
def style_function_2(feature):
    facility_capacity = feature["properties"].get("for_Norm_color_2", None)
    return {
        "fillColor": facility_capacity,
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.5,
    }
    
# solar_power_plant 일사량 스타일 (진한색)
def style_function_3(feature):
    color = feature['properties'].get('for_Norm_color', None)
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

# 행정동 설비현황 스타일 (연한색)
def style_function_4(feature):
    color = feature['properties'].get('for_Norm_color', None)
    return {
        "fillColor" : color,
        "color" : "black", #경계선 색
        "weight": 1, #경계선 두께
        "fillOpacity": 0.5
    }

#--------------------바플롯

e_power_bar_plot = []
plot_popup = folium.GeoJson(
    merge_geojson,
    style_function=style_function
)

# 플롯 팝업
for i in range(len(e_power_df)) :
    name = e_power_df.columns[1:3]
    value = e_power_df.iloc[i, 1:3]
    
    # 산업용 전력 사용량 값
    region_data = power_usage[power_usage["loc_nm"]==e_power_df.iloc[i,0]]
    # 시/도 데이터
    sido_data = sido_area[sido_area["loc_nm"]==e_power_df.iloc[i,0]]

    fig = make_subplots(rows=2, cols=2,
                    specs=[[{"type": "bar"}, {"type": "pie"}],
                           [{"colspan": 2, "type": "table"}, None]],
                            column_widths=[0.4, 0.6], row_heights =[0.7, 0.3])
    
    fig.update_layout(title_text= f"{e_power_df.iloc[i, 0]} 발전량, 전력 사용량, 면적대비 태양광설비용량",
                       title_x = 0.5,
                       legend_y=0.5,
                       legend_x=-0.15,
                       showlegend=False)

    fig.add_trace(go.Bar( y=value ,x=name),
                  row=1, col=1)

    fig.add_annotation(x=0, y=10,
            text=f"{(value.iloc[0] / value.iloc[1] * 100):.2f}%",
            showarrow=True,
            arrowhead=1)
    
    fig.add_annotation(x=1, y=10,
            text=f"100%",
            showarrow=True,
            arrowhead=1)
    
    fig.add_trace(
        go.Table(
            header=dict(values=["태양광 발전량<br>(2020년 8월)",
                                "전력사용량<br>(2020년 8월)",
                                "단위면적당 설비용량<br>(2023년 기준 누적 설비용량)"]),
            cells=dict(values=[f"{value.iloc[0]}MKW",
                               f"{value.iloc[1]}MKW",
                               f"{sido_area.loc[i, 'electric_capacity'] / sido_area.loc[i, 'area']:.2f}KW/km²"])
            ),row=2, col=1
        )
    if not region_data.empty:
        fig.add_trace(
            go.Pie(
                labels=region_data["category"],
                values = region_data["unit_pu(%)"],
                name = "전력 비율(%)<br>(주거제외)",
                showlegend=False
            ),row=1, col=2 
        )

    fig.update_yaxes(title_text='단위: MKW')

    html = fig.to_html(include_plotlyjs="cdn")
    iframe = IFrame(html, width=750, height=600)
    popup = folium.Popup(iframe, max_width=900)

    e_power_bar_plot.append(popup)


# 플롯 마커에 추가 후 맵으로
for i in range(len(e_power_bar_plot)):
    location = [e_power_df.loc[i, 'latitude'], e_power_df.loc[i, 'longitude']]
    marker = folium.Marker(location=location)
    marker.add_child(e_power_bar_plot[i])
    plot_popup.add_child(marker)

plot_popup.add_to(fg4)

print("바플롯 완료")

# geojson 저장 / 툴팁, 스타일, 팝업

# 행정동 2020년 8월 일사량
folium.GeoJson(
    merged,
    style_function = style_function_3,
    tooltip = folium.GeoJsonTooltip(fields=["simple_name", "insolation per month (kmh/m^2)"])
).add_to(fg1)

# 행정동 태양광발전 설비현황 (2024년 기준) 
folium.GeoJson(
    solar_plant_merged,
    style_function = style_function_4,
    tooltip = folium.GeoJsonTooltip(fields=["city_name", "power generation capacity(kWh)"])
).add_to(fg2)

# 시/도 2020년 8월 일사량
folium.GeoJson(
    sido_merged,
    style_function = style_function_3,
    tooltip = folium.GeoJsonTooltip(fields=["SiDo", "insolation per month (kmh/m^2)"])
).add_to(fg5)

# 시/도 태양광 설비 개수 단계구분도
folium.GeoJson(
    merge_geojson,
    tooltip=folium.GeoJsonTooltip(fields=["CTP_KOR_NM", "facility_capacity", "facility_count"],
                                   aliases=["지역명:", "23년 누적 설비 용량 (KW) :", "23년 누적 설비 개수:"],),
    style_function=style_function
).add_to(fg3)

# 설비용량 단계구분도
folium.GeoJson(
    merge_geojson,
    tooltip=folium.GeoJsonTooltip(fields=["CTP_KOR_NM", "facility_capacity", "facility_count"],
                                   aliases=["지역명:", "23년 누적 설비 용량 (KW) :", "23년 누적 설비 개수:"],),
    style_function=style_function_2
).add_to(fg6)


m.save("./Visualization/insolation_facility_map.html")
print("맵 생성 완료")