import pandas as pd
import numpy as np
#import streamlit as str
import seaborn as sns
import matplotlib.pyplot as plt


# read csv and build dataframe, remove nan rows

data = pd.read_csv("sim_data/test_opt_2month.csv")
df = data.dropna(axis=0, how='any')

# keep relevant columns

df = df[['temp_air', 'uHeaCoiStg1', 'uHeaCoiStg2', 'uHeaCoiStg3', 'uHeaCoiStg4', 'uHeaCoiStg5', 'yRooTem1', 'yRooTem2', 'yRooTem3', 'yRooTem4', 'yRooTem5']]

# delta T

df["dTRoo1"] = df["yRooTem1"].diff()
df["dTRoo2"] = df["yRooTem2"].diff()
df["dTRoo3"] = df["yRooTem3"].diff()
df["dTRoo4"] = df["yRooTem4"].diff()
df["dTRoo5"] = df["yRooTem5"].diff()

df["TintToutDiff"] = df['yRooTem1'] - df['temp_air']


dx = 10
T_int_T_ext_bins = np.linspace(10,40,dx)
T_int_T_ext_center = T_int_T_ext_bins[:-1] + (T_int_T_ext_bins[1]-T_int_T_ext_bins[0])/2
T_int_T_ext_labels = [str(i) for i in T_int_T_ext_center]
df["T_int-T_ext_bin"] = pd.cut(df["TintToutDiff"], T_int_T_ext_bins, labels = T_int_T_ext_labels)

dy = 10
heating_bins = np.linspace(-1,2,dy)
heating_center = heating_bins[:-1] + (heating_bins[1]-heating_bins[0])/2
heating_labels = [str(i) for i in heating_center]
df["heating_total_bin"] = pd.cut(df["uHeaCoiStg1"], heating_bins, labels = heating_labels)

df_pivot_mean = pd.pivot_table(df, values="dTRoo1", index="heating_total_bin", columns="T_int-T_ext_bin", dropna=False, aggfunc="mean")
df_pivot_count = pd.pivot_table(df, values="dTRoo1", index="heating_total_bin", columns="T_int-T_ext_bin", dropna=False, aggfunc="count")


# Direction based on mean
x, y = np.meshgrid(T_int_T_ext_center, heating_center)
v = df_pivot_mean.values
u = df_pivot_mean.max().max()

# Colour based on count
# c = df_pivot_count.values / df_pivot_count.max().max()
# cbar_title = "Relative Count"
c = np.log(df_pivot_count.values / df_pivot_count.max().max() + 0.0001)
cbar_title = "Log Relative Count"

# Quiver plot
plt.figure(figsize=(10,8))
plt.quiver(x, y, u, v, c, cmap=plt.cm.viridis)
plt.xlabel("T_{int} - T_{ext} (larger means colder)")
plt.ylabel("Heating")
cbar = plt.colorbar()
cbar.ax.set_title(cbar_title, fontsize=10)
# plt.xlim(10, 45)
# plt.ylim(-5, 110)
plt.title("Rate of change of temperature")
plt.savefig('delta_T_2.png')

