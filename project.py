#두 라이브러리를 불러옵니다

import pandas as pd
import netCDF4 as nc
#이후에 데이터를 불러오고 .nc파일의 변수를 확인해 줍니다

# NetCDF 파일 열기
file_path = "./data/KMAPP_solar_FWS_total_mean.nc"
dataset = nc.Dataset(file_path, "r")

# 파일 내의 변수 이름 확인
variables = dataset.variables.keys()
print(variables)
#sealab image
#변수로 'lons', 'lats', 'times', 'drifter', 'time' 이렇게 5개의 변수가 존재하고 각각을 데이터프레임으로 바꾸는 코드를 소개합니다

a = dataset["X"]
b = dataset["Y"]
c = dataset["SWDN_flat_with_shading"]


df_long = pd.DataFrame(a[:])
df_lat = pd.DataFrame(b[:])
df_swdn = pd.DataFrame(c[:])

#이렇게 하면 안에 들어있던 파일들을 전부 해체해서 쉽게 사용할 수 있게 볼 수 있습니다.

#이것을 csv로 저장할려면

df_long.to_csv("./data/long.csv", index = False)
df_lat.to_csv("./data/lat.csv", index = False)
df_swdn.to_csv("./data/swdn.csv", index = False)

#이렇게 저장 하면 됩니다. 코드중에 index = False를 쓰지 않으면 index가 추가로 생성되니까 잊지 말아 주세요
