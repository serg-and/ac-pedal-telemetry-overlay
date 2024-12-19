import ac, acsys

import math
from data import TelemetryData
from utils import console_exception, load_texture

CHECKBOX_SIZE = 16
CHECKBOX_LABEL_GAP = 10
SPINNER_WIDTH = 150
SPINNER_HEIGHT = 22
SPINNER_LABEL_GAP = 10

class BaseWidget:
    id = 0

    def set_visible(self, visible = True):
        ac.setVisible(self.id, True)


class Checkbox(BaseWidget):
    def __init__(self, window, value, x, y, size = CHECKBOX_SIZE, label = None, onChange = None):
        self.checkbox = ac.addCheckBox(window, '')
        ac.setValue(self.checkbox, value)
        ac.setPosition(self.checkbox, x, y)
        ac.setSize(self.checkbox, size, size)
        
        if onChange:
            ac.addOnCheckBoxChanged(self.checkbox, onChange)
        
        self.label = None
        if label:
            self.label = ac.addLabel(window, label)
            ac.setPosition(self.label, x + size + CHECKBOX_LABEL_GAP, y - 4)
            ac.setFontSize(self.label, size)

    def set_value(self, value):
        return ac.setValue(self.checkbox, value)
    
    def get_value(self):
        return ac.getValue(self.checkbox)
    
    def set_visible(self, visible=True):
        ac.setVisible(self.checkbox, visible)
        if self.label:
            ac.setVisible(self.label, visible)


class ConfirmButton(BaseWidget):
    def __init__(self,
        window,
        x = 0,
        y = 0,
        text = 'confirm',
        confirm_text = 'confirm',
        cancel_text = 'cancel',
        size = 22,
        button_width = 100,
        confirm_width = 125,
        on_confirm = None,
    ):
        self.text = text
        self.cancel_text = cancel_text
        self.active = False
        self.on_confirm = on_confirm

        self.button = ac.addButton(window, self.text)
        ac.setPosition(self.button, x, y)
        ac.setSize(self.button, button_width, size)
        ac.drawBorder(self.button, 0)

        self.confirm_button = ac.addButton(window, confirm_text)
        ac.setVisible(self.confirm_button, 0)
        ac.setBackgroundColor(self.confirm_button, 1, 0, 0)
        ac.setPosition(self.confirm_button, x + button_width + 10, y)
        ac.setSize(self.confirm_button, confirm_width, size)
        ac.drawBorder(self.confirm_button, 0)

        self._on_click = self.on_click
        self._on_confirm_click = self.on_confirm_click
        ac.addOnClickedListener(self.button, self._on_click)
        ac.addOnClickedListener(self.confirm_button, self._on_confirm_click)
    
    def on_click(self, *args):
        if self.active:
            ac.setVisible(self.confirm_button, 0)
            ac.setText(self.button, self.text)
            self.active = False
        else:
            ac.setVisible(self.confirm_button, 1)
            ac.setText(self.button, self.cancel_text)
            self.active = True
    
    def on_confirm_click(self, *args):
        if self.on_confirm:
            self.on_confirm()
        
        self.set_visible(self.confirm_button, 0)
        self.active = False

    def set_visible(self, visible=True):
        if visible:
            ac.setVisible(self.button, 1)
            ac.setVisible(self.confirm_button, 1 if self.active else 0)
        else:
            ac.setVisible(self.button, 0)
            ac.setVisible(self.confirm_button, 0)
            self.active = False


