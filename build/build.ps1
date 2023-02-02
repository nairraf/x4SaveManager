. ..\.venv\Scripts\Activate.ps1
pyinstaller -y -p ..\src\modules --noconsole -i ..\src\img\icon.ico --add-binary "..\src\img\icon.ico;img" ..\src\x4SaveManager.py