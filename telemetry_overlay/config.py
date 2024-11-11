import os
import configparser

from utils import console


class Config:
    """App configuration. Load config upon intialization."""

    def __init__(self):
        self.update_cfg = False
        app_dir = os.path.dirname(__file__)
        self.cfg_file_path = os.path.join(app_dir, "config.ini")
        self.cfg_parser = configparser.ConfigParser(inline_comment_prefixes=";")
        self.set_defaults()
        self.parse_config()
    
    def set_defaults(self, save=False):
        self.show_throttle=True  # Show throttle trace
        self.show_brake=True # Show brake trace
        self.show_clutch=False   # Show clutch trace
        self.show_steering=False    # Show steering trace
        self.show_gx=False  # Show lageral g force trace
        self.show_gz=False  # Show longitudinal g force trace
        self.show_handbrake=False  # Show handbrake trace
        self.show_throttle_bar=False    # Show throttle bar
        self.show_brake_bar=False   # Show brake bar
        self.show_clutch_bar=False  # Show clutch bar
        self.show_handbrake_bar=False  # Show handbrake bar
        self.show_bar_value=False   # Show number value above bar
        self.show_graph_lines=False # Show horizontal graph lines
        self.show_telemetry_label=False # Show temetry label
        self.app_height=100  # App height (Specifies the height of the app in pixels); from 10 to 1000
        self.app_width=300   # App width in pixels; from 10 to 1000
        self.sample_rate=40  # Traces sample rate; from  1 hz to 100 hz
        self.trace_size=2.0  # Trace line thickness; from 1 px to 10 px
        self.opacity=0.5 # App opacity (between 0.0 and 1.0)
        self.denoise_g=5    # Number of measurements to combine to denoise g force traces
        self.padding=0  # Padding around main window
        self.bar_width=10   # Width of bars
        self.open_settings_click = True # Open settings window on clicking left side of the main window
        self.throttle_color=(0.16, 1.0, 0.0, 1.0)    # Color of the throttle trace
        self.brake_color=(1.0, 0.16, 0.0, 1.0)   # Color of the brake trace
        self.clutch_color=(0.16, 1.0, 1.0, 1.0)  # Color of the clutch trace
        self.steering_color=(0.9, 0.9, 0.9, 1.0)  # Color of the steering trace
        self.gx_color=(1.0, 0.9, 0.0, 1.0)  # Color of the lageral g force trace
        self.gz_color=(0.5, 0.0, 0.9, 1.0)  # Color of the longitudinal g force trace
        self.handbrake_color=(0.2, 0.1, 0.7, 1.0)  # Color of the handbrake trace
        
        if save:
            self.save()

    def parse_config(self):
        """Initialize config parser and load config"""
        self.cfg_parser.read(self.cfg_file_path)

        if not self.cfg_parser.has_section('GENERAL'):
            self.cfg_parser.add_section('GENERAL')
                
        # Load attributes from config.
        self.get_bool('GENERAL', 'show_throttle')
        self.get_bool('GENERAL', 'show_brake')
        self.get_bool('GENERAL', 'show_clutch')
        self.get_bool('GENERAL', 'show_steering')
        self.get_bool('GENERAL', 'show_gx')
        self.get_bool('GENERAL', 'show_gz')
        self.get_bool('GENERAL', 'show_handbrake')
        self.get_bool('GENERAL', 'show_throttle_bar')
        self.get_bool('GENERAL', 'show_brake_bar')
        self.get_bool('GENERAL', 'show_clutch_bar')
        self.get_bool('GENERAL', 'show_handbrake_bar')
        self.get_bool('GENERAL', 'show_bar_value')
        self.get_bool('GENERAL', 'show_graph_lines')
        self.get_bool('GENERAL', 'show_telemetry_label')
        self.get_bool('GENERAL', 'open_settings_click')
        self.get_int('GENERAL', 'app_height')
        self.get_int('GENERAL', 'app_width')
        self.get_int('GENERAL', 'sample_rate')
        self.get_int('GENERAL', 'trace_size')
        self.get_int('GENERAL', 'denoise_g')
        self.get_int('GENERAL', 'padding')
        self.get_int('GENERAL', 'bar_width')
        self.get_float('GENERAL', 'opacity')
        self.get_rgba('GENERAL', 'throttle_color')
        self.get_rgba('GENERAL', 'brake_color')
        self.get_rgba('GENERAL', 'clutch_color')
        self.get_rgba('GENERAL', 'steering_color')
        self.get_rgba('GENERAL', 'gx_color')
        self.get_rgba('GENERAL', 'gz_color')
        self.get_rgba('GENERAL', 'handbrake_color')

        # If update_cfg has been triggered (set to True), run save to update file.
        if self.update_cfg:
            self.save()
        

    def save(self):
        """Save config file"""
        console('saving config')

        self.cfg_parser.set('GENERAL', 'show_throttle', str(self.show_throttle))
        self.cfg_parser.set('GENERAL', 'show_brake', str(self.show_brake))
        self.cfg_parser.set('GENERAL', 'show_clutch', str(self.show_clutch))
        self.cfg_parser.set('GENERAL', 'show_steering', str(self.show_steering))
        self.cfg_parser.set('GENERAL', 'show_gx', str(self.show_gx))
        self.cfg_parser.set('GENERAL', 'show_gz', str(self.show_gz))
        self.cfg_parser.set('GENERAL', 'show_handbrake', str(self.show_handbrake))
        self.cfg_parser.set('GENERAL', 'show_throttle_bar', str(self.show_throttle_bar))
        self.cfg_parser.set('GENERAL', 'show_brake_bar', str(self.show_brake_bar))
        self.cfg_parser.set('GENERAL', 'show_clutch_bar', str(self.show_clutch_bar))
        self.cfg_parser.set('GENERAL', 'show_handbrake_bar', str(self.show_handbrake_bar))
        self.cfg_parser.set('GENERAL', 'show_bar_value', str(self.show_bar_value))
        self.cfg_parser.set('GENERAL', 'show_graph_lines', str(self.show_graph_lines))
        self.cfg_parser.set('GENERAL', 'show_telemetry_label', str(self.show_telemetry_label))
        self.cfg_parser.set('GENERAL', 'open_settings_click', str(self.open_settings_click))
        self.cfg_parser.set('GENERAL', 'app_height', str(self.app_height))
        self.cfg_parser.set('GENERAL', 'app_width', str(self.app_width))
        self.cfg_parser.set('GENERAL', 'sample_rate', str(self.sample_rate))
        self.cfg_parser.set('GENERAL', 'opacity', str(self.opacity))
        self.cfg_parser.set('GENERAL', 'trace_size', str(self.trace_size))
        self.cfg_parser.set('GENERAL', 'denoise_g', str(self.denoise_g))
        self.cfg_parser.set('GENERAL', 'padding', str(self.padding))
        self.cfg_parser.set('GENERAL', 'bar_width', str(self.bar_width))

        # serialize rgba tuples
        for rgba in ['throttle_color', 'brake_color', 'clutch_color', 'steering_color', 'gx_color', 'gz_color', 'handbrake_color']:
            value = ','.join([str(int(i * 100)) for i in getattr(self, rgba)])
            self.cfg_parser.set('GENERAL', rgba, value)
        
        
        with open(self.cfg_file_path, 'w') as cfgfile:
            self.cfg_parser.write(cfgfile)


    def get_float(self, section, option):
        try:
            value = self.cfg_parser.getfloat(section, option)
        except:
            value = getattr(self, option)
            self.update_cfg = True
        
        self.__setattr__(option, value)


    def get_bool(self, section, option):      
        try:
            value = self.cfg_parser.getboolean(section, option)
        except:
            value = getattr(self, option)
            self.update_cfg = True
        
        self.__setattr__(option, value)


    def get_int(self, section, option):       
        try:
            value = self.cfg_parser.getint(section, option)
        except:
            try:
                value = int(self.cfg_parser.getfloat(section, option))
            except:
                value = getattr(self, option)
            
            self.update_cfg = True
        
        self.__setattr__(option, value)


    # rgba value are represented as four 0-100 int values saperated by a ","
    def get_rgba(self, section, option):       
        try:
            value = self.cfg_parser.get(section, option)
            values = [int(s) / 100 for s in value.split(',')]
            rgba = (values[0], values[1], values[2], values[3])
        except:
            rgba = getattr(self, option)
            self.update_cfg = True
        
        self.__setattr__(option, rgba)
