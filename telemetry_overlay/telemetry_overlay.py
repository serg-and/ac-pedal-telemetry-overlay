import ac

from app import App
from utils import console_exception

app_state = None


def acMain(ac_version):
    global app_state

    try:
        app_state = App()
        app_state.load_main()
        ac.addRenderCallback(app_state.app_window, on_app_render)
    except Exception as e:
        console_exception(e, 'acMain() failed', True)
    
    return "telemetry_overlay"


def acUpdate(dt):
    global app_state
    if not app_state:
        return

    try:
        app_state.on_update(dt)
    except Exception as e:
        pass
        console_exception(e, 'acUpdate() failed')


def on_app_render(dt):
    global app_state
    if not app_state:
        return

    try:
        app_state.on_render(dt)
    except Exception as e:
        pass
        console_exception(e, 'app render failed')


def acShutDown():
    global app_state
    if not app_state:
        return

    # make sure that changes are always saved
    if app_state.config and app_state.config.update_cfg:
        app_state.config.save()