class Spinner(BaseWidget):
    def __init__(
            self,
            window,
            value,
            min,
            max,
            step,
            x,
            y,
            width = SPINNER_WIDTH,
            height = SPINNER_HEIGHT,
            label_gap=SPINNER_LABEL_GAP,
            label = None,
            label_top = False,
            label_align = 'left',
            onChange = None):
        
        self.spinner = ac.addSpinner(window, "")
        ac.setRange(self.spinner, min, max)
        ac.setStep(self.spinner, step)
        ac.setValue(self.spinner, value)
        ac.setPosition(self.spinner, x, y)
        ac.setSize(self.spinner, width, height)
        ac.setFontSize(self.spinner, 14)
        
        if onChange:
            ac.addOnValueChangeListener(self.spinner, onChange)
        
        self.label = None
        if label:
            self.label = ac.addLabel(window, label)
            ac.setFontSize(self.label, 16)
            
            if label_top:
                ac.setFontAlignment(self.label, label_align)
                ac.setSize(self.label, width, 16)
                ac.setPosition(self.label, x, y - label_gap - 16)
            else:
                ac.setPosition(self.label, x + width + label_gap, y - 2)

    def set_value(self, value):
        return ac.setValue(self.spinner, value)
    
    def get_value(self):
        return ac.getValue(self.spinner)
    
    def set_visible(self, visible=True):
        ac.setVisible(self.spinner, visible)
        if self.label:
            ac.setVisible(self.label, visible)


class RGBAInput:
    def __init__(self, window, x, y, value = (0.0, 0.0, 0.0, 0.0), show_labels = False, onChange = None):
        self.window = window
        self.x = x
        self.y = y
        self.show_labels = show_labels
        
        self.on_spinner_change = lambda *args: onChange(self.get_value()) if onChange else None

        self.r_spinner = self._create_spinner('R', 0, value[0])
        self.g_spinner = self._create_spinner('G', 90, value[1])
        self.b_spinner = self._create_spinner('B', 180, value[2])
        self.a_spinner = self._create_spinner('A', 270, value[3])
    
    def _create_spinner(self, label, x_offset, value):
        return Spinner(
            window=self.window,
            y=self.y,
            x=self.x + x_offset,
            value=value * 100,
            min=0,
            max=100,
            step=1,
            width=80,
            label=label if self.show_labels else None,
            label_top=True,
            label_align='center',
            onChange=self.on_spinner_change,
        )
    
    def set_value(self, value):
        self.r_spinner.set_value(value[0] * 100)
        self.g_spinner.set_value(value[1] * 100)
        self.b_spinner.set_value(value[2] * 100)
        self.a_spinner.set_value(value[3] * 100)

    def get_value(self):
        return (
            self.r_spinner.get_value() / 100,
            self.g_spinner.get_value() / 100,
            self.b_spinner.get_value() / 100,
            self.a_spinner.get_value() / 100,
        )
    
    def set_visible(self, visible=True):
        self.r_spinner.set_visible(visible)
        self.g_spinner.set_visible(visible)
        self.b_spinner.set_visible(visible)
        self.a_spinner.set_visible(visible)


tab_handlers = {}


class Tabs:
    def __init__(
            self,
            window,
            x = 0,
            y = 0,
            btn_width = 50,
            btn_size = 16,
            btn_margin = 10,
    ):
        self.window = window
        self.x = x
        self.y = y
        self.btn_width = btn_width
        self.btn_size = btn_size
        self.btn_margin = btn_margin

        self.tabs = []
        self.btns = []
        self.active = -1

    def add_tab(self, name = ''):
        tab = Tab(name)
        btn = ac.addButton(self.window, name)
        ac.setPosition(btn, self.x + len(self.tabs) * (self.btn_width + self.btn_margin), self.y)
        ac.setSize(btn, self.btn_width, self.btn_size + 6)
        ac.setBackgroundColor(btn, 0.5, 0.5, 0.5)
        ac.drawBorder(btn, 0)

        def on_click(*args):
            self.set_active_tab(self.tabs.index(tab) if tab in self.tabs else len(self.tabs))
        
        tab_handlers[btn] = on_click
        ac.addOnClickedListener(btn, tab_handlers[btn])

        self.tabs.append(tab)
        self.btns.append(btn)

        return tab
    
    def set_active_tab(self, index):
        if index == self.active:
            return

        self.tabs[self.active].set_active(False)
        ac.setBackgroundColor(self.btns[self.active], 0.5, 0.5, 0.5)
        ac.setBackgroundColor(self.btns[self.active], 0.5, 0.5, 0.5)
        
        self.tabs[index].set_active(True)
        ac.setBackgroundColor(self.btns[index], 1, 0, 0)

        self.active = index


