. ..\.venv\Scripts\Activate.ps1
pyinstaller -y --noconsole `
    -p ..\src\modules `
    -i ..\src\img\icon.ico `
    --add-binary "..\src\img;img" `
    --add-data "..\src\conf;conf" `
    --add-data "..\src\db;db" `
    ..\src\x4SaveManager.py