# x4SaveManager Overview

x4SaveManager help to continuously backup your saves for X4 Foundations. This way you can see all your save gaves organized by playthrough, and each playthrough is organized by date/time, so you can easily jump to a previous backup if/when needed.

The initial version was just a powershell script, but overtime i wanted to add a bunch of new features, so a complete re-write was done in python, and tkinter was used to create the GUI which allows you to easily configure and control the x4SaveManager features.

## Features

### Completed
* Create many playthroughs
  * add notes to track ideas/progress/game progress/mod details/etc
* Automates backing up X4 Saves
  * associates the auto-backups with a specific playthrough
  * add quick notes, or set a flag to mark a backup
    * the flag can be used to mark importance
    * a backup with a flag will not be auto-pruned
  * details are extracted from the backup to help tell the difference between backups
    * character name
    * in-game money
    * original save time
    * hours played so far
* each backup can have it's own notes to use however you like
* easily move backups between playthroughs in case that's needed
  * useful on first load as it will back up all saves and associated then with 
    the currently selected playthrough
* backup process takes place on a dedicated thread for application performance
  * easily start and stop the backup process loop
  * will run indefinetly according to a user specified timeframe (300 seconds)
    by default, which means x4SaveManager will look for new saves every 5 minutes
    and auto-backup any that are found. this way you can just quicksave everything
    and you will have a nice history of the progress of the current playthrough.

### TODO
* restore any previous backup to an X4 game slot and resume playback from that point

## screen shots
![main window](./doc/images/beta1/Main%20Window.png)
![Application Settings](./doc/images/beta1/Application%20Settings%20Window.png)
![Playthrough Window](./doc/images/beta1/Create_Edit%20Playthrough%20Window.png)
![Backup in progress](./doc/images/beta1/Backup%20in%20progress.png)
![Backup Window](./doc/images/beta1/Backup%20Window.png)
![Edit Backup](./doc/images/beta1/Edit%20Backup%20Window.png)

## Installation

Installation is very simply. Download the latest release and extract it into any folder on your system, and simply double click on x4SaveManager.exe to start the application

## Uninstallation

Uninstallation is very easy, as you can simply delete the folder containing X4SaveManager. Please note that doing so will not delete any of the backed up saves, or any of your playthrough configuration. 

If you want to fully delete everything, including all backups, then you will need to delete the config file, database, and backup folder as well. By default these will be located in the %LOCALAPPDATA%\x4SaveManager\Release folder. In there you sill see the config.json, x4saveManager.db SQLite database, as well as the Backups folder.

## Usage

Once x4SaveManager has been opened, you will need to create at least one playthrough. Click on File -> Create Playthrough, or in the main screen, just enter a new playthrough name and click on create. This will then allow you to add notes in the edit playthrough screen and save them.

Select the desired playthrough. Notice that in the bottom left in the status bar that the currently selected playthrough is displayed. Clicking on the top Backup menu you can now start and stop the backup process. 

From there x4SaveManager will automatically search the default save X4 save location for new saves, and start backing them up. Simply play the game, and every time the game saves anything (autosave, quick save, or saving to one of the X4 slots), x4SaveManger will back it up, and associate the backup with the currently selected playthrough.

Clicking on the top backup menu and choosing stop will stop the backup loop and return you to the main application screen. Now that you have some backups, notice that they are listed in the right side of the screen. As you select different playthroughs, only the backups for the currently selected playthrough will be displayed. you can further interect with the backups by double clicking or right clicking.

Notes and tips:
* confirm all paths and backup intervals in the application settings (Edit -> Settings)
* double click on a playthrough name to open the edit playthrough window
* double click on a backup to open the edit backup screen
* right click on the selected backups for more actions.
  * edit (edits the first selected backup)
  * Move to another playthrough
    * simply use the submenu's to choose another playthrough, and all the selected backups will be moved to that playthrough.

## How can I help?

x4SaveManager is currently in beta. Please report all bugs and/or feature requests in the Issues tracker.

If you would like to help out with any development, please read the CONTRIBUTING.md file


## License

This work is licensed under the MIT license