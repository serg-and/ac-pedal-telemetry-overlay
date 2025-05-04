import ac, acsys

import os
import sys
import platform

# Import Assetto Corsa shared memory library.
# It has a dependency on ctypes, which is not included in AC python version.
# Point to correct ctypes module based on platform architecture.
# First, get directory of the app, then add correct folder to sys.path.
app_dir = os.path.dirname(__file__)

if platform.architecture()[0] == "64bit":
    sysdir = os.path.join(app_dir, 'dll', 'stdlib64')
else:
    sysdir = os.path.join(app_dir, 'dll', 'stdlib')
# Python looks in sys.path for modules to load, insert new dir first in line.
sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

from _telemetry_overlay.lib.sim_info import info


class TelemetryData:
    car_id = 0
    replay_time_multiplier = 0
    throttle = 0
    brake = 0
    clutch = 0
    handbrake = 0
    steering = 0
    steering_norm = 0.5
    ffb = 0
    gx_values = []
    gz_values = []
    max_x = 2.8
    max_z = 2.8
    gear_str = 'N'
    speed_kph = 0
    speed_mph = 0

    def __init__(self, IS_CSP, config):
        self.IS_CSP = IS_CSP
        self.config = config
        self.update_globals()
        self.update_telemetry()
    
    def update_globals(self):
        """Update the data required for telemetry"""
        self.car_id = ac.getFocusedCar()
        self.replay_time_multiplier = info.graphics.replayTimeMultiplier
    
    def update_telemetry(self):
        """Update telemetry data"""
        self.throttle = ac.getCarState(self.car_id, acsys.CS.Gas)
        self.brake = ac.getCarState(self.car_id, acsys.CS.Brake)
        self.clutch = 1 - ac.getCarState(self.car_id, acsys.CS.Clutch)
        self.ffb = ac.getCarState(self.car_id, acsys.CS.LastFF)
        self.steering = ac.getCarState(self.car_id, acsys.CS.Steer)
        self.steering_norm = min(
            max(
                0.5 + (self.steering / self.config.steering_sensitivity) * -1,
                0.0
            ),
            1.0
        )

        if self.IS_CSP:
            self.handbrake = ac.ext_getHandbrake(self.car_id)
        
        g = ac.getCarState(self.car_id, acsys.CS.AccG)
        while len(self.gx_values) >= self.config.denoise_g: self.gx_values.pop(0)
        while len(self.gz_values) >= self.config.denoise_g: self.gz_values.pop(0)
        self.gx_values.append(min(max(g[0] * -1, self.max_x * -1.1), self.max_x * 1.1))
        self.gz_values.append(min(max(g[2] * -1, self.max_z * -1.1), self.max_z * 1.1))

        gear = ac.getCarState(self.car_id, acsys.CS.Gear)
        if gear == 0:
            self.gear_str = 'R'
        elif gear == 1:
            self.gear_str = 'N'
        else:
            self.gear_str = str(gear - 1)

        self.speed_kph = ac.getCarState(self.car_id, acsys.CS.SpeedKMH)
        self.speed_mph = ac.getCarState(self.car_id, acsys.CS.SpeedMPH)
        
    def get_gx(self):
        if not len(self.gx_values):
            return 0.5
        
        avg_x = sum(self.gx_values) / len(self.gx_values)
        if abs(avg_x) > self.max_x: self.max_x = abs(avg_x)

        return 0.5 + avg_x / (self.max_x * 2)
    
    def get_gz(self):
        if not len(self.gz_values):
            return 0.5
        
        avg_z = sum(self.gz_values) / len(self.gz_values)
        if abs(avg_z) > self.max_z: self.max_z = abs(avg_z)

        return 0.5 + avg_z / (self.max_z * 2)
