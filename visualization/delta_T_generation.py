import pandas as pd
import numpy as np
import scipy
from pyparsing import alphas
#import streamlit as str
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

SIM_TRAINING_DATA = "modelica_simulation/sim_data/2monthbangbang.csv"

# read csv and build dataframe, remove nan rows
data = pd.read_csv(SIM_TRAINING_DATA, index_col=0)
df = data.dropna(axis=0, how='any')
start = datetime.datetime(2021, 1, 1, 21, 0, 0)
end = start + datetime.timedelta(hours=3)
df = df.loc[str(start):str(end), :]
# keep relevant columns

df = df[['temp_air', 'uHeaCoiStg1', 'uHeaCoiStg2', 'uHeaCoiStg3', 'uHeaCoiStg4', 'uHeaCoiStg5', 'yRooTem1', 'yRooTem2', 'yRooTem3', 'yRooTem4', 'yRooTem5']]

# generate delta T
df["dTRoo1"] = df["yRooTem1"].diff()
df["dTRoo2"] = df["yRooTem2"].diff()
df["dTRoo3"] = df["yRooTem3"].diff()
df["dTRoo4"] = df["yRooTem4"].diff()
df["dTRoo5"] = df["yRooTem5"].diff()

# T_interior - T_outside
df["TintToutDiff"] = df['yRooTem1'] - df['temp_air']

print(df)

delta_T = []
for zone in range(5):
    zone_delta_T = []
    for ctrl in range(3):
        ctrl_df = df.loc[(df["uHeaCoiStg" + str(zone + 1)]) == ctrl]
        zone_delta_T.append(ctrl_df.loc[:, "dTRoo" + str(zone + 1)].mean())
    delta_T.append(zone_delta_T)

print(delta_T)
    