class Tab:
    def __init__(self, name = ''):
        self.name = name
        self.active = False
        self.components = []

    def mount(self, component):
        self.components.append(component)
        
        if isinstance(component, BaseWidget) or hasattr(component, 'set_visible'):
            component.set_visible(self.active)
        else:
            ac.setVisible(component, self.active)
    
    def unmount(self, component):
        self.components.remove(component)
        
        if isinstance(component, BaseWidget) or hasattr(component, 'set_visible'):
            component.set_visible(False)
        else:
            ac.setVisible(component, False)
    
    def set_active(self, value = True):
        for comp in self.components:
            if isinstance(comp, BaseWidget) or hasattr(comp, 'set_visible'):
                comp.set_visible(value)
            else:
                ac.setVisible(comp, value)
        
        self.active = value


class ACGraph:
    def __init__(self, window, x, y, width, height, trace_width = 1, opacity = 0.2):
        self.graphs = []
        self.window = window
        self.traces = []
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.trace_width = trace_width
        self.opacity = opacity

        self.bg_label = ac.addLabel(self.window, '')
        ac.setBackgroundColor(self.bg_label, 0.25, 0.25, 0.25)
        
        self.setup()
    
    def setup(self):
        for graph in self.graphs:
            ac.setRange(graph, 0, 0, 0)
            ac.removeItem(self.window, graph)

        self.graphs = []

        for i in range(self.trace_width):
            graph = ac.addGraph(self.window, '')
            ac.setRange(graph, 0.0, self.height, self.width)
            ac.setPosition(graph, self.x + 1, self.y  + 1 + i)
            ac.setSize(graph, self.width - 1, self.height - 1 - self.trace_width)
            ac.setBackgroundOpacity(graph, 0)
            ac.drawBorder(graph, 0)
            # ac.setBackgroundColor(graph, 0.25, 0.25, 0.25)
            # ac.setBackgroundOpacity(graph, self.opacity / self.trace_width)

            for i, trace in enumerate(self.traces):
                trace._index = i
                ac.addSerieToGraph(graph, trace.color[0], trace.color[1], trace.color[2])
            
            self.graphs.append(graph)
        
        ac.setPosition(self.bg_label, self.x, self.y)
        ac.setSize(self.bg_label, self.width, self.height)
        ac.setBackgroundOpacity(self.bg_label, self.opacity)

    def add_trace(self, color):
        trace_index = len(self.traces)
        trace = ACGraphTrace(self, color, trace_index)
        self.traces.append(trace)
        for graph in self.graphs:
            ac.addSerieToGraph(graph, color[0], color[1], color[2])
        
        return trace


class ACGraphTrace:
    def __init__(self, graph, color, trace_index):
        self._graph = graph
        self._index = trace_index
        self.color = color
    
    def add_value(self, value):
        for graph in self._graph.graphs:
            ac.addValueToGraph(graph, self._index, value * self._graph.height)
    
    def update_color(self, color):
        self.color = color
        self._graph.setup()

    def remove(self):
        self._graph.traces.remove(self)
        self._graph.setup()


