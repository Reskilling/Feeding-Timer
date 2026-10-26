# Feeding-Timer

Feeding-Timer is a small desktop app that shows whether your pet has been fed and
counts down to the next meal. Tap the bowl after feeding, and the app shows a
countdown until the next feeding window starts. The app uses a fixed 800×480
window that you can switch to fullscreen.

This README is for anyone who wants to run the app from source or adapt it for
their own pet.

![Feeding-Timer after feeding: "Jake has been fed" with a countdown to the next meal, the feeding time, and an Undo link.](docs/screenshot.png)

## Download for Windows

To run the app without installing Python, download `Feeding-Timer.exe` from the
[latest release](https://github.com/Reskilling/Feeding-Timer/releases/latest)
and open it.

The rest of this README covers running the app from source.

## Requirements

- Python 3.6 or later, with Tkinter. Tkinter is included with the standard
  Python installers for Windows and macOS. On Debian or Ubuntu, install the
  `python3-tk` package.
- [Pillow](https://pypi.org/project/pillow/)

## Install

1. Clone the repository:

   ```sh
   git clone https://github.com/Reskilling/Feeding-Timer.git
   ```

2. Go to the project directory:

   ```sh
   cd Feeding-Timer
   ```

3. Install Pillow:

   ```sh
   pip install pillow
   ```

## Run the app

To start the app, run the following command:

```sh
python feeding_timer.py
```

The window shows "Time to feed Jake" and a food bowl.

## Record a feeding

1. After you feed your pet, tap the bowl.

   The title changes to "Jake has been fed", and the app shows a countdown to
   the next meal and the time you fed your pet.

2. Optional: If you tapped the bowl by mistake, tap **Undo**.

When the countdown reaches zero, the app returns to "Time to feed Jake" and the
bowl reappears.

The countdown ends at the next feeding window:

| If you tap the bowl | The countdown ends at |
|---|---|
| Before 06:00 | 06:00 the same day |
| From 06:00 until 16:30 | 16:30 the same day |
| At or after 16:30 | 06:00 the next day |

The app remembers the last feeding, so closing it or restarting your computer
doesn't reset the countdown. On Windows, the feeding is saved in
`%APPDATA%\Feeding-Timer\state.json`; on Linux and macOS, it's saved in
`~/.local/share/Feeding-Timer/state.json`. Tapping **Undo** deletes the saved
feeding.

## Use fullscreen mode

- To enter or leave fullscreen, tap the arrows icon in the top-right corner.
- To leave fullscreen from the keyboard, press **Esc**.

## Customize the app

To change the app's behavior, edit the `AppConfig` class in `feeding_timer.py`.
The following settings are available:

| Setting | Description | Default |
|---|---|---|
| `PET_NAME` | The name shown in the status messages. | `"Jake"` |
| `APP_TITLE` | The window title. | `"Feeding-Timer"` |
| `RESET_TIME_MORNING` | The start of the morning feeding window, as `(hour, minute)`. | `(6, 0)` |
| `RESET_TIME_EVENING` | The start of the evening feeding window, as `(hour, minute)`. | `(16, 30)` |
| `WINDOW_SIZE` | The window size in pixels, as `(width, height)`. Match it to your background image. | `(800, 480)` |
| `UPDATE_INTERVAL` | How often the countdown refreshes, in milliseconds. | `1000` |

To change text sizes, weights, or colors, edit the `Styles` class. To move
text, edit the `Layout` class.

To use your own artwork, replace `assets/background.png` and `assets/bowl.gif`.

## Run the tests

To run the unit tests, run the following command from the project directory:

```sh
python -m unittest discover -s tests
```

## Build the Windows executable

1. Install PyInstaller:

   ```sh
   pip install pyinstaller
   ```

2. From the project directory, run the build script in PowerShell:

   ```powershell
   ./build.ps1
   ```

The script creates `dist/Feeding-Timer.exe`, a single file that includes the
images and font.

## License

This project is licensed under the MIT License. For details, see
[LICENSE](LICENSE).

The app bundles the [Nunito](https://github.com/googlefonts/nunito) font, which
is licensed under the SIL Open Font License 1.1. For details, see
[assets/fonts/OFL.txt](assets/fonts/OFL.txt).
