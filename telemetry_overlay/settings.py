import ac

import app
from widgets import Checkbox, ConfirmButton, RGBAInput, Spinner, Tabs


class SettingsWindow:
    def __init__(self, app: app.App):
        self.app = app
        self.open = False
        self._handlers = []

        self.window = ac.newApp("Telemetry Overlay Settings")
        ac.setTitle(self.window, "")
        ac.setVisible(self.window, 0)
        ac.drawBorder(self.window, 0)
        ac.setIconPosition(self.window, 0, -10000)
        ac.setSize(self.window, 530, 390)
        ac.setBackgroundOpacity(self.window, 0.8)
        ac.setVisible(self.window, 0)

        ac.addOnAppActivatedListener(self.window, self._add_handler(lambda *args: self.set_open(True)))
        ac.addOnAppDismissedListener(self.window, self._add_handler(lambda *args: self.set_open(False)))

        close_btn = ac.addButton(self.window, 'close')
        ac.setPosition(close_btn, 470, 358)
        ac.setSize(close_btn, 50, 22)
        ac.drawBorder(close_btn, 0)
        self._on_close = lambda *args: self.set_open(False)
        ac.addOnClickedListener(close_btn, self._on_close)     

        self.tabs = Tabs(
            window=self.window,
            x=10,
            y=10,
            btn_width=75,
            btn_margin=15,
        )
        self.general_tab = self.tabs.add_tab('General')
        self.traces_tab = self.tabs.add_tab('Traces')
        self.inputs_tab = self.tabs.add_tab('Inputs')
        self.wheel_tab = self.tabs.add_tab('Wheel')
        self.reset_tab = self.tabs.add_tab('Reset')
        self.tabs.set_active_tab(0)

        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Width',
                label_top=True,
                label_align='center',
                value=self.app.config.app_width,
                min=10,
                max=1000,
                step=1,
                x=20,
                y=70,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('app_width', value, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Height',
                label_top=True,
                label_align='center',
                value=self.app.config.app_height,
                min=10,
                max=1000,
                step=1,
                x=20,
                y=130,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('app_height', value, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Opacity',
                label_top=True,
                label_align='center',
                value=self.app.config.opacity * 100,
                min=0,
                max=100,
                step=1,
                x=20,
                y=190,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('opacity', value / 100, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Sample rate (Hz)',
                label_top=True,
                label_align='center',
                value=self.app.config.sample_rate,
                min=1,
                max=100,
                step=1,
                x=275,
                y=70,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('sample_rate', value, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Denoise G traces',
                label_top=True,
                label_align='center',
                value=self.app.config.denoise_g,
                min=1,
                max=50,
                step=1,
                x=275,
                y=130,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('denoise_g', value, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Padding',
                label_top=True,
                label_align='center',
                value=self.app.config.padding,
                min=0,
                max=30,
                step=1,
                x=20,
                y=250,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('padding', value, True))
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Trace size',
                label_top=True,
                label_align='center',
                value=self.app.config.trace_size,
                min=1,
                max=10 if self.app.IS_CSP else 5,   # more expensive for non CSP graph
                step=1,
                x=275,
                y=190,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('trace_size', value, True)),
            )
        )
        self.general_tab.mount(
            Spinner(
                window=self.window,
                label='Steering trace sensitivity °',
                label_top=True,
                label_align='center',
                value=self.app.config.steering_sensitivity,
                min=100,
                max=1000,   # more expensive for non CSP graph
                step=1,
                x=275,
                y=250,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('steering_sensitivity', value, True)),
            )
        )
        
        self.general_tab.mount(
            Checkbox(
                window=self.window,
                label='Open settings on window click',
                value=self.app.config.open_settings_click,
                x=20,
                y=300,
                onChange=self._add_handler(
                    lambda *args: self.config_change('open_settings_click', not self.app.config.open_settings_click))
            )
        )
        self.general_tab.mount(
            Checkbox(
                window=self.window,
                label='Horizontal graph lines',
                value=self.app.config.show_graph_lines,
                x=20,
                y=330,
                onChange=self._add_handler(
                    lambda *args: self.config_change('show_graph_lines', not self.app.config.show_graph_lines))
            )
        )
        self.general_tab.mount(
            Checkbox(
                window=self.window,
                label='Telemetry label',
                value=self.app.config.show_telemetry_label,
                x=20,
                y=360,
                onChange=self._add_handler(
                    lambda *args: self.config_change('show_telemetry_label', not self.app.config.show_telemetry_label, True))
            )
        )

        self._create_trace_components('throttle', 65, 'Throttle trace', True)
        self._create_trace_components('brake', 105, 'Brake trace')
        self._create_trace_components('clutch', 145, 'Clutch trace')
        self._create_trace_components('steering', 185, 'Steering trace')
        self._create_trace_components('gx', 225, 'Lateral G')
        self._create_trace_components('gz', 265, 'Longitudinal G')

        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='Throttle bar',
                value=self.app.config.show_throttle_bar,
                x=20,
                y=50,
                onChange=self._add_handler(lambda *args: self.config_change('show_throttle_bar', not self.app.config.show_throttle_bar, True)),
            )
        )
        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='Brake bar',
                value=self.app.config.show_brake_bar,
                x=20,
                y=80,
                onChange=self._add_handler(lambda *args: self.config_change('show_brake_bar', not self.app.config.show_brake_bar, True)),
            )
        )
        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='Clutch bar',
                value=self.app.config.show_clutch_bar,
                x=20,
                y=110,
                onChange=self._add_handler(lambda *args: self.config_change('show_clutch_bar', not self.app.config.show_clutch_bar, True)),
            )
        )
        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='Show input value above bar',
                value=self.app.config.show_bar_value,
                x=20,
                y=150,
                onChange=self._add_handler(lambda *args: self.config_change('show_bar_value', not self.app.config.show_bar_value, True)),
            )
        )
        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='End stop',
                value=self.app.config.pedals_end_stop,
                x=20,
                y=180,
                onChange=self._add_handler(lambda *args: self.config_change('pedals_end_stop', not self.app.config.pedals_end_stop, True)),
            )
        )
        self.inputs_tab.mount(
            Checkbox(
                window=self.window,
                label='Base stop',
                value=self.app.config.pedals_base_stop,
                x=20,
                y=210,
                onChange=self._add_handler(lambda *args: self.config_change('pedals_base_stop', not self.app.config.pedals_base_stop, True)),
            )
        )
        self.inputs_tab.mount(
            Spinner(
                window=self.window,
                label='Bar width',
                label_top=True,
                label_align='center',
                value=self.app.config.bar_width,
                min=1,
                max=50,
                step=1,
                x=275,
                y=65,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('bar_width', value, True))
            )
        )

        self.wheel_tab.mount(
            Checkbox(
                window=self.window,
                label='Show wheel',
                value=self.app.config.show_wheel,
                x=20,
                y=50,
                onChange=self._add_handler(lambda *args: self.config_change('show_wheel', not self.app.config.show_wheel, True)),
            )
        )
        self.wheel_tab.mount(
            Spinner(
                window=self.window,
                label='Wheel thickness',
                label_top=True,
                label_align='center',
                value=self.app.config.wheel_depth,
                min=1,
                max=30,
                step=1,
                x=275,
                y=65,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('wheel_depth', value, True))
            )
        )
        self.wheel_tab.mount(
            Spinner(
                window=self.window,
                label='Wheel width',
                label_top=True,
                label_align='center',
                value=self.app.config.wheel_angle,
                min=1,
                max=40,
                step=1,
                x=275,
                y=125,
                width=235,
                onChange=self._add_handler(lambda value: self.config_change('wheel_angle', value, True))
            )
        )
        if self.app.IS_CSP:
            self.wheel_tab.mount(
                Checkbox(
                    window=self.window,
                    label='Gear',
                    value=self.app.config.wheel_show_gear,
                    x=20,
                    y=80,
                    onChange=self._add_handler(lambda *args: self.config_change('wheel_show_gear', not self.app.config.wheel_show_gear, True)),
                )
            )
            self.wheel_tab.mount(
                Checkbox(
                    window=self.window,
                    label='Speed',
                    value=self.app.config.wheel_show_speed,
                    x=20,
                    y=110,
                    onChange=self._add_handler(lambda *args: self.config_change('wheel_show_speed', not self.app.config.wheel_show_speed, True)),
                )
            )
            self.wheel_tab.mount(
                Checkbox(
                    window=self.window,
                    label='Metric',
                    value=self.app.config.metric,
                    x=20,
                    y=140,
                    onChange=self._add_handler(lambda *args: self.config_change('metric', not self.app.config.metric, True)),
                )
            )


        def on_reset():
            self.app.config.set_defaults(True)
            self.app.apply_config()

        self.reset_tab.mount(
            ConfirmButton(
                window=self.window,
                x=10,
                y=50,
                text='reset settings',
                confirm_text='requires restart',
                on_confirm=on_reset,
            )
        )

    def set_open(self, open):
        ac.setVisible(self.window, 1 if open else 0)
        self.open = open

    def config_change(self, attribute, value, redraw_app=False):
        setattr(self.app.config, attribute, value)
        self.app.config.update_cfg = True
        
        if redraw_app:
            self.app.apply_config()
    
    def _add_handler(self, handler):
        """
        A reference to a callback handler passed to AC has to be retained or globally defined,
        ortherwise gets collected by garbage collection and will fail to run
        """
        self._handlers.append(handler)
        return handler
    
    def _create_trace_components(self, trace, y, label, show_color_labels = False):
        show_name = 'show_' + trace
        color_name = trace + '_color'

        def on_enabled_change(*args):
            self.config_change(show_name, not getattr(self.app.config, show_name))

            if not self.app.IS_CSP:
                if self.app.ac_graph_traces[trace]:
                    self.app.ac_graph_traces[trace].remove()
                    self.app.ac_graph_traces[trace] = None
                else:
                    self.app.ac_graph_traces[trace] = self.app.ac_graph.add_trace(getattr(self.app.config, trace + '_color'))
        
        def on_color_change(value):
            self.config_change(color_name, value)
            if not self.app.IS_CSP and self.app.ac_graph_traces[trace]:
                self.app.ac_graph_traces[trace].update_color(value)

        self.traces_tab.mount(
            Checkbox(
                window=self.window,
                label=label,
                value=getattr(self.app.config, show_name),
                x=20,
                y=y,
                onChange=self._add_handler(on_enabled_change),
            )
        )
        self.traces_tab.mount(
            RGBAInput(
                window=self.window,
                x=160,
                y=y - 3,
                value=getattr(self.app.config, color_name),
                onChange=self._add_handler(on_color_change),
                show_labels=show_color_labels
            )
        )
