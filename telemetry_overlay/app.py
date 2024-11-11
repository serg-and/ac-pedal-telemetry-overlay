import ac, acsys

from config import Config
from data import TelemetryData
from utils import console, console_exception
from widgets import ACGraph, CSPGraph


class App:
    def __init__(self):
        self.IS_CSP = hasattr(ac, 'ext_createRenderTarget')
        self.update_ref = {'timer': 0, 'timeout': 0}
        self.update_low_freq_ref = {'timer': 0, 'timeout': 0.1} # update low priority data every 0.1s
        self.ac_graph_traces = {
            'throttle': None,
            'brake': None,
            'clutch': None,
            'steering': None,
            'gx': None,
            'gz': None,
            'handbrake': None,
        }

    def load_main(self):
        self.config = Config()
        self.telemetry = TelemetryData(self.config)

        self.app_window = ac.newApp("Telemetry Overlay")
        ac.setTitle(self.app_window, "")
        ac.drawBorder(self.app_window, 0)
        ac.setBackgroundOpacity(self.app_window, 0.0)
        ac.setIconPosition(self.app_window, 0, -10000)

        from settings import SettingsWindow
        self.settings = SettingsWindow(self)

        self.toggle_settings_button = ac.addButton(self.app_window, "")
        ac.setPosition(self.toggle_settings_button, 0, 0)
        ac.setBackgroundOpacity(self.toggle_settings_button, 0)
        ac.drawBorder(self.toggle_settings_button, 0)
        self._on_toggle_settings = lambda *args: self.settings.set_open(True) if self.config.open_settings_click else None
        ac.addOnClickedListener(self.toggle_settings_button, self._on_toggle_settings)

        self.ac_graph = None
        self.csp_graph = None
        if self.IS_CSP:
            self.csp_graph = CSPGraph(self.config.app_width, 0, 0, self.config.app_height, self.config.trace_size)
            
            # fallback to traditional graph incase the CSP graph fails
            if not self.csp_graph.setup():
                self.IS_CSP = False
                self.csp_graph = None
                console('Falling back to traditional AC graph')
        
        if not self.IS_CSP:
            self.ac_graph = ACGraph(
                window=self.app_window,
                y=0,
                x=0,
                width=self.config.app_width,
                height=self.config.app_height,
                trace_width=self.config.trace_size,
                opacity=self.config.opacity
            )
            self.ac_graph.setup()
        
        self.throttle_label = ac.addLabel(self.app_window, '')
        self.brake_label = ac.addLabel(self.app_window, '')
        self.clutch_label = ac.addLabel(self.app_window, '')
        self.handbrake_label = ac.addLabel(self.app_window, '')

        try:
            curr_dir = __file__.split('\\')[0:-1]
            curr_dir.append('img\\telemetry-label.png')
            telemetry_label_path = '\\'.join(curr_dir)
            self.telemetry_label_texture = ac.newTexture(telemetry_label_path)
            if self.telemetry_label_texture == -1:
                self.telemetry_label_texture = None
        except Exception as e:
            self.telemetry_label_texture = None
            console_exception(e, 'Failed to load label texture', True)

        self.apply_config()

    def apply_config(self):
        self.window_with = self.config.app_width + self.config.padding * 2
        self.window_height = self.config.app_height + self.config.padding * 2
        self.show_bars = self.config.show_throttle_bar or self.config.show_brake_bar or self.config.show_clutch_bar or self.config.show_handbrake_bar
        if self.show_bars:
            bars = 0
            if self.config.show_throttle_bar: bars += 1
            if self.config.show_brake_bar: bars += 1
            if self.config.show_clutch_bar: bars += 1
            if self.config.show_handbrake_bar: bars += 1
            self.window_with += bars * (self.config.bar_width + 8) + 2
        
        self.graph_origin_x = self.config.padding
        self.graph_origin_y = self.config.padding

        self.label_width = 0
        if self.config.show_telemetry_label:
            self.label_width = round(258 / 1250 * self.window_height)
            self.window_with += self.label_width + 6
            self.graph_origin_x += self.label_width + 6

        labels = [
            (self.throttle_label, self.config.show_throttle_bar),
            (self.brake_label, self.config.show_brake_bar),
            (self.clutch_label, self.config.show_clutch_bar),
            (self.handbrake_label, self.config.show_handbrake_bar),
        ]
        offset = 1
        for label, enabled in labels:
            if not self.config.show_bar_value or not enabled:
                # hide label if not enabled
                ac.setText(label, '')
                continue

            ac.setPosition(label, self.graph_origin_x + self.config.app_width + 2 + offset * (self.config.bar_width + 8), self.graph_origin_y - self.config.bar_width * 0.3)
            ac.setFontAlignment(label, 'right')
            ac.setFontSize(label, self.config.bar_width)
            offset += 1

        ac.setSize(self.app_window, self.window_with, self.window_height)
        ac.setBackgroundOpacity(self.app_window, 0)

        # left side of the main window is clickable for settings
        ac.setSize(self.toggle_settings_button, self.config.app_width / 2, self.config.app_height)

        self.update_ref['timeout'] = 1 / self.config.sample_rate

        if self.IS_CSP:
            self.csp_graph.x = self.graph_origin_x
            self.csp_graph.y = self.graph_origin_y
            self.csp_graph.width = self.config.app_width
            self.csp_graph.height = self.config.app_height
            self.csp_graph.trace_width = self.config.trace_size
            self.csp_graph.setup()
        else:
            self.ac_graph.x = self.graph_origin_x
            self.ac_graph.y = self.graph_origin_y
            self.ac_graph.width = self.config.app_width
            self.ac_graph.height = self.config.app_height
            self.ac_graph.trace_width = self.config.trace_size
            self.ac_graph.opacity = self.config.opacity
            self.ac_graph.setup()

            if self.config.show_gz and not self.ac_graph_traces['gz']:
                self.ac_graph_traces['gz'] = self.ac_graph.add_trace(self.config.gz_color)
            if self.config.show_gx and not self.ac_graph_traces['gx']:
                self.ac_graph_traces['gx'] = self.ac_graph.add_trace(self.config.gx_color)
            if self.config.show_steering and not self.ac_graph_traces['steering']:
                self.ac_graph_traces['steering'] = self.ac_graph.add_trace(self.config.steering_color)
            if self.config.show_clutch and not self.ac_graph_traces['clutch']:
                self.ac_graph_traces['clutch'] = self.ac_graph.add_trace(self.config.clutch_color)
            if self.config.show_throttle and not self.ac_graph_traces['throttle']:
                self.ac_graph_traces['throttle'] = self.ac_graph.add_trace(self.config.throttle_color)
            if self.config.show_brake and not self.ac_graph_traces['brake']:
                self.ac_graph_traces['brake'] = self.ac_graph.add_trace(self.config.brake_color)
            if self.config.show_handbrake and not self.ac_graph_traces['handbrake']:
                self.ac_graph_traces['handbrake'] = self.ac_graph.add_trace(self.config.handbrake_color)

    def on_update(self, dt):
        self.update_ref['timer'] += dt
        self.update_low_freq_ref['timer'] += dt

        # update telemetry
        if self.update_ref['timer'] >= self.update_ref['timeout'] and self.telemetry.replay_time_multiplier != 0:
            prev_throttle = self.telemetry.throttle
            prev_brake = self.telemetry.brake
            prev_clutch = self.telemetry.clutch
            prev_steering = self.telemetry.steering
            prev_gx = self.telemetry.get_gx()
            prev_gz = self.telemetry.get_gz()
            prev_handbrake = self.telemetry.handbrake

            self.update_ref['timer'] = 0
            self.telemetry.update_telemetry()

            if self.show_bars and self.config.show_bar_value:
                bars = [
                    (self.config.show_throttle_bar, self.throttle_label, self.telemetry.throttle),
                    (self.config.show_brake_bar, self.brake_label, self.telemetry.brake),
                    (self.config.show_clutch_bar, self.clutch_label, self.telemetry.clutch),
                    (self.config.show_handbrake_bar, self.handbrake_label, self.telemetry.handbrake),
                ]
                for enabled, label, value in bars:
                    if enabled:
                        rounded = round(value * 100)
                        ac.setText(label, '00' if rounded == 100 else str(rounded))

            if self.IS_CSP:
                values = []
                if self.config.show_gz:
                    values.append((prev_gz, self.telemetry.get_gz(), self.config.gz_color))
                if self.config.show_gx:
                    values.append((prev_gx, self.telemetry.get_gx(), self.config.gx_color))
                if self.config.show_steering:
                    values.append((prev_steering, self.telemetry.steering, self.config.steering_color))
                if self.config.show_clutch:
                    values.append((prev_clutch, self.telemetry.clutch, self.config.clutch_color))
                if self.config.show_handbrake:
                    values.append((prev_handbrake, self.telemetry.handbrake, self.config.handbrake_color))
                if self.config.show_throttle:
                    values.append((prev_throttle, self.telemetry.throttle, self.config.throttle_color))
                if self.config.show_brake:
                    values.append((prev_brake, self.telemetry.brake, self.config.brake_color))
                
                self.csp_graph.add_values(values)
            else:
                if self.ac_graph_traces['brake']:
                    self.ac_graph_traces['brake'].add_value(self.telemetry.brake)
                if self.ac_graph_traces['throttle']:
                    self.ac_graph_traces['throttle'].add_value(self.telemetry.throttle)
                if self.ac_graph_traces['clutch']:
                    self.ac_graph_traces['clutch'].add_value(self.telemetry.clutch)
                if self.ac_graph_traces['steering']:
                    self.ac_graph_traces['steering'].add_value(self.telemetry.steering)
                if self.ac_graph_traces['gz']:
                    self.ac_graph_traces['gz'].add_value(self.telemetry.get_gz())
                if self.ac_graph_traces['gx']:
                    self.ac_graph_traces['gx'].add_value(self.telemetry.get_gx())
                if self.ac_graph_traces['handbrake']:
                    self.ac_graph_traces['handbrake'].add_value(self.telemetry.handbrake)
        
        # low priorty updates
        # low frequency to reduce load
        if self.update_low_freq_ref['timer'] >= self.update_low_freq_ref['timeout']:
            self.update_low_freq_ref['timer'] = 0
            self.telemetry.update_globals()

            # Window opacity is reset on drag, set to correct value
            ac.setBackgroundOpacity(self.app_window, self.config.opacity)

            if self.config.update_cfg:
                self.config.update_cfg = False
                self.config.save()

    def on_render(self, dt):
        if self.IS_CSP:
            ac.glColor4f(0.25, 0.25, 0.25, self.config.opacity)
            ac.glQuad(self.graph_origin_x, self.graph_origin_y, self.config.app_width, self.config.app_height)

        if self.config.show_telemetry_label and self.telemetry_label_texture:
            ac.glColor4f(1, 1, 1, 1)
            ac.glQuadTextured(0, 0, self.label_width, self.window_height, self.telemetry_label_texture)

        if self.config.show_graph_lines:
            for offset in [0.25, 0.5, 0.75]:
                y = self.config.app_height * offset + self.graph_origin_y
                ac.glBegin(acsys.GL.Lines)
                ac.glColor4f(0.42, 0.42, 0.42, min(0.3 + self.config.opacity, 1))
                ac.glVertex2f(self.graph_origin_x, y)
                ac.glVertex2f(self.config.app_width + self.graph_origin_x, y)
                ac.glEnd()
    
        if self.csp_graph:
            self.csp_graph.render()

        if self.show_bars:
            bar_height = self.config.app_height
            bar_start_y = self.graph_origin_y
            if self.config.show_bar_value:
                bar_height -= self.config.bar_width * 1.1
                bar_start_y += self.config.bar_width * 1.1
    
            bars = [
                (self.config.show_throttle_bar, self.telemetry.throttle, self.config.throttle_color),
                (self.config.show_brake_bar, self.telemetry.brake, self.config.brake_color),
                (self.config.show_clutch_bar, self.telemetry.clutch, self.config.clutch_color),
                (self.config.show_handbrake_bar, self.telemetry.handbrake, self.config.handbrake_color),
            ]
            
            for i, (value, color) in enumerate([(value, color) for enabled, value, color in bars if enabled]):
                x = self.graph_origin_x + self.config.app_width + i * (self.config.bar_width + 8) + 10
                ac.glColor4f(0.25, 0.25, 0.25, self.config.opacity)
                ac.glQuad(x, bar_start_y, self.config.bar_width, bar_height)
                height = bar_height * value
                ac.glColor3f(color[0], color[1], color[2])
                ac.glQuad(x, bar_start_y + bar_height - height, self.config.bar_width, height)
        
        # Window opacity is reset on drag, set to correct value
        if self.settings.open:
            ac.setBackgroundOpacity(self.settings.window, 0.8)