class CSPGraph:
    def __init__(self, x, y, width, height, trace_width = 1):
        self.x = x
        self.y = y
        self.trace_width = int(trace_width)
        self.width = width
        self.height = height + self.trace_width

        # main target for drawing lines
        self.render_target = 0
        # secondary target for temporarily storing left shifted version of main target
        self.shift_target = 0
    
    def setup(self):
        try:
            if self.render_target:
                ac.ext_disposeRenderTarget(self.render_target)
            if self.shift_target:
                ac.ext_disposeRenderTarget(self.shift_target)

            # main target for drawing lines
            self.render_target = ac.ext_createRenderTarget(self.width, self.height, False)
            # secondary target for temporarily storing left shifted version of main target
            self.shift_target = ac.ext_createRenderTarget(self.width, self.height, False)

            return True
        except Exception as e:
            console_exception(e, 'Failed to create CSP render targets', True)
            return False

    def add_values(self, values):
        if not self.render_target:
            return

        self._shift_left()
        ac.ext_bindRenderTarget(self.render_target)
        ac.ext_glSetBlendMode(0)

        inner_height = self.height - self.trace_width
        for (prev, value, color) in values:
            y1 = None
            y2 = None
            if value > prev:
                y1 = self.height - inner_height * prev
                y2 = self.height - inner_height * value - self.trace_width
            else:
                y1 = self.height - inner_height * prev - self.trace_width
                y2 = self.height - inner_height * value
            
            ac.glColor4f(color[0], color[1], color[2], color[3])
            if self.trace_width == 1:
                ac.glBegin(acsys.GL.Lines)
                ac.glVertex2f(self.width, y1)
                ac.glVertex2f(self.width, y2)
                ac.glEnd()
            else:
                ac.glBegin(acsys.GL.Quads)
                ac.glVertex2f(self.width - self.trace_width, y1)
                ac.glVertex2f(self.width, y1)
                ac.glVertex2f(self.width, y2)
                ac.glVertex2f(self.width - self.trace_width, y2)
                ac.glEnd()
                
        ac.ext_restoreRenderTarget()
        ac.ext_generateMips(self.render_target)

    def _shift_left(self):
        if not self.render_target or not self.shift_target:
            return
        
        # clear shift target
        ac.ext_clearRenderTarget(self.shift_target)
        ac.ext_bindRenderTarget(self.shift_target)
        ac.ext_glSetBlendMode(0)
        
        # copy main target
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glSetTexture(self.render_target, 0)
        ac.glColor4f(1,1,1,1)
        # shift all left by 1 px
        ac.ext_glVertexTex(-1, 0, 0, 0)
        ac.ext_glVertexTex(-1, self.height, 0, 1)
        ac.ext_glVertexTex(self.width - 1, self.height, 1, 1)
        ac.ext_glVertexTex(self.width - 1, 0, 1, 0)
        ac.glEnd()
        ac.ext_restoreRenderTarget()

        # copy shifter target to main target
        ac.ext_clearRenderTarget(self.render_target)
        ac.ext_bindRenderTarget(self.render_target)
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glSetTexture(self.shift_target, 0)
        ac.ext_glSetBlendMode(0)
        ac.glColor4f(1,1,1,1)
        ac.ext_glVertexTex(0,0, 0, 0)
        ac.ext_glVertexTex(0, self.height, 0, 1)
        ac.ext_glVertexTex(self.width, self.height, 1, 1)
        ac.ext_glVertexTex(self.width, 0, 1, 0)
        ac.glEnd()
    
    def render(self):
        ac.glBegin(acsys.GL.Quads)
        ac.glColor4f(1,1,1,1)
        ac.ext_glSetTexture(self.render_target, 0)
        ac.ext_glVertexTex(0 + self.x, 0 + self.y, 0, 0)
        ac.ext_glVertexTex(0 + self.x, self.height + self.y, 0, 1)
        ac.ext_glVertexTex(self.width + self.x, self.height + self.y, 1, 1)
        ac.ext_glVertexTex(self.width + self.x, 0 + self.y, 1, 0)
        ac.glEnd()


