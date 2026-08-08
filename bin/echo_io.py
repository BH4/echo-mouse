"""
This file handles saving and loading echo files, including rejecting
incorrectly formatted files.
"""

import json
from pynput import mouse


ALLOWED_CLICK_TYPES = {"Button.left", "Button.right", "Button.middle", "None"}


def button_converter(button_str):
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
    else:
        raise ValueError("Invalid click type")


def save_echo(filename, clicks, timing, repeats, speed_up):
    clicks_str = []
    for c in clicks:
        clicks_str.append((c[0], c[1], str(c[2]), c[3]))

    data = {
        "format": "echo_data",
        "version": 1,
        "clicks": clicks_str,
        "timing": timing,
        "repeats": repeats,
        "speed_up": speed_up,
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_echo(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("File is not a valid JSON data file")

    if not isinstance(data, dict):
        raise ValueError("Invalid file structure")

    if data.get("format") != "echo_data":
        raise ValueError("Invalid file format")

    if data.get("version") != 1:
        raise ValueError("Unsupported file version")

    clicks = data.get("clicks")
    timing = data.get("timing")
    repeats = data.get("repeats")
    speed_up = data.get("speed_up")

    if not isinstance(clicks, list):
        raise ValueError("Invalid clicks data")

    for click in clicks:
        if (
            not isinstance(click, list)
            or len(click) != 4
            or not isinstance(click[0], int)
            or not isinstance(click[1], int)
            or click[2] not in ALLOWED_CLICK_TYPES
            or not isinstance(click[3], bool)
        ):
            raise ValueError("Invalid click entry")
        else:
            click[2] = button_converter(click[2])

    if (not isinstance(timing, list) or
            not all(isinstance(x, (int, float)) for x in timing) or
            not len(timing) == len(clicks)-1):
        raise ValueError("Invalid timing")

    if not isinstance(repeats, int):
        raise ValueError("Invalid repeats")

    if not isinstance(speed_up, (int, float)):
        raise ValueError("Invalid speed_up")

    # JSON has no tuple type, so convert click lists back to tuples.
    clicks = [tuple(click) for click in clicks]

    return clicks, timing, repeats, speed_up
