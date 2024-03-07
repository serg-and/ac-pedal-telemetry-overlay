import ac
import traceback


def console(*args, join_char=' '):
    ac.console('[Telemetry Overlay]: ' + join_char.join([str(arg) for arg in args]))


def console_exception(exception, description = 'Caught exception'):
    console(description + ':', exception)

    for line in traceback.format_exc().splitlines():
        ac.console(line)
