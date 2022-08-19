
import pandas as pd
import numpy as np
from pyparsing import alphas
#import streamlit as str
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

SIM_TRAINING_DATA = "sim_data/2monthbangbang.csv"

# read csv and build dataframe, remove nan rows
data = pd.read_csv(SIM_TRAINING_DATA, index_col=0)
df = data.dropna(axis=0, how='any')

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

#delta_T = []
for zone in range(5):
    #zone_delta_T = []
    for ctrl in range(3):
        ctrl_df = df.loc[(df["uHeaCoiStg" + str(zone + 1)]) == ctrl]
        d = ctrl_df.loc[:, "dTRoo" + str(zone + 1)]
        d.plot.hist()
        plt.savefig("deltaT_dist/deltaT_distRoo" + str(zone + 1) + "Ctrl" + str(ctrl) + ".png")
        plt.cla()
    #delta_T.append(zone_delta_T)
