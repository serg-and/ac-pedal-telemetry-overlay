import ac
import acsys

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

from lib.sim_info import info


class TelemetryData:
    car_id = 0
    replay_time_multiplier = 0
    throttle = 0
    brake = 0
    clutch = 0

    def __init__(self):
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
