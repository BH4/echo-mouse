import sys
import types
import unittest
from pathlib import Path


def load_main_module():
    pynput = types.ModuleType("pynput")
    pynput.mouse = types.SimpleNamespace()
    pynput.keyboard = types.SimpleNamespace()
    sys.modules["pynput"] = pynput

    qtcore = types.ModuleType("PyQt5.QtCore")
    qtcore.QSize = qtcore.Qt = object()
    qtcore.QCoreApplication = types.SimpleNamespace(quit=lambda: None)
    qtwidgets = types.ModuleType("PyQt5.QtWidgets")
    for name in (
        "QApplication", "QMainWindow", "QPushButton", "QLabel", "QLineEdit",
        "QMenuBar", "QMenu", "QAction", "QFileDialog",
    ):
        setattr(qtwidgets, name, type(name, (), {}))
    qtgui = types.ModuleType("PyQt5.QtGui")
    qtgui.QIcon = qtgui.QIntValidator = qtgui.QDoubleValidator = object
    sys.modules.update(
        {"PyQt5": types.ModuleType("PyQt5"), "PyQt5.QtCore": qtcore,
         "PyQt5.QtWidgets": qtwidgets, "PyQt5.QtGui": qtgui}
    )

    module = types.ModuleType("echo_mouse_main")
    source = (Path(__file__).parents[1] / "main.py").read_text()
    exec(source.rsplit("\napp = QApplication(sys.argv)", 1)[0], module.__dict__)
    return module


class RuntimeEstimateTests(unittest.TestCase):
    def test_includes_playback_delays_for_each_repeat(self):
        module = load_main_module()
        window = module.MainWindow.__new__(module.MainWindow)
        window.repeats = 2
        window.clicks = [(1, 1, object(), True), (1, 1, object(), False)]
        window.timing = [1.0]
        window.speed_up = 10
        window.drag_delay = 0.02
        window.repeat_delay = 0.02
        window.kill_check_delay = 0.01
        window.runtime_text = types.SimpleNamespace(setText=lambda text: setattr(window, "runtime", text))

        window.calculate_runtime()

        self.assertEqual(window.runtime, "Runtime: 0.32 (seconds)")
