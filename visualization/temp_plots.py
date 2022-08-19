
from re import X
from time import time
import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import altair as al


# read csv and build dataframe, remove nan rows

data = pd.read_csv("results/opt_controller_jan_2.csv", index_col=0)
bbdata = pd.read_csv("results/banbangjan2.csv", index_col=0)

df = data.dropna(axis=0, how='any')
bbdf = bbdata.dropna(axis=0, how='any')

# keep relevant columns

df = df[['temp_air', 'uHeaCoiStg1', 'uHeaCoiStg2', 'uHeaCoiStg3', 'uHeaCoiStg4', 'uHeaCoiStg5', 'yRooTem1', 'yRooTem2', 'yRooTem3', 'yRooTem4', 'yRooTem5', 'ySumEnergy']]
bbdf = bbdf[['temp_air', 'uHeaCoiStg1', 'uHeaCoiStg2', 'uHeaCoiStg3', 'uHeaCoiStg4', 'uHeaCoiStg5', 'yRooTem1', 'yRooTem2', 'yRooTem3', 'yRooTem4', 'yRooTem5', 'ySumEnergy']]

# deadband settings
##7am-6pm

low_occ =22
high_occ=25
low_unocc =15
high_unocc=26

df['T_min'] = [low_unocc] * 28 + [low_occ] * 44 + [low_unocc] * 25
df['T_max'] = [high_unocc] * 28 + [high_occ] * 44 + [high_unocc] * 25


def summary_streamlit(df):

    st.set_page_config(layout="wide")

    st.header("Temperatures")

    num_zones = 5

    # plot temperatures
    for i in range(num_zones):

        temp_df = pd.DataFrame({
            "Temperature": df['yRooTem' + str(i+1)],
            "Classical controller": bbdf['yRooTem' + str(i+1)],
            "T min": df['T_min'],
            "T max": df['T_max']
        })
        scale = al.Scale(domain=['Temperature', "Classical controller", 'T min', 'T max'], range=[
                                'black', 'gray', '#00008B', '#8B0000'])
        data = temp_df.reset_index().melt('index')
        temp_chart = al.Chart(data, height=200).mark_line().encode(
            al.X('index:T', axis=al.Axis(title="Time", grid=False, format = ("%X"))),
            al.Y('value', scale=al.Scale(zero=False),
                    axis=al.Axis(title="Temperature", grid=False)),
            color=al.Color('variable', scale=scale),
            strokeDash=al.condition(
                al.datum.variable == 'Classical controller',
                # dashed line: 5 pixels  dash + 5 pixels space
                al.value([5, 5]),
                al.value([0]),  # solid line
            )
        )

        
        st.altair_chart(temp_chart, use_container_width=True)

    # plot instantaneous power calls
    st.header("Power")

    df['instant_power'] = df['uHeaCoiStg1'] + df['uHeaCoiStg2'] + df['uHeaCoiStg3'] + df['uHeaCoiStg4'] + df['uHeaCoiStg5']
    df['instant_power'] = df['instant_power'] * 2250
    bbdf['instant_power'] = bbdf['uHeaCoiStg1'] + bbdf['uHeaCoiStg2'] + bbdf['uHeaCoiStg3'] + bbdf['uHeaCoiStg4'] + bbdf['uHeaCoiStg5']
    bbdf['instant_power'] = bbdf['instant_power'] * 2250

    power_peaks_df = pd.DataFrame({
        "power": df.loc[:, "instant_power"],
        "Classical controller": bbdf.loc[:, "instant_power"]
    })

    scale = al.Scale(domain=['power', "Classical controller"], range=[
                        'black', 'gray'])
    data = power_peaks_df.reset_index().melt('index')
    power_peaks_chart = al.Chart(data).mark_line().encode(
        al.X('index:T', axis=al.Axis(title="Time", grid=False, format = ("%X"))),
        al.Y('value', scale=al.Scale(zero=False),
                axis=al.Axis(title="Power", grid=False)),
        color=al.Color('variable', scale=scale),
        strokeDash=al.condition(
                al.datum.variable == 'Classical controller',
                # dashed line: 5 pixels  dash + 5 pixels space
                al.value([5, 5]),
                al.value([0]),  # solid line
            )
    )
    st.altair_chart(power_peaks_chart, use_container_width=True)

    # plot energy
    st.header("Energy")

    energy_df = pd.DataFrame({
        "Energy": df.loc[:, "ySumEnergy"],
        "Classical controller": bbdf.loc[:, "ySumEnergy"]
    })

    scale = al.Scale(domain=['Energy', "Classical controller"], range=[
                        'black', 'gray'])
    data = energy_df.reset_index().melt('index')
    energy_chart = al.Chart(data).mark_line().encode(
        al.X('index:T', axis=al.Axis(title="Time", grid=False, format = ("%X"))),
        al.Y('value', scale=al.Scale(zero=False),
                axis=al.Axis(title="Energy", grid=False)),
        color=al.Color('variable', scale=scale),
        strokeDash=al.condition(
                al.datum.variable == 'Classical controller',
                # dashed line: 5 pixels  dash + 5 pixels space
                al.value([5, 5]),
                al.value([0]),  # solid line
            )
    )
    st.altair_chart(energy_chart, use_container_width=True)
    


summary_streamlit(df)