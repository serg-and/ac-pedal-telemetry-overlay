import ac
import traceback
import os


def console(*args, join_char=' '):
    ac.console('[Telemetry Overlay]: ' + join_char.join([str(arg) for arg in args]))


def console_exception(exception, description = 'Caught exception', log = False):
    console(description + ':', exception)

    trace = traceback.format_exc()

    for line in traceback.format_exc().splitlines():
        ac.console(line)

    if log:
        ac.log(description + ':', exception)
        ac.log(trace)


def get_path(path):
    curr_dir = os.path.dirname(__file__)
    return os.path.join(curr_dir, path)


def load_texture(texture_path):
    console(texture_path)
    try:
        abs_path = get_path(texture_path)
        texture_id = ac.newTexture(abs_path)
        if texture_id == -1:
            return None
        
        return texture_id
    except Exception as e:
        console_exception(e, 'Failed to load texture "' + abs_path + '"', True)
        return None

    
