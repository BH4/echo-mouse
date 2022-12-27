from pynput import mouse, keyboard
import sys

from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMenuBar, QMenu, QAction, QFileDialog
from PyQt5.QtGui import QIcon

from time import sleep, time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Parameters
        self.start_x = 100
        self.start_y = 100
        self.width = 250
        self.height = 100
        self.filemenu_height = 25
        self.drag_delay = 0.02
        self.kill_check_delay = 0.02

        # Variables
        self.recording = False
        self.clicks = []  # Tuples with location and press as True release as False
        self.prev_click_time = None
        self.last_move_loc = None
        self.timing = []
        # self.moves = []
        # self.scroll = []
        # self.keys = []
        self.verbose = True
        self.repeats = 10
        self.speed_up = 10

        self.Controllers()
        self.Listeners()

        # GUI
        self.setWindowTitle("Echo Mouse")
        self.setGeometry(self.start_x, self.start_y, self.width, self.height)

        # self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.UiComponents()
        self.show()

    def Controllers(self):
        self.mouse_C = mouse.Controller()

    def Listeners(self):
        # Non-blocking pynput listeners
        # listener_mouse = mouse.Listener(
        #     on_move=self.on_move,
        #     on_click=self.on_click,
        #     on_scroll=self.on_scroll)
        listener_mouse = mouse.Listener(
            on_click=self.on_click)
        listener_mouse.start()

        # listener_keyboard = keyboard.Listener(
        #     on_press=self.on_press,
        #     on_release=self.on_release)
        listener_keyboard = keyboard.Listener(
             on_press=self.on_press)
        listener_keyboard.start()

    def UiComponents(self):
        # Define buttons
        record = QPushButton("Record\nF5", self)
        play = QPushButton("Play\nF6", self)

        # Button shape
        record.setGeometry(0, self.filemenu_height, self.width//2, self.height-self.filemenu_height)
        play.setGeometry(self.width//2, self.filemenu_height, self.width//2, self.height-self.filemenu_height)

        # Connections
        record.clicked.connect(self.record)
        play.clicked.connect(self.play)

        self.create_menu_bar()

    def create_menu_bar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        openAct = QAction(QIcon(), '&Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open file')
        openAct.triggered.connect(self.openAction)
        fileMenu.addAction(openAct)

        saveAct = QAction(QIcon(), '&Save', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Save current file')
        saveAct.triggered.connect(self.saveAction)
        fileMenu.addAction(saveAct)

        exitAct = QAction(QIcon(), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('End program')
        exitAct.triggered.connect(self.exitAction)
        fileMenu.addAction(exitAct)

        # settingsMenu = QMenu("&Settings", self)
        # menuBar.addMenu(settingsMenu)

    def saveAction(self):
        # Make sure recording is off
        if self.recording:
            self.record()

        name = QFileDialog.getSaveFileName(self, 'Save File')
        # There is a better way to ensure the file ext is right.
        name = name[0]
        if '.' in name:
            name = name.split('.')[0]
        filename = name+'.echo'
        with open(filename, 'w') as f:
            # convert button click to reasonable string
            clicks_str = []
            for c in self.clicks:
                clicks_str.append((c[0], c[1], str(c[2]), c[3]))
            f.write(str(clicks_str)+'\n')
            f.write(str(self.timing)+'\n')
            f.write(str(self.repeats)+'\n')
            f.write(str(self.speed_up)+'\n')

    def button_converter(self, button_str):
        """
        Takes in a string like Button.left and returns the correct object
        """
        if button_str == "Button.left":
            return mouse.Button.left
        elif button_str == "Button.right":
            return mouse.Button.right
        elif button_str == "Button.middle":
            return mouse.Button.middle
        return mouse.Button.unknown

    def openAction(self):
        # Make sure recording is off
        if self.recording:
            self.record()

        name = QFileDialog.getOpenFileName(self, 'Open File')[0]
        with open(name, 'r') as f:
            clicks = f.readline().strip()[2:-2].split('), (')
            timing = f.readline().strip()[1:-1].split(', ')
            self.timing = [float(x) for x in timing]
            self.repeats = int(f.readline().strip())
            self.speed_up = int(f.readline().strip())

            self.clicks = []
            for c in clicks:
                c = c.split(', ')
                self.clicks.append((int(c[0]), int(c[1]),
                                   self.button_converter(c[2][1:-1]),
                                   c[3] == 'True'))

        if self.verbose:
            print('Data from open file')
            print(self.clicks)
            print(self.timing)
            print(self.repeats)
            print(self.speed_up)

    def exitAction(self):
        QCoreApplication.quit()

    # pynput
    def on_move(self, x, y):
        if self.recording:
            print('Pointer moved to {0}'.format(
                (x, y)))

    def on_click(self, x, y, button, pressed):
        if self.recording:
            self.clicks.append((x, y, button, pressed))
            if self.prev_click_time is None:
                self.prev_click_time = time()
            else:
                t = time()
                self.timing.append(t-self.prev_click_time)
                self.prev_click_time = t

            if self.verbose:
                print('{0} at {1}'.format(
                    'Pressed' if pressed else 'Released',
                    (x, y)))

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            print('Scrolled {0} at {1}'.format(
                'down' if dy < 0 else 'up',
                (x, y)))

    def on_press(self, key):
        """
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
        except AttributeError:
            print('special key {0} pressed'.format(
                key))
        """
        if key == keyboard.Key.f5:
            self.record()
        if key == keyboard.Key.f6:
            self.play()
        if key == keyboard.Key.esc:
            self.exitAction()

    def on_release(self, key):
        print('{0} released'.format(
            key))
        # if key == keyboard.Key.esc:
        #     # Stop listener
        #     return False

    def record(self):
        self.recording = not self.recording
        print('recording is', self.recording)
        if self.recording:
            self.clicks = []
            self.prev_click_time = None
            self.timing = []

    def check_kill_location(self):
        if self.verbose:
            print('Kill check')
        sleep(self.kill_check_delay)
        if self.last_move_loc is None:
            return False

        if self.mouse_C.position != self.last_move_loc:
            print('Stopped play')
            return True
        return False

    def play(self):
        self.last_move_loc = None

        if self.recording:
            self.record()

        if self.verbose:
            print('Start replay')
        for i in range(self.repeats):
            for j, click in enumerate(self.clicks):
                x, y, button, pressed = click
                if self.check_kill_location():  # kill repeats by moving mouse at all
                    return
                self.mouse_C.position = (x, y)
                self.last_move_loc = (x, y)
                if j > 0:
                    sleep(self.timing[j-1]/self.speed_up)
                if pressed:
                    self.mouse_C.press(button)
                    sleep(self.drag_delay)
                else:
                    self.mouse_C.release(button)

            if self.verbose:
                print('Finished replay number', i+1)


app = QApplication(sys.argv)
window = MainWindow()
app.exec()
