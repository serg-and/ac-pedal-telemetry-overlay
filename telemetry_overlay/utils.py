import ac
import traceback


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