class Pedals:
    def __init__(self, app_window, IS_CSP, config, telemetry=TelemetryData, x=0, y=0, height=100):
        self.IS_CSP = IS_CSP
        self.config = config
        self.telemetry = telemetry
        self.x = x
        self.y = y
        self.height = height

        self.font = 0
        self.throttle_label = None
        self.brake_label = None
        self.clutch_label = None
        if self.IS_CSP:
            self.font = ac.ext_glFontCreate('roboto', 1, 1, 1)
        else:
            self.throttle_label = ac.addLabel(app_window, '')
            self.brake_label = ac.addLabel(app_window, '')
            self.clutch_label = ac.addLabel(app_window, '')

        self.setup()
        
    def setup(self):
        self.show_bars = self.config.show_throttle_bar or self.config.show_brake_bar or self.config.show_clutch_bar

        self.pedal_height = self.height
        self.pedal_y= self.y

        self.end_height = max(2, self.pedal_height * 0.015)
        self.end_gap = max(2, self.end_height / 1.15)
        if self.config.show_bar_value:
            self.pedal_height = self.pedal_height - self.config.bar_width - self.end_gap
            self.pedal_y = self.pedal_y + self.config.bar_width + self.end_gap

        self.bar_height = self.pedal_height
        self.bar_y = self.pedal_y

        combined_height = self.end_height + self.end_gap

        if self.config.pedals_end_stop:
            self.bar_y += combined_height
            self.bar_height -= combined_height
        if self.config.pedals_base_stop:
            self.bar_height -= combined_height

        self.gap_x = round(self.config.bar_width / 2)

        if not self.IS_CSP:
            i = 0
            for show, label in [
                (self.config.show_throttle_bar, self.throttle_label),
                (self.config.show_brake_bar, self.brake_label),
                (self.config.show_clutch_bar, self.clutch_label),
            ]:
                if label:
                    if show and self.config.show_bar_value:
                        ac.setPosition(label, self.x + i * (self.config.bar_width + self.gap_x), self.y - self.end_gap - self.end_height)
                        ac.setSize(label, self.config.bar_width, self.config.bar_width)
                        ac.setFontSize(label, self.config.bar_width)
                        ac.setFontAlignment(label, 'center')
                        ac.setVisible(label, 1)
                        ac.setBackgroundColor(label, 1, 0, 0)
                        i += 1
                    else:
                        ac.setVisible(label, 0)

    
    def width(self):
        bars = 0
        if self.config.show_throttle_bar: bars +=1 
        if self.config.show_brake_bar: bars +=1 
        if self.config.show_clutch_bar: bars +=1

        if bars == 0:
            return 0
        
        return bars * self.config.bar_width + (bars - 1) * self.gap_x
    
    def update(self):
        if not self.show_bars or self.IS_CSP or not self.config.show_bar_value:
            return
        
        for show, label, value in [
            (self.config.show_throttle_bar, self.throttle_label, self.telemetry.throttle),
            (self.config.show_brake_bar, self.brake_label, self.telemetry.brake),
            (self.config.show_clutch_bar, self.clutch_label, self.telemetry.clutch),
        ]:
            if show and label:
                rounded = round(value * 100)
                ac.setText(label, '00' if rounded >= 100 else str(rounded))

    def render(self):
        if not self.show_bars:
            return
        
        bars = [
            (self.config.show_throttle_bar, self.telemetry.throttle, self.config.throttle_color),
            (self.config.show_brake_bar, self.telemetry.brake, self.config.brake_color),
            (self.config.show_clutch_bar, self.telemetry.clutch, self.config.clutch_color),
        ]
        for i, (value, color) in enumerate([rest for enabled, *rest in bars if enabled]):
            x = self.x + i * (self.config.bar_width + self.gap_x)
            
            # bar background
            ac.glColor4f(0.24, 0.24, 0.24, self.config.opacity)
            ac.glQuad(x, self.bar_y, self.config.bar_width, self.bar_height)

            height = self.bar_height * value
            ac.glColor3f(color[0], color[1], color[2])
            ac.glQuad(x, self.bar_y + self.bar_height - height, self.config.bar_width, height)

            # end stop
            if self.config.pedals_end_stop:
                if value == 1: ac.glColor3f(color[0], color[1], color[2])
                else: ac.glColor4f(0.24, 0.24, 0.24, self.config.opacity)
                ac.glQuad(x, self.pedal_y, self.config.bar_width, self.end_height)
            # base stop
            if self.config.pedals_base_stop:
                if value > 0: ac.glColor3f(color[0], color[1], color[2])
                else: ac.glColor4f(0.24, 0.24, 0.24, self.config.opacity)
                ac.glQuad(x, self.pedal_y + self.pedal_height - self.end_height, self.config.bar_width, self.end_height)

            if self.IS_CSP and self.config.show_bar_value:
                rounded = round(value * 100)
                ac.ext_glFontColor(self.font, (1, 1, 1, 1))
                ac.ext_glFontUse(
                    self.font,
                    '00' if rounded >= 100 else str(rounded),
                    (x + self.config.bar_width / 2, self.y - self.config.bar_width * 0.2),
                    self.config.bar_width,
                    2
                )

