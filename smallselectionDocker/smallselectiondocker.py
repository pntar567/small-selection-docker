from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt
from krita import Selection, DockWidget

DOCKER_TITLE = 'SmallSelection buttons'
DOCKER_ID = 'small_selection_buttons'

class DockerButton(QPushButton):
    def __init__(self, btn_name='', icon_text='', btn_tooltip=''):
        super(DockerButton, self).__init__()
        self.setText(btn_name)
        self.setIcon(Krita.instance().icon(icon_text))
        self.setToolTip(btn_tooltip)
        self.setFixedHeight(24)


class SmallSelectionButtonsDocker(DockWidget):
    def __init__(self):
        super(SmallSelectionButtonsDocker, self).__init__()

        self.setWindowTitle(DOCKER_TITLE)
        self.setFixedSize(200, 100)
        wdget = QWidget(self)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(2, 0, 2, 0)
        vbox.setSpacing(0)
        wdget.setLayout(vbox)
        
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        
        x_btn = DockerButton('x')
        x_btn.clicked.connect(lambda: self.selectDirection('x'))
        y_btn = DockerButton('y')
        y_btn.clicked.connect(lambda: self.selectDirection('y'))
        left_btn = DockerButton('', 'arrow-left', 'left')
        left_btn.clicked.connect(lambda: self.selectDirection('left'))
        right_btn = DockerButton('', 'arrow-right', 'right')
        right_btn.clicked.connect(lambda: self.selectDirection('right'))
        top_btn = DockerButton('', 'arrow-up', 'top')
        top_btn.clicked.connect(lambda: self.selectDirection('top'))
        bottom_btn = DockerButton('', 'arrow-down', 'bottom')
        bottom_btn.clicked.connect(lambda: self.selectDirection('bottom'))
        
        hbox1.addWidget(x_btn)
        hbox1.addWidget(y_btn)
        hbox1.addWidget(left_btn)
        hbox1.addWidget(right_btn)
        hbox1.addWidget(top_btn)
        hbox1.addWidget(bottom_btn)

        ref_btn = DockerButton('', 'config-canvas-only', 'convert selection to referenceImage')
        ref_btn.clicked.connect(self.on_ref_btn_clicked)
        clear_invertedArea_btn = DockerButton('', 'edit-clear-16', 'clear invertedArea')
        clear_invertedArea_btn.clicked.connect(self.clear_invertedArea)
        samplerA_btn = DockerButton('', 'krita_tool_color_sampler', 'sample screen color')
        samplerA_btn.clicked.connect(self.sample_screenColor)
        paste_selection_btn = DockerButton('', 'edit-paste', 'paste selection into same layer')
        paste_selection_btn.clicked.connect(self.pasteIntoSameLayer)
        
        hbox2.addWidget(ref_btn)
        hbox2.addWidget(clear_invertedArea_btn)
        hbox2.addWidget(samplerA_btn)
        hbox2.addWidget(paste_selection_btn)
        
        self.setWidget(wdget)
        self.setAllowedAreas(Qt.NoDockWidgetArea)
        self.setFloating(True)


    def selectDirection(self, direction:str):
        doc = Krita.instance().activeDocument()
        get_selection = doc.selection()
        if not get_selection:
            return
        new_selection = Selection()
        if direction == 'x':
            new_selection.select(doc.bounds().x(), get_selection.y(), doc.width(), get_selection.height(), 255)
        elif direction == 'y':
            new_selection.select(get_selection.x(), doc.bounds().y(), get_selection.width(), doc.height(), 255)
        elif direction == 'left':
            new_selection.select(doc.bounds().x(), get_selection.y(), get_selection.x()+get_selection.width(), get_selection.height(), 255)
        elif direction == 'right':
            new_selection.select(get_selection.x(), get_selection.y(), doc.width()-get_selection.x(), get_selection.height(), 255)
        elif direction == 'top':
            new_selection.select(get_selection.x(), doc.bounds().y(), get_selection.width(), get_selection.y()+get_selection.height(), 255)
        elif direction == 'bottom':
            new_selection.select(get_selection.x(), get_selection.y(), get_selection.width(), doc.height()-get_selection.y(), 255)
        doc.setSelection(new_selection)


    def on_ref_btn_clicked(self):
        doc = Krita.instance().activeDocument()
        if not doc.selection():
            Krita.instance().action('select_all').trigger()
        Krita.instance().action('edit_copy').trigger()
        Krita.instance().action('paste_as_reference').trigger()
        doc.waitForDone()
        Krita.instance().action('deselect').trigger()


    def clear_invertedArea(self):
        doc = Krita.instance().activeDocument()
        currentLayer = doc.activeNode()
        s = doc.selection()
        if not s:
            return
        all_s = Selection()
        all_s.select(0, 0, doc.width(), doc.height(), 255)
        all_s.symmetricdifference(s)
        doc.setSelection(all_s)
        doc.waitForDone()
        Krita.instance().action('clear').trigger()
        doc.refreshProjection()


    def sample_screenColor(self):
        qwin = Krita.instance().activeWindow().qwindow()
        pobj = qwin.findChild(QWidget,'screenColorSamplerWidget')
        wobj = pobj.findChild(QPushButton)
        wobj.click()


    def get_bytarray(self) ->bool:
        doc = Krita.instance().activeDocument()
        current_s = doc.selection()
        currentLayer = doc.activeNode()
        if not current_s:
            return
        s_x = current_s.x()
        s_y = current_s.y()
        s_w = current_s.width()
        s_h = current_s.height()
        pixdata = currentLayer.pixelData(s_x, s_y, s_w, s_h)
        for d in pixdata:
            if d != b'\x00':
                return False
        return True


    def pasteIntoSameLayer(self):
        doc = Krita.instance().activeDocument()
        current_s = doc.selection()
        currentLayer = doc.activeNode()
        if currentLayer.type() != "paintlayer":
            Krita.instance().action('deselect').trigger()
            return
        elif self.get_bytarray() == True:
            Krita.instance().action('deselect').trigger()
            return
        elif current_s:
            s = current_s.duplicate()
            Krita.instance().action('edit_copy').trigger()
            Krita.instance().action('paste_into').trigger()
            doc.setSelection(s)
        elif not current_s:
            bounds_x = currentLayer.bounds().x()
            bounds_y = currentLayer.bounds().y()
            bounds_w = currentLayer.bounds().width()
            bounds_h = currentLayer.bounds().height()
            s = Selection()
            s.select(bounds_x, bounds_y, bounds_w, bounds_h, 255)
            doc.setSelection(s)
            s1 = s.duplicate()
            doc.waitForDone()
            Krita.instance().action('edit_copy').trigger()
            Krita.instance().action('paste_into').trigger()
            doc.setSelection(s1)


    def canvasChanged(self, canvas):
        pass


