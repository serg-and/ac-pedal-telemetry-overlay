import ac

from config import Config
from modules.trace import Trace
from data import TelemetryData
from widgets import Checkbox, Spinner, RGBAInput
from utils import console_exception

# app data
config = None
telemetry = None
update_ref = {'timer': 0, 'timeout': 0}
update_low_freq_ref = {'timer': 0, 'timeout': 0.2} # update low priority data every 0.2s
settings_open = False

# main window ui
app_window = None
toggle_settings_button = None
traces = {
    'throttle': None,
    'brake': None,
    'clutch': None,
}

# settings window ui
settings_window = None
throttle_checkbox = None
brake_checkbox = None
clutch_checkbox = None
width_spinner = None
height_spinner = None
opacity_spinner = None
trace_size_spinner = None
time_window_spinner = None
sample_rate_spinner = None
throttle_color_input = None
brake_color_input = None
clutch_color_input = None


def acMain(ac_version):
    try:
        global config, telemetry, app_window, toggle_settings_button

        config = Config()
        telemetry = TelemetryData()

        app_window = ac.newApp("Telemetry Overlay")
        ac.setTitle(app_window, "")
        ac.drawBorder(app_window, 0)
        ac.setIconPosition(app_window, 0, -10000)
        ac.addRenderCallback(app_window, app_render)

        toggle_settings_button = ac.addButton(app_window, "")
        ac.setPosition(toggle_settings_button, 0, 0)
        ac.setBackgroundOpacity(toggle_settings_button, 0)
        ac.drawBorder(toggle_settings_button, 0)
        ac.addOnClickedListener(toggle_settings_button, toggle_settings_window)
        
        set_window_config()
        
        global settings_window
        global throttle_checkbox, brake_checkbox, clutch_checkbox
        global width_spinner, height_spinner, opacity_spinner, trace_size_spinner, time_window_spinner, sample_rate_spinner
        global throttle_color_input, brake_color_input, clutch_color_input
        
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
        
        trace_size_spinner = Spinner(
            window=settings_window,
            label='Trace size',
            label_top=True,
            label_align='center',
            value=config.trace_size * 10,
            min=1,
            max=100,
            step=1,
            x=275,
            y=200,
            width=235,
            onChange=on_trace_size_change,
        )
        time_window_spinner = Spinner(
            window=settings_window,
            label='Time window (sec)',
            label_top=True,
            label_align='center',
            value=config.time_window,
            min=1,
            max=60,
            step=1,
            x=275,
            y=260,
            width=235,
            onChange=on_time_window_change
        )
        sample_rate_spinner = Spinner(
            window=settings_window,
            label='Sample rate (Hz)',
            label_top=True,
            label_align='center',
            value=config.sample_rate,
            min=1,
            max=50,
            step=1,
            x=275,
            y=320,
            width=235,
            onChange=on_sample_rate_change
        )
    except Exception as e:
        console_exception(e, 'acMain() failed')


def set_window_config():
    global config, app_window, telemetry, update_ref, traces, toggle_settings_button

    ac.setSize(app_window, config.app_width, config.app_height)
    ac.setBackgroundOpacity(app_window, config.opacity)

    # left side of the main window is clickable for settings
    ac.setSize(toggle_settings_button, config.app_width / 2, config.app_height)

    update_ref['timeout'] = 1 / config.sample_rate

    if traces['throttle']:
        traces['throttle'].clear()
    if traces['brake']:
        traces['brake'].clear()
    if traces['clutch']:
        traces['clutch'].clear()
    
    if config.show_brake:
        set_brake_trace()
    if config.show_throttle:
        set_throttle_trace()
    if config.show_clutch:
        set_clutch_trace()


def toggle_settings_window(*args):
    global settings_open, settings_window

    if settings_open:
        settings_open = False
        ac.setVisible(settings_window, 0)
    else:
        settings_open = True
        ac.setVisible(settings_window, 1)


def set_trace(trace, color):
    global config, telemetry, traces
    traces[trace] = Trace(config, telemetry, color)


def set_throttle_trace():
    global config
    set_trace('throttle', config.throttle_color)


def set_brake_trace():
    global config
    set_trace('brake', config.brake_color)


def set_clutch_trace():
    global config
    set_trace('clutch', config.clutch_color)


def config_change(attribute, value, redraw_app=False):
    global config
    
    setattr(config, attribute, value)
    config.update_cfg = True
    
    if redraw_app:
        set_window_config()


def on_show_throttle_change(id, value):
    global config, traces
    
    if traces['throttle']:
        traces['throttle'].clear()
    
    if value:
        set_throttle_trace()
        config.show_throttle = True
    else:
        traces['throttle'] = None
        config.show_throttle = False
    
    config.update_cfg = True


def on_show_brake_change(id, value):
    global config, traces
    
    if traces['brake']:
        traces['brake'].clear()
    
    if value:
        set_brake_trace()
        config.show_brake = True
    else:
        traces['brake'] = None
        config.show_brake = False
    
    config.update_cfg = True


def on_show_clutch_change(id, value):
    global config, traces
    
    if traces['clutch']:
        traces['clutch'].clear()
    
    if value:
        set_clutch_trace()
        config.show_clutch = True
    else:
        traces['clutch'] = None
        config.show_clutch = False
    
    config.update_cfg = True


def on_throttle_color_change(*args):
    global config, traces, throttle_color_input
    value = throttle_color_input.get_value()
    traces['throttle'].color = value
    config_change('throttle_color', value)


def on_brake_color_change(*args):
    global config, traces, brake_color_input
    value = brake_color_input.get_value()
    traces['brake'].color = value
    config_change('brake_color', value)


def on_clutch_color_change(*args):
    global config, traces, clutch_color_input
    value = clutch_color_input.get_value()
    traces['clutch'].color = value
    config_change('clutch_color', value)


def on_width_change(value):
    config_change('app_width', value, True)


def on_height_change(value):
    config_change('app_height', value, True)


def on_opacity_change(value):
    config_change('opacity', value / 100, True)


def on_trace_size_change(value):
    config_change('trace_size', value / 10, True)


def on_time_window_change(value):
    config_change('time_window', value, True)


def on_sample_rate_change(value):
    config_change('sample_rate', value, True)


def acUpdate(deltaT):
    try:
        global config, update_ref, update_low_freq_ref, app_window, telemetry, traces

        update_ref['timer'] += deltaT
        update_low_freq_ref['timer'] += deltaT

        # update telemetry
        if update_ref['timer'] >= update_ref['timeout']:
            update_ref['timer'] = 0
            telemetry.update_telemetry()

            if traces['throttle']:
                traces['throttle'].update(telemetry.throttle)
            if traces['brake']:
                traces['brake'].update(telemetry.brake)
            if traces['clutch']:
                traces['clutch'].update(telemetry.clutch)
        
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
    global traces
    
    # order by importance, last draw is rendered on top
    if traces['clutch']:
        traces['clutch'].draw()
    if traces['throttle']:
        traces['throttle'].draw()
    if traces['brake']:
        traces['brake'].draw()


def acShutDown():
    global config
    
    # make sure that changes are always saved
    if config.update_cfg:
        config.save()
