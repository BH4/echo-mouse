from pynput import mouse, keyboard
import sys

from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QMenuBar, QMenu, QAction, QFileDialog
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from threading import Thread

from time import sleep, time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Parameters
        self.kill_tol = 4
        self.start_x = 100
        self.start_y = 100
        self.filemenu_height = 25
        self.runtime_height = 25
        self.button_height = 75
        self.input_height = 50
        self.width = 300
        self.height = self.filemenu_height+self.runtime_height+self.input_height+self.button_height

        self.drag_delay = 0.02
        self.kill_check_delay = 0.01

        # Variables
        self.recording = False
        self.save_path = False
        self.playing = False
        self.curr_pressed = set()
        self.prev_click_time = None

        self.clicks = []  # Tuples with location and press as True release as False
        self.last_move_loc = None
        self.timing = []
        # self.moves = []
        # self.scroll = []
        # self.keys = []
        self.verbose = True
        self.repeats = 1
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
            on_move=self.on_move,
            on_click=self.on_click)
        listener_mouse.start()

        # listener_keyboard = keyboard.Listener(
        #     on_press=self.on_press,
        #     on_release=self.on_release)
        listener_keyboard = keyboard.Listener(
             on_press=self.on_press)
        listener_keyboard.start()

    def UiComponents(self):
        # Define elements
        self.runtime_text = QLabel("Runtime: 0 (s)", self)

        record = QPushButton("Record\nF5", self)
        play = QPushButton("Play\nF6", self)

        repeats = QLineEdit(str(self.repeats), self)
        repeat_label = QLabel("Repeats:", self)
        speed_up = QLineEdit(str(self.speed_up), self)
        speed_up_label = QLabel("Speed up:", self)

        # Element shapes
        curr_top = self.filemenu_height
        self.runtime_text.setGeometry(20, curr_top, self.width-40, 30)

        curr_top += self.runtime_height
        mid = self.width//2
        record.setGeometry(0, curr_top, mid, self.button_height)
        play.setGeometry(mid, curr_top, mid, self.button_height)

        curr_top += self.button_height+10
        label_space = 80
        repeats.setGeometry(label_space-10, curr_top, mid-label_space, 30)
        repeat_label.setGeometry(20, curr_top, label_space-20, 30)

        speed_up.setGeometry(mid+label_space-12, curr_top, mid-label_space+2, 30)
        speed_up_label.setGeometry(mid+10, curr_top, label_space-10, 30)

        # Connections
        record.clicked.connect(self.record)
        play.clicked.connect(self.play)

        repeats.setValidator(QIntValidator(0, 99999))
        repeats.editingFinished.connect(self.repeat_changed)
        speed_up.setValidator(QDoubleValidator(0.0001, 1000.0, 4))
        speed_up.editingFinished.connect(self.speed_up_changed)

        self.repeats_input = repeats
        self.speed_up_input = speed_up

        self.create_menu_bar()

    def unit_convert(self, tot_time):
        # tot_time starts in seconds
        units = 'seconds'
        if tot_time > 60:
            tot_time /= 60
            units = 'minutes'

            if tot_time > 60:
                tot_time /= 60
                units = 'hours'

                if tot_time > 24:
                    tot_time /= 24
                    units = 'days'

                    if tot_time > 365.25:
                        tot_time /= 365.25
                        units = 'years'

        return str(round(tot_time, 2))+' ('+units+')'

    def calculate_runtime(self):
        """
        Uses the click timing, number of repeats, and speedup fraction to
        estimate the full runtime and set the label text accordingly.

        Currently doesn't take finite time of code into account
        """
        if self.repeats == 0:
            estimate = "Infinite"
        else:
            num_presses = len([x for x in self.clicks if x[3]])
            drag_delay_time = self.drag_delay*num_presses
            kill_check_delay = self.kill_check_delay*len(self.clicks)
            repeat_time = self.repeats*sum(self.timing)/self.speed_up
            sec_estimate = drag_delay_time+repeat_time+kill_check_delay
            estimate = self.unit_convert(sec_estimate)  # Gives a string with attached units

        self.runtime_text.setText("Runtime: "+estimate)

    def change_repeat(self, v):
        if v == 0:
            self.repeats_input.setText('Infinite')
            self.infAct.setChecked(True)
        else:
            self.repeats_input.setText(str(v))
            self.infAct.setChecked(False)
        self.repeats = v

        if self.verbose:
            print('Repeats changed to:', self.repeats)

        self.calculate_runtime()

    def repeat_changed(self):
        int_value = int(self.repeats_input.text())
        self.change_repeat(int_value)

    def change_speed_up(self, v):
        self.speed_up_input.setText(str(v))
        self.speed_up = v

        if self.verbose:
            print('Speed up changed to:', self.speed_up)

        self.calculate_runtime()

    def speed_up_changed(self):
        float_val = float(self.speed_up_input.text())
        self.change_speed_up(float_val)

    def create_menu_bar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        # File
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

        # Settings
        settingsMenu = QMenu("&Settings", self)
        menuBar.addMenu(settingsMenu)

        infAct = QAction(QIcon(), '&Infinite', self)
        infAct.setShortcut('Ctrl+I')
        infAct.setStatusTip('Infinite Repeats')
        infAct.triggered.connect(self.infAction)
        infAct.setCheckable(True)
        settingsMenu.addAction(infAct)
        self.infAct = infAct

        copyPathAct = QAction(QIcon(), '&Copy Full Path', self)
        copyPathAct.setShortcut('Ctrl+P')
        copyPathAct.setStatusTip('Repeat exact mouse movements')
        copyPathAct.triggered.connect(self.copyPathAction)
        copyPathAct.setCheckable(True)
        settingsMenu.addAction(copyPathAct)

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
        elif button_str == "None":
            return None
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
            self.speed_up = float(f.readline().strip())

            self.clicks = []
            for c in clicks:
                c = c.split(', ')
                self.clicks.append((int(c[0]), int(c[1]),
                                   self.button_converter(c[2][1:-1]),
                                   c[3] == 'True'))

        self.change_repeat(self.repeats)
        self.change_speed_up(self.speed_up)
        if self.verbose:
            print('Data from open file')
            print(self.clicks)
            print(self.timing)
            print(self.repeats)
            print(self.speed_up)

    def exitAction(self):
        QCoreApplication.quit()

    def infAction(self):
        if self.recording:
            print('Cannot change settings while recording.')
            return

        if self.repeats > 0:
            self.change_repeat(0)
        else:
            self.change_repeat(1)

    def copyPathAction(self):
        if self.recording:
            print('Cannot change settings while recording.')
            return

        self.save_path = not self.save_path

    # pynput
    def on_move(self, x, y):
        if self.recording and self.save_path:
            self.clicks.append((x, y, None, None))

            if self.prev_click_time is None:
                self.prev_click_time = time()
            else:
                t = time()
                self.timing.append(t-self.prev_click_time)
                self.prev_click_time = t

            if self.verbose:
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
        if self.recording:
            print('Starting recording')
            self.clicks = []
            self.prev_click_time = None
            self.timing = []

            self.runtime_text.setText("Runtime: Recording...")
        else:
            print('Recording ended')

            self.calculate_runtime()

    def check_kill_location(self):
        if self.verbose:
            print('Kill check')
        sleep(self.kill_check_delay)
        if self.last_move_loc is None:
            return False

        dx = self.mouse_C.position[0]-self.last_move_loc[0]
        dy = self.mouse_C.position[1]-self.last_move_loc[1]
        if dx**2+dy**2 > self.kill_tol**2:
            print('Stopped play')
            self.playing = False
            return True
        return False

    def play(self):
        if self.playing:
            return

        self.playing = True
        thread = Thread(target=self.play_thread)
        thread.start()

    def play_thread(self):
        runtime_test = time()
        self.last_move_loc = None
        self.curr_pressed = set()

        if self.recording:
            print('Cannot play while recording')
            return

        if self.verbose:
            print('Start replay')

        # repeats = 0 functions as infinite repeats until stopped.
        count = 0
        while self.repeats == 0 or count < self.repeats:
            count += 1

            for j, click in enumerate(self.clicks):
                x, y, button, pressed = click
                if self.check_kill_location():  # kill repeats by moving mouse
                    # Release buttons that are pressed
                    for b in self.curr_pressed:
                        self.mouse_C.release(b)
                    return
                self.mouse_C.position = (x, y)
                self.last_move_loc = (x, y)

                if j > 0:
                    sleep(self.timing[j-1]/self.speed_up)
                if pressed is not None:  # Not just a movement
                    if pressed:
                        self.mouse_C.press(button)
                        self.curr_pressed.add(button)
                        sleep(self.drag_delay)
                    else:
                        self.mouse_C.release(button)
                        self.curr_pressed.discard(button)

            if self.verbose:
                print('Finished replay number', count)

        if self.verbose:
            print('True runtime:', time()-runtime_test)

        self.playing = False


app = QApplication(sys.argv)
window = MainWindow()
app.exec()
