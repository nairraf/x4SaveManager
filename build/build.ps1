[CmdletBinding()]
param (
    [Parameter(Position=0)]
    [String]
    $Command="Build"
)

function clean() {
    if (Test-Path -Path $PSScriptRoot\build) {
        Remove-Item -Path $PSScriptRoot\build -Force -Recurse
    }
    if (Test-Path -Path $PSScriptRoot\dist) {
        Remove-Item -Path $PSScriptRoot\dist -Force -Recurse
    }
    if (Test-Path -Path $PSScriptRoot\*.spec) {
        Remove-Item -Path $PSScriptRoot\*.spec -Force
    }
    if (Test-Path -Path $PSScriptRoot\..\src\modules\app\__pycache__) {
        Remove-Item -Path $PSScriptRoot\..\src\modules\app\__pycache__ -Force -Recurse
    }
    if (Test-Path -Path $PSScriptRoot\..\src\modules\gui\__pycache__) {
        Remove-Item -Path $PSScriptRoot\..\src\modules\gui\__pycache__ -Force -Recurse
    }
}

function remove-pyinstaller() {
    . $PSScriptRoot\..\.venv\Scripts\Activate.ps1

    pip uninstall altgraph pefile pyinstaller pyinstaller-hooks-contrib pywin32-ctypes -y
}

function requirements() {
    # rebuilds the requirements.txt file in the project root
    . $PSScriptRoot\..\.venv\Scripts\Activate.ps1

    pip freeze --exclude setuptools `
               --exclude pip `
               --exclude pyinstaller `
               --exclude altgraph `
               --exclude pefile `
               --exclude pyinstaller-hooks-contrib `
               --exclude wheel `
               --exclude pywin32-ctypes > $PSScriptRoot\..\requirements.txt
}

function build() {
    Set-Location $PSScriptRoot
    . ..\.venv\Scripts\Activate.ps1

    pyinstaller -y --noconsole `
        -p ..\src\modules `
        -i ..\src\img\icon.ico `
        --add-binary "..\src\img;img" `
        ..\src\x4SaveManager.py
}

switch ($Command) {
    build {
        requirements
        build 
    }
    clean { clean }
    cleanbuild {
        clean
        requirements
        build
    }
    requirements {
        requirements
    }
    remove-pyinstaller {
        remove-pyinstaller
    }
}