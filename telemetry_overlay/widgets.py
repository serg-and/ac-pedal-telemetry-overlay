import ac, acsys
import math

CHECKBOX_SIZE = 16
CHECKBOX_LABEL_GAP = 10
SPINNER_WIDTH = 150
SPINNER_HEIGHT = 22
SPINNER_LABEL_GAP = 10


class Checkbox:
    def __init__(self, window, value, x, y, size = CHECKBOX_SIZE, label = None, onChange = None):
        self.checkbox = ac.addCheckBox(window, '')
        ac.setValue(self.checkbox, value)
        ac.setPosition(self.checkbox, x, y)
        ac.setSize(self.checkbox, size, size)
        
        if onChange:
            ac.addOnCheckBoxChanged(self.checkbox, onChange)
        
        if label:
            self.label = ac.addLabel(window, label)
            ac.setPosition(self.label, x + size + CHECKBOX_LABEL_GAP, y - 4)
            ac.setFontSize(self.label, size)

    def set_value(self, value):
        return ac.setValue(self.checkbox, value)
    
    def get_value(self):
        return ac.getValue(self.checkbox)


class Spinner:
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


class RGBAInput:
    def __init__(self, window, x, y, value = (0.0, 0.0, 0.0, 0.0), show_labels = False, onChange = None):
        self.window = window
        self.x = x
        self.y = y
        self.on_change = onChange
        self.show_labels = show_labels
        
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
            onChange=self.on_change,
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


class ACGraph:
    def __init__(self, window, x, y, width, height):
        self.graph = None
        self.window = window
        self.traces = []
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.setup()
    
    def setup(self):
        if self.graph:
            ac.setRange(self.graph, 0, 0, 0)

        self.graph = ac.addGraph(self.window, '')
        ac.setRange(self.graph, 0.0, self.height, self.width)
        ac.setPosition(self.graph, self.x, self.y)
        ac.setSize(self.graph, self.width, self.height)
        ac.setBackgroundOpacity(self.graph, 0)
        ac.drawBorder(self.graph, 0)

        for i, trace in enumerate(self.traces):
            trace._index = i
            ac.addSerieToGraph(self.graph, trace.color[0], trace.color[1], trace.color[2])

    def add_trace(self, color):
        trace_index = len(self.traces)
        trace = ACGraphTrace(self, color, trace_index)
        self.traces.append(trace)
        ac.addSerieToGraph(self.graph, color[0], color[1], color[2])
        
        return trace


class ACGraphTrace:
    def __init__(self, graph, color, trace_index):
        self._graph = graph
        self._index = trace_index
        self.color = color
    
    def add_value(self, value):
        ac.addValueToGraph(self._graph.graph, self._index, value * self._graph.height)
    
    def update_color(self, color):
        self.color = color
        self._graph.setup()

    def remove(self):
        self._graph.traces.remove(self)
        self._graph.setup()


class CSPGraph:
    def __init__(self, width, height, trace_width = 1):
        self.trace_width = int(trace_width)
        self.width = width
        self.height = height + self.trace_width

        # main target for drawing lines
        self.render_target = ac.ext_createRenderTarget(self.width, self.height, False)
        # secondary target for temporarily storing left shifted version of main target
        self.shift_target = ac.ext_createRenderTarget(self.width, self.height, False)
    
    def setup(self):
        if self.render_target:
            ac.ext_disposeRenderTarget(self.render_target)
        if self.shift_target:
            ac.ext_disposeRenderTarget(self.shift_target)

        # main target for drawing lines
        self.render_target = ac.ext_createRenderTarget(self.width, self.height, False)
        # secondary target for temporarily storing left shifted version of main target
        self.shift_target = ac.ext_createRenderTarget(self.width, self.height, False)

    def add_values(self, values):
        self._shift_left()
        ac.ext_bindRenderTarget(self.render_target)
        ac.ext_glSetBlendMode(1)

        x1 = self.width - 1
        x2 = self.width

        for (prev, value, color) in values:
            inner_height = self.height - self.trace_width
            y1 = self.height - (inner_height) * prev
            y2 = self.height - (inner_height) * value
            ac.glColor4f(color[0], color[1], color[2], color[3])

            if y1 == y2:
                if self.trace_width == 1:
                    ac.glBegin(acsys.GL.Lines)
                    ac.glVertex2f(x1, y1)
                    ac.glVertex2f(x2, y2)
                    ac.glEnd()
                else:
                    ac.glBegin(acsys.GL.Quads)
                    ac.glVertex2f(x1, y1)
                    ac.glVertex2f(x1, y1 - self.trace_width - 1)
                    ac.glVertex2f(x2, y2)
                    ac.glVertex2f(x2, y2 - self.trace_width - 1)
                    ac.glEnd()
            else:
                direction = ( -math.degrees( math.atan2(y1 - y2, x2 - x1)))
                dx1 = math.cos((-direction + 90) * math.pi / 180) * self.trace_width*0.5
                dy1 = math.sin((-direction + 90) * math.pi / 180) * self.trace_width*0.5
                dx2 = math.cos((-direction - 90) * math.pi / 180) * self.trace_width*0.5
                dy2 = math.sin((-direction - 90) * math.pi / 180) * self.trace_width*0.5
                ac.glBegin(acsys.GL.Quads)
                ac.glVertex2f(x1+dx1, y1-dy1)
                ac.glVertex2f(x2-dx2, y2+dy2)
                ac.glVertex2f(x2+dx2, y2-dy2)
                ac.glVertex2f(x1-dx1, y1+dy1)
                ac.glEnd()
                
        ac.ext_restoreRenderTarget()
        ac.ext_generateMips(self.render_target)

    def _shift_left(self):
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
        ac.ext_glVertexTex(0, 0, 0, 0)
        ac.ext_glVertexTex(0, self.height, 0, 1)
        ac.ext_glVertexTex(self.width, self.height, 1, 1)
        ac.ext_glVertexTex(self.width, 0, 1, 0)
        ac.glEnd()

