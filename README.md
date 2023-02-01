# x4SaveManager Overview

x4SaveManager help to continuously backup your saves for X4 Foundations. 
This way you can see all your save gaves organized by playthrough, and each
playthrough is organized by date/time, so you can easily jump to a previous
backup if/when needed.

## Development QuickStart

VSCode was used with the pylint and python extensions. 
A launch.json and settings.json is included in the .vscode directory
so that you can debug the application properly, just choose the debug profile
called 'Python: x4SaveManager'.

* make sure you have python 3 installed 
  (3.11 was used for the initial development)
* 'git clone' into a folder of your choosing
* create a new python venv:
    * python -m venv .venv
* then restore the pip packages:
    * 'pip install -r requirements.txt'

## License

This work is licensed under the MIT license