class Wheel:
    def __init__(self, IS_CSP, config, telemetry=TelemetryData, x=0, y=0, size=100, depth=5, angle=20, color=(1, 1, 1, 1)):
        self.IS_CSP = IS_CSP
        self.config = config
        self.telemetry = telemetry
        self.x = x
        self.y = y
        self.size = size
        self.depth = depth
        self.angle = angle
        self.color = color

        self.full_white_circle_texture = load_texture('img/white-circle.png')

        self.font = 0
        if self.IS_CSP:
            self.font = ac.ext_glFontCreate('roboto', 1, 1, 1)
        
        self.setup()
    
    def setup(self):
        self.size = self.config.app_height
        self.depth = self.config.wheel_depth
        self.angle = self.config.wheel_angle

        self.angle_offset = self.angle / 2
        self.radius = self.size / 2
        self.inner_size = self.size - self.depth * 2

        center =  self.depth + self.inner_size / 2
        self.center_x = self.x + center
        self.center_y = self.y + center

        if self.config.wheel_show_gear and self.config.wheel_show_speed:
            self.gear_size = self.inner_size * 0.35
            self.unit_size = self.inner_size * 0.12
            self.speed_size = self.inner_size * 0.16
            self.y_gear = self.center_y - self.gear_size - self.inner_size * 0.07
            self.y_unit = self.center_y + self.inner_size * 0.03
            self.y_speed = self.y_unit + self.unit_size + self.inner_size * 0.03
        else:
            self.gear_size = self.inner_size * 0.39
            self.y_gear = self.center_y - self.gear_size / 1.5
            
            self.unit_size = self.inner_size * 0.14
            self.speed_size = self.inner_size * 0.22
            gap = self.inner_size * 0.05
            total_height = self.unit_size + self.speed_size + gap
            self.y_unit = self.center_y - total_height / 2
            self.y_speed = self.center_y + total_height / 2 - self.speed_size

    
    def _point(self, deg, offset):
        x = self.x + self.radius + math.sin(math.radians(deg)) * offset
        y = self.y + self.radius + math.cos(math.radians(deg)) * offset * -1

        return x, y
    
    def render(self):
        ac.glColor4f(0.24, 0.24, 0.24, self.config.opacity)
        ac.glQuadTextured(self.x, self.y, self.size, self.size, self.full_white_circle_texture)
        
        ac.glColor4f(0, 0, 0, min(1, self.config.opacity + 0.1))
        ac.glQuadTextured(self.x + self.depth, self.y + self.depth, self.inner_size, self.inner_size, self.full_white_circle_texture)

        xbl, ybl = self._point(self.telemetry.steering - self.angle_offset, self.radius - self.depth)
        xbr, ybr = self._point(self.telemetry.steering + self.angle_offset, self.radius - self.depth)
        xtl, ytl = self._point(self.telemetry.steering - self.angle_offset, self.radius)
        xtr, ytr = self._point(self.telemetry.steering + self.angle_offset, self.radius)

        ac.glBegin(acsys.GL.Quads)
        ac.glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        ac.glVertex2f(xbl, ybl)
        ac.glVertex2f(xbr, ybr)
        ac.glVertex2f(xtr, ytr)
        ac.glVertex2f(xtl, ytl)
        ac.glEnd()

        if self.IS_CSP:
            if self.config.wheel_show_gear:
                ac.ext_glFontColor(self.font, (1, 1, 1, 1))
                ac.ext_glFontUse(self.font, self.telemetry.gear_str, (self.center_x, self.y_gear) , self.gear_size, 2)
            if self.config.wheel_show_speed:
                ac.ext_glFontColor(self.font, (0.5, 0.5, 0.5, 1))
                ac.ext_glFontUse(
                    self.font,
                    'KPH' if self.config.metric else 'MPH',
                    (self.center_x, self.y_unit),
                    self.unit_size,
                    2
                )
                ac.ext_glFontColor(self.font, (1, 1, 1, 1))
                ac.ext_glFontUse(
                    self.font,
                    str(round(self.telemetry.speed_kph if self.config.metric else self.telemetry.speed_mph)),
                    (self.center_x, self.y_speed),
                    self.speed_size,
                    2
                )
