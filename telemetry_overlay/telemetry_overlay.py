import ac

from app import App
from utils import console_exception

app_state = App()


def acMain(ac_version):
    try:
        app_state.load_main()
        ac.addRenderCallback(app_state.app_window, on_app_render)
    except Exception as e:
        console_exception(e, 'acMain() failed')


def acUpdate(dt):
    try:
        app_state.on_update(dt)
    except Exception as e:
        pass
        console_exception(e, 'acUpdate() failed')


def on_app_render(dt):
    try:
        app_state.on_render(dt)
    except Exception as e:
        pass
        console_exception(e, 'app render failed')


def acShutDown():
    # make sure that changes are always saved
    if app_state.config and app_state.config.update_cfg:
        app_state.config.save()
