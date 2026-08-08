# echo-mouse
Record a sequence of mouse inputs (an echo) and play them back in the same sequence. Echos can be played back faster or slower and set to play back any number of times or set to infinitely repeat. Stopping playback early can be done with any mouse movement or the escape key. Additionally, recorded inputs and settings can be saved to an "echo" file to be loaded back in at a future time.

## Example

Orignal usage of downloading pictures from a facebook album (because this is how my family sends pictures to me).

First create the recording

https://github.com/user-attachments/assets/0f2471ed-6abd-4f47-9028-9290fb8719f6

then play back the recording with the required settings

https://github.com/user-attachments/assets/fd3739e0-b1dc-46d5-8205-7fdce79d632b


## Development
Feel free to suggest changes or open pull requests. Test files can be run with
```
python3 -m unittest discover -v
```

## echo-mouse.exe
Executable file created with Pyinstaller.
```
pyinstaller --onefile -w main.py
```


![Echo Mouse from the series Owl House](https://static.wikia.nocookie.net/the-owl-house/images/c/cb/Echo_Mouse.png/revision/latest/scale-to-width-down/1000?cb=20211115185335)


