# python3 -m unittest discover -v
import unittest

from main import MainWindow


class RuntimeEstimateTests(unittest.TestCase):
    def test_full_time_estimate(self):
        window = MainWindow.__new__(MainWindow)

        window.repeats = 7
        window.clicks = [
            (1, 1, object(), True),
            (1, 1, object(), False),
        ]
        window.timing = [1.0]
        window.speed_up = 10
        window.drag_delay = 0.03
        window.repeat_delay = 0.02
        window.kill_check_delay = 0.01

        estimate = window.calculate_run_length()

        self.assertEqual(estimate, "1.19 (seconds)")
