import folium
import requests
import pandas as pd

data_name = "./data/123456.csv"
datas = pd.read_csv(data_name,encoding="cp949")

for col in datas:
    datas[col] = datas[col].astype(str).str.replace("?","")

datas.to_csv("./data/수정된 데이터.csv",encoding="EUC-KR" ,index=False)