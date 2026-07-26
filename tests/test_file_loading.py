import io
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


def load_main_module():
    pynput = types.ModuleType("pynput")
    pynput.mouse = types.SimpleNamespace(Button=types.SimpleNamespace(unknown=object()))
    pynput.keyboard = types.SimpleNamespace()
    sys.modules["pynput"] = pynput

    qtcore = types.ModuleType("PyQt5.QtCore")
    qtcore.QSize = qtcore.Qt = object()
    qtcore.QCoreApplication = types.SimpleNamespace(quit=Mock())
    qtwidgets = types.ModuleType("PyQt5.QtWidgets")
    for name in (
        "QApplication",
        "QMainWindow",
        "QPushButton",
        "QLabel",
        "QLineEdit",
        "QMenuBar",
        "QMenu",
        "QAction",
        "QFileDialog",
    ):
        setattr(qtwidgets, name, type(name, (), {}))
    qtgui = types.ModuleType("PyQt5.QtGui")
    qtgui.QIcon = qtgui.QIntValidator = qtgui.QDoubleValidator = object
    pyqt5 = types.ModuleType("PyQt5")
    sys.modules.update(
        {"PyQt5": pyqt5, "PyQt5.QtCore": qtcore, "PyQt5.QtWidgets": qtwidgets, "PyQt5.QtGui": qtgui}
    )

    module = types.ModuleType("echo_mouse_main")
    source = (Path(__file__).parents[1] / "main.py").read_text()
    exec(source.rsplit("\napp = QApplication(sys.argv)", 1)[0], module.__dict__)
    return module


class OpenActionTests(unittest.TestCase):
    def test_malformed_echo_file_is_ignored_without_changing_recording(self):
        module = load_main_module()
        with tempfile.NamedTemporaryFile("w", suffix=".echo") as echo_file:
            echo_file.write("not a click list\nnot a timing list\nnot an integer\nnot a float\n")
            echo_file.flush()

            window = module.MainWindow.__new__(module.MainWindow)
            window.recording = False
            window.verbose = True
            window.clicks = [(1, 2, None, True)]
            window.timing = [1.0]
            window.repeats = 2
            window.speed_up = 3.0
            window.change_repeat = Mock()
            window.change_speed_up = Mock()

            with patch.object(
                module.QFileDialog, "getOpenFileName", return_value=(echo_file.name, ""), create=True
            ):
                with redirect_stdout(io.StringIO()):
                    module.MainWindow.openAction(window)

        self.assertEqual(window.clicks, [(1, 2, None, True)])
        self.assertEqual(window.timing, [1.0])
        self.assertEqual(window.repeats, 2)
        self.assertEqual(window.speed_up, 3.0)
        window.change_repeat.assert_not_called()
        window.change_speed_up.assert_not_called()
