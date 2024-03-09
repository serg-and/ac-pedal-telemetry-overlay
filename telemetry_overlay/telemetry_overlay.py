import ac

from config import Config
from data import TelemetryData
from widgets import Checkbox, Spinner, RGBAInput, ACGraph, CSPGraph
from utils import console_exception

IS_CSP = hasattr(ac, 'ext_createRenderTarget')

# app data
config = None
telemetry = None
update_ref = {'timer': 0, 'timeout': 0}
update_low_freq_ref = {'timer': 0, 'timeout': 0.2} # update low priority data every 0.2s
settings_open = False
confirm_active = False

csp_graph = None
ac_graph = None
ac_graph_traces = {
    'throttle': None,
    'brake': None,
    'clutch': None,
}

# main window ui
app_window = None
toggle_settings_button = None

# settings window ui
settings_window = None
throttle_checkbox = None
brake_checkbox = None
clutch_checkbox = None
width_spinner = None
height_spinner = None
opacity_spinner = None
trace_size_spinner = None
# time_window_spinner = None
sample_rate_spinner = None
throttle_color_input = None
brake_color_input = None
clutch_color_input = None
set_defaults_btn = None
confirm_set_defaults_btn = None


def acMain(ac_version):
    try:
        if IS_CSP:
            ac.ext_setStrictMode()

        global config, telemetry, app_window, toggle_settings_button

        config = Config()
        telemetry = TelemetryData()

        app_window = ac.newApp("Telemetry Overlay")
        ac.setTitle(app_window, "")
        ac.drawBorder(app_window, 0)
        ac.setIconPosition(app_window, 0, -10000)

        if IS_CSP:
            ac.addRenderCallback(app_window, app_render)

        toggle_settings_button = ac.addButton(app_window, "")
        ac.setPosition(toggle_settings_button, 0, 0)
        ac.setBackgroundOpacity(toggle_settings_button, 0)
        ac.drawBorder(toggle_settings_button, 0)
        ac.addOnClickedListener(toggle_settings_button, toggle_settings_window)

        global ac_graph, csp_graph
        if IS_CSP:
            csp_graph = CSPGraph(config.app_width, config.app_height, config.trace_size)
        else:
            ac_graph = ACGraph(app_window, 0, 0, config.app_width, config.app_height)

        set_window_config()
        
        global settings_window
        global throttle_checkbox, brake_checkbox, clutch_checkbox
        global width_spinner, height_spinner, opacity_spinner, trace_size_spinner, sample_rate_spinner
        global throttle_color_input, brake_color_input, clutch_color_input
        global set_defaults_btn, confirm_set_defaults_btn
        
        settings_window = ac.newApp("Telemetry Overlay Settings")
        ac.setVisible(settings_window, 0)
        ac.drawBorder(settings_window, 0)
        ac.setIconPosition(settings_window, 0, -10000)
        ac.setSize(settings_window, 530, 360)
        ac.setBackgroundOpacity(settings_window, 0.7)
        ac.setVisible(settings_window, 0)
        
        throttle_checkbox = Checkbox(
            window=settings_window,
            label='Throttle trace',
            value=config.show_throttle,
            x=20,
            y=60,
            onChange=on_show_throttle_change
        )
        brake_checkbox = Checkbox(
            window=settings_window,
            label='Brake trace',
            value=config.show_brake,
            x=20,
            y=100,
            onChange=on_show_brake_change
        )
        clutch_checkbox = Checkbox(
            window=settings_window,
            label='Clutch trace',
            value=config.show_clutch,
            x=20,
            y=140,
            onChange=on_show_clutch_change
        )

        throttle_color_input = RGBAInput(
            window=settings_window,
            x=160,
            y=57,
            value=config.throttle_color,
            onChange=on_throttle_color_change,
            show_labels=True
        )
        brake_color_input = RGBAInput(
            window=settings_window,
            x=160,
            y=97,
            value=config.brake_color,
            onChange=on_brake_color_change
        )
        clutch_color_input = RGBAInput(
            window=settings_window,
            x=160,
            y=137,
            value=config.clutch_color,
            onChange=on_clutch_color_change
        )
        
        width_spinner = Spinner(
            window=settings_window,
            label='Width',
            label_top=True,
            label_align='center',
            value=config.app_width,
            min=10,
            max=1000,
            step=1,
            x=20,
            y=200,
            width=235,
            onChange=on_width_change
        )
        height_spinner = Spinner(
            window=settings_window,
            label='Height',
            label_top=True,
            label_align='center',
            value=config.app_height,
            min=10,
            max=1000,
            step=1,
            x=20,
            y=260,
            width=235,
            onChange=on_height_change
        )
        opacity_spinner = Spinner(
            window=settings_window,
            label='Opacity',
            label_top=True,
            label_align='center',
            value=config.opacity * 100,
            min=0,
            max=100,
            step=1,
            x=20,
            y=320,
            width=235,
            onChange=on_opacity_change
        )

        sample_rate_spinner = Spinner(
            window=settings_window,
            label='Sample rate (Hz)',
            label_top=True,
            label_align='center',
            value=config.sample_rate,
            min=1,
            max=100,
            step=1,
            x=275,
            y=200,
            width=235,
            onChange=on_sample_rate_change
        )
        
        # trace size can only be changed with CSPGraph
        if IS_CSP:
            trace_size_spinner = Spinner(
                window=settings_window,
                label='Trace size',
                label_top=True,
                label_align='center',
                value=config.trace_size,
                min=1,
                max=10,
                step=1,
                x=275,
                y=260,
                width=235,
                onChange=on_trace_size_change,
            )
        # time_window_spinner = Spinner(
        #     window=settings_window,
        #     label='Time window (sec)',
        #     label_top=True,
        #     label_align='center',
        #     value=config.time_window,
        #     min=1,
        #     max=60,
        #     step=1,
        #     x=275,
        #     y=260,
        #     width=235,
        #     onChange=on_time_window_change
        # )
            
        set_defaults_btn = ac.addButton(settings_window, "reset settings")
        ac.setPosition(set_defaults_btn, 275, 320)
        ac.setSize(set_defaults_btn, 100, 22)
        ac.addOnClickedListener(set_defaults_btn, on_set_defaults_click)

        confirm_set_defaults_btn = ac.addButton(settings_window, "requires restart")
        ac.setVisible(confirm_set_defaults_btn, 0)
        ac.setBackgroundColor(confirm_set_defaults_btn, 1, 0, 0)
        ac.setPosition(confirm_set_defaults_btn, 385, 320)
        ac.setSize(confirm_set_defaults_btn, 125, 22)
        ac.addOnClickedListener(confirm_set_defaults_btn, on_reset_click)
    except Exception as e:
        console_exception(e, 'acMain() failed')


