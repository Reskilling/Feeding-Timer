# Builds dist\Feeding-Timer.exe, a single-file Windows executable with the assets bundled.
python -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name Feeding-Timer `
    --icon assets/icon.ico `
    --add-data "assets;assets" `
    feeding_timer.py
