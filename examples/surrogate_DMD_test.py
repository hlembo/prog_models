# Copyright © 2021 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration.  All Rights Reserved.

"""
Example demonstrating and benchmarking the DMD surrogate model 

Compares two simulations: 1) Full model, 2) DMD approximation in next_state 
"""

from prog_models.models.battery_electrochem import DMDModel_dx, BatteryElectroChemEOD
from statistics import mean
from numpy.random import normal
from timeit import timeit
import matplotlib.pyplot as plt

def run_example_Full(): 
    batt = BatteryElectroChemEOD()
    batt.parameters['process_noise'] = 0

    ## Define Loading Profile
    def future_loading(t, x=None):
        if (t < 500):
            i = 3
        elif (t < 1000):
            i = 1
        elif (t < 2000):
            i = 2
        else:
            i = 4
        return {'i': i}

    # Simulation Options
    options = {
        'save_freq': 1,  # Frequency at which results are saved
        'dt': 1  # Timestep
    }
    
    ## Simulate to Threshold 
    # simulated_results = batt.simulate_to_threshold(future_loading, **options)

    ## Simulate to specitic time 
    # simulated_results = batt.simulate_to(600, future_loading, **options)

    ## More rigorous benchmarking
    print('Benchmarking:')
    def sim_Full():  
        simulated_results = batt.simulate_to_threshold(future_loading, **options)
    timeFull = timeit(sim_Full, number=100)

    # Print results
    print('Simulation Time from Full: {} ms/sim'.format(timeFull*2))


def run_example_DMD_dx(): 
    batt = DMDModel_dx()

    ## Define Loading Profile 
    def future_loading(t, x=None):
        if (t < 500):
            i = 3
        elif (t < 1000):
            i = 1
        elif (t < 2000):
            i = 2
        else:
            i = 4
        return {'i': i}

    # Simulation Options
    options = {
        'save_freq': 1,  # Frequency at which results are saved
        'dt': 1  # Timestep
    }

    ## Simulate to Threshold 
    # simulated_results = batt.simulate_to_threshold(future_loading, **options)

    ## Simulate to specific time 
    # simulated_results = batt.simulate_to(600,future_loading,**options)

    ## More rigorous benchmarking
    print('Benchmarking:')
    def sim_Full():  
        simulated_results = batt.simulate_to_threshold(future_loading, **options)
    timeFull = timeit(sim_Full, number=100)

    # Print results
    print('Simulation Time from Full: {} ms/sim'.format(timeFull*2))


# This allows the module to be executed directly 
if __name__ == '__main__':
    # Run Full Simulation:
    # run_example_Full()
    
    # Run DMD approximation in next_state
    run_example_DMD_dx()
    