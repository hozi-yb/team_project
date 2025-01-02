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

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

power_usage = pd.read_csv("./fa_data/2020-08 시도별 산업용 전력사용량.csv",encoding="euc_kr")
power_usage.columns = ["date","loc_nm","category","unit_pu(kwh/count)","unit_pu(%)"]


print(power_usage.groupby("loc_nm")["강원특별자치도"])