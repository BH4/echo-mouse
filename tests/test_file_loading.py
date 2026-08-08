import unittest

from bin.echo_io import load_echo
from pynput import mouse


class FileLoadingTests(unittest.TestCase):
    def test_bad_value(self):
        self.assertRaises(ValueError, load_echo, 'tests/test_files/malformed_1.echo')

    def test_bad_timing(self):
        self.assertRaises(ValueError, load_echo, 'tests/test_files/malformed_2.echo')

    def test_bad_version(self):
        self.assertRaises(ValueError, load_echo, 'tests/test_files/malformed_3.echo')

    def test_version_1_echo(self):
        clicks, timing, repeats, speed_up = load_echo('tests/test_files/version_1_save.echo')

        correct_clicks = [
            (
                627,
                19,
                mouse.Button.left,
                True
            ),
            (
                627,
                19,
                mouse.Button.left,
                False
            ),
            (
                994,
                18,
                mouse.Button.left,
                True
            ),
            (
                994,
                17,
                mouse.Button.left,
                False
            ),
            (
                651,
                24,
                mouse.Button.left,
                True
            ),
            (
                651,
                24,
                mouse.Button.left,
                False
            ),
            (
                1015,
                29,
                mouse.Button.left,
                True
            ),
            (
                1015,
                29,
                mouse.Button.left,
                False
            )
        ]

        correct_timing = [
            0.07245278358459473,
            0.7900454998016357,
            0.07219195365905762,
            0.5075364112854004,
            0.09609818458557129,
            0.6821911334991455,
            0.11220479011535645
        ]
        correct_repeats = 124
        correct_speed_up = 35.0

        self.assertEqual(clicks, correct_clicks)
        self.assertEqual(timing, correct_timing)
        self.assertEqual(repeats, correct_repeats)
        self.assertEqual(speed_up, correct_speed_up)
