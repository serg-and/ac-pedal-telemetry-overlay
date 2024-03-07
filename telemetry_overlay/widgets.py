import ac

from utils import console

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
