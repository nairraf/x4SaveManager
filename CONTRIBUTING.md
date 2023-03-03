# Quick Guidelines for contributing to this project

## Issues

Feel free to create any issues for any enhancement requests or bugs you discover.

You can also scan through the existing issues to see if there are any you feel you can help out with.

## Pull Request

If you would like to help out with coding, then just create a pull request, making sure that you link the PR with an issue. Please also select the "allow maintainer edits" so the branch can be updated for a merge.

Once you submit a PR, please allow some time for review and/or further discussions if needed.

## Development QuickStart

VSCode was used with the pylint and python extensions. A launch.json and settings.json is included in the .vscode directory so that you can easily debug the application properly, just choose the debug profile called 'Python: x4SaveManager' in VsCode, and you can press F5 to launch and debug.

* make sure you have python 3 installed 
  (3.11 was used for the initial development, also tested on 3.10)
* 'git clone' this repository into a folder of your choosing
* create a new python venv in the same folder that contains the above git clone:
  * python -m venv .venv
* activate the new python venv
  * . .\.venv\Scripts\Activate.ps1
* then restore the pip packages:
  * 'pip install -r requirements.txt'

### Building

To build a release, you have to compile the pyinstaller bootloader so that antivirus softwares don't trigget a false positive when packaging python to an exe.

* Install Visual Studio BuildTools
  * install VisualStudio 2022 Community with the following workload
    * Desktop development with C++
        * Windows 10 SDK
        * MSVC v142
* Download the source code for the latest pyinstaller release
  * https://github.com/pyinstaller/pyinstaller/releases
* extract the pyinstaller source code zip into a folder of your choice
* open a command prompt/terminal/powershell console and CD into the bootloader folder
* activate the python venv that you want to install into
* make sure that you have the wheel package
  * pip install wheel
* compile the bootloader:
  * python ./waf all
* navigate back to the pyinstaller source code root to install pyinstaller:
  * pip install .

Once you have all the build requirements satisfied you can use build.ps1 to build x4SaveManager. build.ps1 has the following options:

* build.ps1                 - by default this will do a normal build
* build.ps1 build           - execute a normal build (same as above)
* build.ps1 clean           - removes all __pycache__, build, and dist folders to make sure the next build is a brand new build
* build.ps1 cleanbuild      - executes a clean first, then a build
* build.ps1 requirements    - builds\updates the pip requirements folder in the root

The newly built executable and required dependencies will be in the dist folder, under a folder called 'x4SaveManager'.