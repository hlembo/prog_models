# Copyright © 2021 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration.  All Rights Reserved.

from .. import PrognosticsModel
import numpy as np

def calc_lumped_param(params):
    return {
        'lumped_param': 0.5 * params['rho']* params['cd'] * params['A'] / params['m']
    }


class ThrownObject(PrognosticsModel):
    """
    Simple Non-Linear :term:`model` that similates an object thrown into the air with air resistance

    :term:`Events<event>`: (2)
        | falling: The object is falling
        | impact: The object has hit the ground

    :term:`Inputs/Loading<input>`: (0)

    :term:`States<state>`: (2)
        | x: Position in space (m)
        | v: Velocity in space (m/s)

    :term:`Outputs<output>`: (1)
        | x: Position in space (m)

    Keyword Args
    ------------
        process_noise : Optional, float or Dict[str, float]
          :term:`Process noise<process noise>` (applied at dx/next_state). 
          Can be number (e.g., .2) applied to every state, a dictionary of values for each 
          state (e.g., {'x1': 0.2, 'x2': 0.3}), or a function (x) -> x
        process_noise_dist : Optional, String
          distribution for :term:`process noise` (e.g., normal, uniform, triangular)
        measurement_noise : Optional, float or Dict[str, float]
          :term:`Measurement noise<measurement noise>` (applied in output eqn).
          Can be number (e.g., .2) applied to every output, a dictionary of values for each
          output (e.g., {'z1': 0.2, 'z2': 0.3}), or a function (z) -> z
        measurement_noise_dist : Optional, String
          distribution for :term:`measurement noise` (e.g., normal, uniform, triangular)
        g : Optional, float
            Acceleration due to gravity (m/s^2). Default is 9.81 m/s^2 (standard gravity)
        thrower_height : Optional, float
            Height of the thrower (m). Default is 1.83 m
        throwing_speed : Optional, float
            Speed at which the ball is thrown (m/s). Default is 40 m/s
    """

    inputs = []  # no inputs, no way to control
    states = [
        'x',    # Position (m) 
        'v'    # Velocity (m/s)
        ]
    outputs = [
        'x'     # Position (m)
    ]
    events = [
        'falling',  # Event- object is falling
        'impact'    # Event- object has impacted ground
    ]

    is_vectorized = True

    # The Default parameters. Overwritten by passing parameters dictionary into constructor
    default_parameters = {
        'thrower_height': 1.83,  # m
        'throwing_speed': 40,  # m/s
        'g': -9.81,  # Acceleration due to gravity in m/s^2
        'rho': 1.225, # Air density at sea level 1.225 kg/m^3
        'A': 0.05, # m^2 - Cross sectional area 
        'm': 0.145, # kg - Mass of thing  
        'cd': 0.007, # Coefficient of drag
        'process_noise': 0.0  # amount of noise in each step
    }

    param_callbacks = {
        'rho': [calc_lumped_param],
        'A': [calc_lumped_param],
        'm': [calc_lumped_param],
        'cd': [calc_lumped_param]
    }

    def initialize(self, u=None, z=None):
        return self.StateContainer({
            'x': self.parameters['thrower_height'],  # Thrown, so initial altitude is height of thrower
            'v': self.parameters['throwing_speed']   # Velocity at which the ball is thrown - this guy is a professional baseball pitcher
            })
    
    def next_state(self, x : dict, u : dict, dt : float):
        next_x =  x['x'] + x['v']*dt
        drag_acc = self.parameters['lumped_param'] * x['v']*x['v']
        next_v = x['v'] + (self.parameters['g'] - drag_acc*np.sign(x['v']))*dt
        return self.StateContainer(np.array([
            [next_x],
            [next_v]  # Acceleration of gravity
        ]))

    def output(self, x : dict):
        return self.OutputContainer(np.array([[x['x']]]))

    # This is actually optional. Leaving thresholds_met empty will use the event state to define thresholds.
    #  Threshold = Event State == 0. However, this implementation is more efficient, so we included it
    def threshold_met(self, x : dict) -> dict:
        return {
            'falling': x['v'] < 0,
            'impact': x['x'] <= 0
        }

    def event_state(self, x : dict) -> dict: 
        x_max = x['x'] + np.square(x['v'])/(-self.parameters['g']*2) # Use speed and position to estimate maximum height
        x_max = np.where(x['v'] > 0, x['x'], x_max) # 1 until falling begins
        return {
            'falling': np.maximum(x['v']/self.parameters['throwing_speed'],0),  # Throwing speed is max speed
            'impact': np.maximum(x['x']/x_max,0)  # then it's fraction of height
        }
