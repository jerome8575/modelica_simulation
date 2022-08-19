from modelicagym.environment import ModelicaBaseEnv, FMIStandardVersion, FMI2CSEnv, FMI2MEEnv
import logging
from datetime import datetime


import matplotlib.pyplot as plt
import pandas as pd
import os
import gym
from pyfmi import load_fmu
import pyfmi.fmi as fmi

import json
import numpy as np
import math
from ControlCore.agents.RTUBangBangModelica import RTUBangBangAgent     # Base class to inherit from
from ControlCore.agents.opt_agent_modelica import OptAgent
#from ControlCore.agents.gargamel_agent_modelica_MILP import GargamelAgent # Base class to inherit from

logger = logging.getLogger(__name__)

class RunModelicaTask():
    def __init__(self): 
        print("### Run Modelica Task Created")  

    def plot_df(self, df2):

        fig = plt.figure()
        plt.clf()
        plt.plot(np.arange(0,len(df2))/12., df2['yRooTem1'], label='Zone 1 T')
        plt.plot(np.arange(0,len(df2))/12., df2['yRooTem2'], label='Zone 2 T')
        plt.plot(np.arange(0,len(df2))/12., df2['yRooTem3'], label='Zone 3 T')
        plt.plot(np.arange(0,len(df2))/12., df2['yRooTem4'], label='Zone 4 T')
        plt.plot(np.arange(0,len(df2))/12., df2['yRooTem5'], label='Zone 5 T')
        plt.plot(np.arange(0,len(df2))/12., df2['temp_air'], label = 'OAT')
        plt.plot(np.arange(0,len(df2))/12., df2['uHeaCoiStg1']-df2['uCooCoiStg1'], label = 'heat/cool 1')
        plt.plot(np.arange(0,len(df2))/12., df2['uHeaCoiStg2']-df2['uCooCoiStg2'], label = 'heat/cool 2')
        plt.plot(np.arange(0,len(df2))/12., df2['uHeaCoiStg3']-df2['uCooCoiStg3'], label = 'heat/cool 3')
        plt.plot(np.arange(0,len(df2))/12., df2['uHeaCoiStg4']-df2['uCooCoiStg4'], label = 'heat/cool 4')
        plt.plot(np.arange(0,len(df2))/12., df2['uHeaCoiStg5']-df2['uCooCoiStg5'], label = 'heat/cool 5')

        plt.ylim(-10, 30)
        plt.title("Gargamel Controller")
        plt.axhline(y=23, color='r')
        plt.axhline(y=21, color='r')
        plt.axhline(y=26, color='b')
        plt.axhline(y=18, color='b')
        plt.legend()
        plt.savefig('demo_fig.png')

    def run_modelica(self, sim_duration_seconds):
        #config file can be customized
        #below Modelica FMU model is loaded, and used to complete config

        #NOTE: assume scientific units m/kg/s/K...   
        # degC = Kelvin -273.15 

        #path to FMU
        model_path = '/opt/ai/Modelica/modelicagym/Models_w_example_scripts/five_zone_five_rtus/five_zones_five_rtus.fmu'

        '''
        Control points for each zone (there are 5 zones):
        1)'uFan1' - Fan control for zone 1. Continuous on [0,1].

        2)'uEco1' - Economizer damper position for zone 1. Continuous on [0,1]. 
                0 = 0% outdoor air, 100% return air
                1 = 100% outdoor air, 0% return air
                If do not want to use this as control point, set it to fixed value.  

        3)'uHeaCoiStg1 - Heating coil control point for zone 1: 
                    1 = Heating stage 1
                    2 = Heating stage 2

        3)'uCooCoiStg1 - Cooling coil control point for zone 1: 
                    1 = Cooing stage 1
                    2 = Cooling stage 2
        '''


        #load FMU - this is just to get inputs, outputs, and variables. Will load simulation with this info.
        model = load_fmu(model_path, log_level=4)

        #get all inputs, outputs, and variables
        inputs= list(model.get_input_list().keys())
        outputs= list(model.get_output_list().keys())
        variables=list(model.get_model_variables().keys())

        #set up config. 
        #NOTE: model input names defines the control points, including the order of the list to pass
        config = {
            'model_path' : model_path,
            'model_input_names': ['uFan1', 'uEco1', 'uHeaCoiStg1','uCooCoiStg1','uFan2', 'uEco2', 'uHeaCoiStg2', 'uCooCoiStg2','uFan3', 'uEco3', 'uHeaCoiStg3', 'uCooCoiStg3', 'uFan4', 'uEco4', 'uHeaCoiStg4', 'uCooCoiStg4', 'uFan5', 'uEco5', 'uHeaCoiStg5', 'uCooCoiStg5'] ,
            'model_output_names': outputs,
            'model_parameters': 
                {'WeaFilNam' : "/opt/ai/Weather_files/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos",  #enter .mos file. need .epw file with same base name in same folder
                'fixedSeed' : 2524521111,  #
                'hvac1.QHea_flow_nominal' : 4500,  #W
                'hvac2.QHea_flow_nominal' : 4500,  #W
                'hvac3.QHea_flow_nominal' : 4500,  #W
                'hvac4.QHea_flow_nominal' : 4500,  #W
                'hvac5.QHea_flow_nominal' : 4500,  #W
                'T_init': 31  #deg C, initial zone temp for all zones
                },  
            'time_step_s': 900, #this is is seconds, 300 sec=5 mins
            'simulation_start_time_h' : 24  ,  #measured in hours from jan 1 at midnight
            'simulation_duration_h' : 24,  #hours
            'wf_horizon_t_steps' : 24  # number of time steps for weather forecast
        }


        #declare simulation object if Co-Simulation
        simulation = FMI2CSEnv(config=config)


        hvac_dict = {'Temp_degC'  : ['yRooTem1','yRooTem2','yRooTem3','yRooTem4','yRooTem5'],
                      'Fans'       : ['uFan1','uFan2','uFan3','uFan4','uFan5'],  
                      'Economizer' : ['uEco1','uEco2','uEco3','uEco4','uEco5'],
                      'Heating_Stg': ['uHeaCoiStg1','uHeaCoiStg2','uHeaCoiStg3','uHeaCoiStg4','uHeaCoiStg5'],
                      'Cooling_Stg': ['uCooCoiStg1','uCooCoiStg2','uCooCoiStg3','uCooCoiStg4','uCooCoiStg5'],
                      'temp_air'   : 'temp_air'}
        # define agent

        # agent = RTUBangBangAgent(hvac_dict=hvac_dict, controls_list=config['model_input_names'])

        # define temperature bounds

        low_occ =22
        high_occ=25
        low_unocc =15
        high_unocc=26

        T_min_horizon = [low_unocc] * 28 + [low_occ] * 44 + [low_unocc] * 50
        T_max_horizon = [high_unocc] * 28 + [high_occ] * 44 + [high_unocc] * 50


        agent = OptAgent(name='Opt', hvac_dict=hvac_dict, T_min_horizon=T_min_horizon, T_max_horizon=T_max_horizon)

        agent.now = simulation.time
        
        num_steps = math.ceil(sim_duration_seconds/float(simulation.tau))

        for i in range(num_steps):#simulation.num_time_steps

            #tell the agent the time
            agent.now = simulation.time

            #get action from agent
            action=agent.apply_policy(simulation.ts_data, i)

            simulation.step_w_ts_data(action=action)
            
            df_temp_feedback = simulation.ts_data.loc[[simulation.ts_data[["yRooTem1"]].last_valid_index()], ["yRooTem1", "yRooTem2", "yRooTem3", "yRooTem4", "yRooTem5"]]
            df_temp_feedback.to_pickle("df_temp_feedback")

            #save & plot

        # save sim data
        simulation.ts_data.to_csv('sim_data/test_opt24_hours.csv')

if __name__ == "__main__":

    runModelicaTask = RunModelicaTask()

    #set simulation for one day: 
    seconds_per_day = 60*60*24
    days=1
    sim_duration_seconds = days*seconds_per_day

    runModelicaTask.run_modelica(sim_duration_seconds)