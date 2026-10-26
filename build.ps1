# Builds dist\Feeding-Timer.exe, a single-file Windows executable with the assets bundled.
Push-Location $PSScriptRoot
try {
    python -m PyInstaller --noconfirm --clean --onefile --windowed `
        --name Feeding-Timer `
        --icon assets/icon.ico `
        --add-data "assets;assets" `
        feeding_timer.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