def set_window_config():
    global config, app_window, telemetry, update_ref, toggle_settings_button

    ac.setSize(app_window, config.app_width, config.app_height)
    ac.setBackgroundOpacity(app_window, config.opacity)

    # left side of the main window is clickable for settings
    ac.setSize(toggle_settings_button, config.app_width / 2, config.app_height)

    update_ref['timeout'] = 1 / config.sample_rate

    
    global csp_graph, ac_graph, ac_graph_traces
    if IS_CSP:
        csp_graph.width = config.app_width
        csp_graph.height = config.app_height
        csp_graph.trace_width = config.trace_size
        csp_graph.setup()
    else:
        ac_graph.width = config.app_width
        ac_graph.height = config.app_height
        ac_graph.setup()

        if config.show_clutch and not ac_graph_traces['clutch']:
            ac_graph_traces['clutch'] = ac_graph.add_trace(config.clutch_color)
        if config.show_throttle and not ac_graph_traces['throttle']:
            ac_graph_traces['throttle'] = ac_graph.add_trace(config.throttle_color)
        if config.show_brake and not ac_graph_traces['brake']:
            ac_graph_traces['brake'] = ac_graph.add_trace(config.brake_color)


def toggle_settings_window(*args):
    global settings_open, settings_window

    if settings_open:
        settings_open = False
        ac.setVisible(settings_window, 0)
    else:
        settings_open = True
        ac.setVisible(settings_window, 1)


def config_change(attribute, value, redraw_app=False):
    global config
    
    setattr(config, attribute, value)
    config.update_cfg = True
    
    if redraw_app:
        set_window_config()


def on_set_defaults_click(*args):
    global confirm_active, set_defaults_btn, confirm_set_defaults_btn
    if confirm_active:
        ac.setText(set_defaults_btn, "reset settings")
        ac.setVisible(confirm_set_defaults_btn, 0)
        confirm_active = False
    else:
        ac.setText(set_defaults_btn, "cancel")
        ac.setVisible(confirm_set_defaults_btn, 1)
        confirm_active = True


def on_reset_click(*args):
    global config
    config.set_defaults(True)
    on_set_defaults_click()
    set_window_config()


