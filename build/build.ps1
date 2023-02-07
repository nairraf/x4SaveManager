[CmdletBinding()]
param (
    [Parameter(Position=0)]
    [String]
    $Command="Build"
)

function clean() {
    Remove-Item -Path $PSScriptRoot\build -Force -Recurse
    Remove-Item -Path $PSScriptRoot\dist -Force -Recurse
    Remove-Item -Path $PSScriptRoot\*.spec -Force
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
    build { build }
    clean { clean }
    cleanbuild {
        clean
        build
    }
}