def on_show_throttle_change(id, value):
    global config, config, ac_graph, ac_graph_traces
    config_change('show_throttle', not config.show_throttle)

    if not IS_CSP:
        if ac_graph_traces['throttle']:
            ac_graph_traces['throttle'].remove()
            ac_graph_traces['throttle'] = None
        else:
            ac_graph_traces['throttle'] = ac_graph.add_trace(config.throttle_color)


def on_show_brake_change(id, value):
    global config, config, ac_graph, ac_graph_traces
    config_change('show_brake', not config.show_brake)

    if not IS_CSP:
        if ac_graph_traces['brake']:
            ac_graph_traces['brake'].remove()
            ac_graph_traces['brake'] = None
        else:
            ac_graph_traces['brake'] = ac_graph.add_trace(config.brake_color)


def on_show_clutch_change(id, value):
    global config, config, ac_graph, ac_graph_traces
    config_change('show_clutch', not config.show_clutch)

    if not IS_CSP:
        if ac_graph_traces['clutch']:
            ac_graph_traces['clutch'].remove()
            ac_graph_traces['clutch'] = None
        else:
            ac_graph_traces['clutch'] = ac_graph.add_trace(config.clutch_color)


def on_throttle_color_change(*args):
    global config, throttle_color_input, ac_graph_traces
    value = throttle_color_input.get_value()
    # traces['throttle'].color = value
    config_change('throttle_color', value)
    
    if not IS_CSP and ac_graph_traces['throttle']:
        ac_graph_traces['throttle'].update_color(value)


def on_brake_color_change(*args):
    global config, brake_color_input, ac_graph_traces
    value = brake_color_input.get_value()
    # traces['brake'].color = value
    config_change('brake_color', value)
    
    if not IS_CSP and ac_graph_traces['brake']:
        ac_graph_traces['brake'].update_color(value)


def on_clutch_color_change(*args):
    global config, clutch_color_input, ac_graph_traces
    value = clutch_color_input.get_value()
    # traces['clutch'].color = value
    config_change('clutch_color', value)
    
    if not IS_CSP and ac_graph_traces['clutch']:
        ac_graph_traces['clutch'].update_color(value)


def on_width_change(value):
    config_change('app_width', value, True)


def on_height_change(value):
    config_change('app_height', value, True)


def on_opacity_change(value):
    config_change('opacity', value / 100, True)


def on_trace_size_change(value):
    config_change('trace_size', value, True)


# def on_time_window_change(value):
#     config_change('time_window', value, True)


def on_sample_rate_change(value):
    config_change('sample_rate', value, True)


def acUpdate(deltaT):
    try:
        global config, update_ref, update_low_freq_ref, app_window, telemetry, csp_graph, ac_graph_traces

        update_ref['timer'] += deltaT
        update_low_freq_ref['timer'] += deltaT

        # update telemetry
        if update_ref['timer'] >= update_ref['timeout'] and telemetry.replay_time_multiplier != 0:
            prev_throttle = telemetry.throttle
            prev_brake = telemetry.brake
            prev_clutch = telemetry.clutch

            update_ref['timer'] = 0
            telemetry.update_telemetry()

            if IS_CSP:
                values = []
                if config.show_clutch:
                    values.append((prev_clutch, telemetry.clutch, config.clutch_color))
                if config.show_throttle:
                    values.append((prev_throttle, telemetry.throttle, config.throttle_color))
                if config.show_brake:
                    values.append((prev_brake, telemetry.brake, config.brake_color))
                
                csp_graph.add_values(values)
            else:
                if ac_graph_traces['brake']:
                    ac_graph_traces['brake'].add_value(telemetry.brake)
                if ac_graph_traces['throttle']:
                    ac_graph_traces['throttle'].add_value(telemetry.throttle)
                if ac_graph_traces['clutch']:
                    ac_graph_traces['clutch'].add_value(telemetry.clutch)
        
        # low priorty updates
        # low frequency to reduce load
        if update_low_freq_ref['timer'] >= update_low_freq_ref['timeout']:
            update_low_freq_ref['timer'] = 0
            telemetry.update_globals()

            # Window opacity is reset on drag, set to correct value
            ac.setBackgroundOpacity(app_window, config.opacity)

            if config.update_cfg:
                config.update_cfg = False
                config.save()
    except Exception as e:
        console_exception(e, 'acUpdate() failed')


def app_render(deltaT):
    global csp_graph
    csp_graph.render()


def acShutDown():
    global config
    
    # make sure that changes are always saved
    if config.update_cfg:
        config.save()
