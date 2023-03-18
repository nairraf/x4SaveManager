"""holds the SaveManager class

The SaveManager class is responsible for starting and stopping
the backup process/threads, which actively looks for new X4 saves
and backs them up
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import threading
import gzip
from lxml import etree
import os
import hashlib
import datetime
import shutil
from time import sleep, perf_counter

if TYPE_CHECKING:
    from modules.gui import WindowController

class SaveManager():
    """SaveManager Class
    """
    def __init__(self, controller: WindowController):
        """Constructor
        Manages the backup save process

        Args:
            controller (WindowController): the root TK controller
        """
        self.controller = controller
        self.backup_thread = None
        self.backup_in_progress = False
        self.cancel_backup = threading.Event()
        self.temp_dir = os.path.join(
            self.controller.app_settings.get_app_setting(
                'BACKUPPATH'
            ),
            'temp'
        )

    def inventory_saves(self):
        x4_save_path = self.controller.app_settings.get_app_setting('X4SAVEPATH')
        inventory = []
        for file in os.scandir(x4_save_path):
            if (
                not file.is_file() or 
                'xml.gz' not in file.name or
                'temp_save' in file.name
            ):
                continue
            
            sha256 = hashlib.sha256()
            with open(file.path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            hash = sha256.hexdigest()
            
            inventory.append({
                'save_file': file,
                'backup': self.controller.db.get_backup_by_hash(hash)
            })
        return inventory
    
    def import_backups(self):
        message = """Are you sure you want to start the import process?

Note: this may take some time to re-import and re-index all previous backups
"""
        self.controller.show_question(message)

        # check the answer, exit if the user selected no
        if not self.controller.check_modal():
            return
        
        self.controller.set_cursor(type='wait')
        self.controller.event_generate("<<ImportingBackups>>")
        self.controller.update()
        backup_root = self.controller.app_settings.get_app_setting('BACKUPPATH')

        playthroughs_deleted = False

        if not os.path.exists(backup_root):
            self.controller.show_error('Cannot Find backup folder. Please check your settings')
            return
        
        for file in os.scandir(backup_root):
            if '.xml.gz' not in file.name:
                continue
            
            timer_start = perf_counter()
            now = datetime.datetime.now()

            hash = self.compute_file_hash(file.path)

            # test to see if the backup already exists and skip if it exists
            if self.controller.db.get_backup_by_hash(hash):
                continue

            id = file.name.split('_')[0].replace('id', '')

            # if the playthrough ID exists don't set the delete flag
            # if not, then set the delete flag and let the user move them

            if self.controller.db.get_playthrough_by_id(id):
                deleted_flag = False
            else:
                deleted_flag = True
                playthroughs_deleted = True

            details = self.extract_backup_details(
                backup_fullpath=file.path
            )

            timer_stop = perf_counter()
            backup_timespan = timer_stop - timer_start

            self.controller.db.add_backup(
                playthrough_id = id,
                x4_filename = 'unknown - imported',
                x4_save_time = details['save_time'],
                file_hash = hash,
                backup_time = now.timestamp(),
                backup_filename = file.name,
                backup_duration = backup_timespan,
                game_version = details['game_version'],
                original_game_version = details['original_version'],
                playtime = details['gametime'],
                x4_start_type = details['start_type'],
                character_name = details['playername'],
                money = details['money'],
                moded = details['modified'],
                delete = deleted_flag
            )
        
        self.controller.event_generate("<<BackupIdle>>")
        self.controller.set_cursor(type='')
        if playthroughs_deleted:
            self.controller.show_message("""import complete

Note: Some backups did not have a matching playthrough
      These backups have had their delete flag set,
      please verify the items in the __RECYCLE BIN__
""")
        else:
            self.controller.show_message('import complete')

    def mark_old_backups(self, silent=False):
        """Tries to find backups that can be pruned.
        Sets the deleted flag for all backups that can be pruned
        
        Args:
            silent (bool): default False. set to True to display a message if
                            no deletion candidiate backups are found
        """
        old_backups = self.controller.db.get_old_backups()
        last_backups = self.controller.db.get_latest_backups()
        marked = 0
        if old_backups:
            for backup in old_backups:
                # make sure this backup is not one of the latest backups
                # we never mark for deletion ond of the latest backups
                # configure the number to keep in the backup settings
                if backup['file_hash'] in last_backups:
                    continue

                marked += 1
                self.controller.db.backup_set_delete(
                    backup['file_hash']
                )
            self.controller.show_message("Marked {} Old Backups For Deletion".format(
                marked
            ))
            return
        if not silent:
            self.controller.show_message("No Backups were candidates for deletion with the current settings")
    
    def delete_backups(self, silent=False):
        """Deletes all backups that have been marked for deletion
        
        Args:
            silent (bool): default False. set to True to hide all confirmation messages
        """
        backups_to_delete = self.controller.db.get_backups_to_delete()

        if len(backups_to_delete) == 0:
            if not silent:
                self.controller.show_message("There are no backups marked for deletion")
            return False
        
        if not silent:
            self.controller.show_question("""Are you sure you want to delete all backups that have been marked for deletion?

WARNING: this will delete both the backup file and the database entry.
WARNING: this action cannot be reversed.
""")
            if not self.controller.check_modal():
                self.controller.show_message("Deletion Cancelled")
                return False
        
        try:
            deletion_error = False
            for backup in backups_to_delete:
                perform_delete = False
                backup_file_path = os.path.join(
                    self.controller.app_settings.get_app_setting('BACKUPPATH'),
                    backup['backup_filename']
                )

                if (
                    self.controller.app_settings.get_app_setting(
                        'DELETE_QUICKSAVES',
                        category="BACKUP"
                    ) 
                    and backup['x4_filename'].startswith('quicksave')
                    and not backup['flag']
                ):
                    perform_delete = True

                if (
                    self.controller.app_settings.get_app_setting(
                        'DELETE_AUTOSAVES',
                        category="BACKUP"
                    ) 
                    and backup['x4_filename'].startswith('autosave')
                    and not backup['flag']
                ):
                    perform_delete = True

                if (
                    self.controller.app_settings.get_app_setting(
                        'DELETE_SAVES',
                        category="BACKUP"
                    ) 
                    and backup['x4_filename'].startswith('save')
                    and not backup['flag']
                ):
                    perform_delete = True

                if perform_delete:
                    os.remove(backup_file_path)
                    self.controller.db.delete_backup(backup['file_hash'])
                else:
                    deletion_error = True
            
            if deletion_error and not silent:
                self.controller.show_message("""Current settings are prohibiting the deletion of
 one or more of the backups marked for deletion.

Review which save types to delete in settings under backup settings
and validate the the backups you want to delete are not flagged (flag = True)
""")
            return True
        except Exception as e:
            self.controller.show_error(e)
            return False

    def stop_backup(self):
        """Stops the backup process/thread
        """
        self.cancel_backup.set()
        self.backup_in_progress = False
        self.controller.startpage.hide_backup_frame()
        self.controller.event_generate("<<BackupIdle>>")
        self.controller.startpage.populate_tree()

    def start_backup(self):
        """starts the backup process/thread
        """
        self.cancel_backup.clear()
        self.controller.startpage.set_progress_count(0)
        self.backup_in_progress = True
        self.controller.startpage.show_backup_frame()
        self.backup_thread = threading.Thread(
            target=self.start_backup_thread,
            args=(
                self.controller.app_settings.app_settings,
                self.controller.message_queue,
                self.controller.selected_playthrough
            )
        )
        self.controller.event_generate("<<BackupThreadStarted>>")
        self.backup_thread.start()
    
    def restore_backup(self, backup_filename, x4_save_slot):
        """resotres a backup to a given X4 save location

        Args:
            backup_filename (str): the backup filename to restore
            x4_save_slot (str): the x4 save name to restore to
        """
        message=f"""
Are you sure you want to restore backup: {backup_filename}
and overwrite the following X4 save file: {x4_save_slot}?

WARNING: this will overwrite the X4 save file if it exists.
"""
        self.controller.show_question(message)
        if not self.controller.check_modal():
            self.controller.show_message("Restore Cancelled")
            return
        
        # restore backup to the requested slot
        backup_path = os.path.join(
            self.controller.app_settings.get_app_setting('BACKUPPATH'),
            backup_filename
        )
        x4_save_path = os.path.join(
            self.controller.app_settings.get_app_setting('X4SAVEPATH'),
            f"{x4_save_slot}.xml.gz"
        )
        if not os.path.exists(backup_path):
            self.controller.show_error("Backup file not found, Restore Failed")
            return
        
        if not os.path.exists(self.controller.app_settings.get_app_setting('X4SAVEPATH')):
            self.controller.show_error("X4 Save Folder not found, Restore Failed")
            return
        
        try:
            shutil.copyfile(backup_path, x4_save_path)
            self.controller.show_message("Backup Successfully restored to X4 slot {}".format(
                x4_save_slot
            ))
        except Exception as e:
            self.controller.show_error(e)
        

    def start_backup_thread(self, settings, message_queue, playthrough):
        """This is the main backup process which is handed to a dedicated
        thread.
        
        Args:
            settings (AppSettings): an instance of AppSettings to access the 
                                    main application settings from a seperate
                                    thread
            message_queue (Queue): a thread save queue to pass messages back 
                                   and forth between threads
            playthrough (List): an instance of the currently selected playthrough
        """
        from modules.app import Model
        db = Model(self.controller, settings["APP"]['DBPATH'])

        backup_path = settings["APP"]["BACKUPPATH"]
        x4_save_path = settings["APP"]["X4SAVEPATH"]
        save_seconds = settings["BACKUP"]["BACKUPFREQUENCY_SECONDS"]
        
        # make sure that we have a temp dir, and it's empty
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        for file in os.scandir(self.temp_dir):
            if '.xml' in file.name:
                os.remove(file.path)

        # create our data dictionary that we return through the messaging queue
        # and enter the main backup loop
        data = {}
        data['loops'] = 0
        data['x4saves'] = []
        while True:
            countdown = save_seconds
            data['processing'] = 0
            # sleep while we wait for the next loop
            while countdown  >= 0:
                self.controller.event_generate("<<UpdateBackupProgress>>")
                data['countdown'] = countdown
                countdown -= 1
                message_queue.put(data)
                self.controller.event_generate("<<NewQueueData>>")

                sleep(1)
                if self.cancel_backup.is_set():
                    self.controller.event_generate("<<RefreshBackupTreeview>>")
                    break

            # make sure we aren't canceled before continuing
            if self.cancel_backup.is_set():
                self.controller.event_generate("<<RefreshBackupTreeview>>")
                break
            
            # check to see if we have any x4saves that haven't been backed up
            # first - we get a list of all save files
            # second - we get the hashes for each save file
            #          and then check the DB for that hash
            # third - if the hash/file hasn't been backed up, back it up

            for file in os.scandir(x4_save_path):
                if (
                    not file.is_file() or 
                    'xml.gz' not in file.name or
                    'temp_save' in file.name
                ):
                    continue
                
                hash = self.compute_file_hash(file.path)
                
                if db.check_backup_exists(hash):
                    continue

                # file has not been backed up
                # get the now time
                self.controller.event_generate("<<BackupRunning>>")
                now = datetime.datetime.now()
                timer_start = perf_counter()
                backup_filename = "id{}_{}.xml.gz".format(
                        playthrough['id'],
                        now.strftime("%Y%m%d-%H%M%S")
                )
                backup_fullpath = os.path.join(
                    backup_path,
                    backup_filename
                )
                data['x4saves'].append({
                    'x4save': file.name,
                    'backup_filename': backup_filename,
                    'hash': hash
                })

                try:
                    data['processing'] = 1
                    message_queue.put(data)
                    self.controller.event_generate("<<NewQueueData>>")
                    shutil.copyfile(file.path, backup_fullpath)
                    
                    details = self.extract_backup_details(
                        backup_fullpath=backup_fullpath
                    )

                    timer_stop = perf_counter()
                    backup_timespan = timer_stop - timer_start
                    data['x4saves'][-1]['backup_timespan'] = backup_timespan

                    db.add_backup(
                        playthrough_id = playthrough['id'],
                        x4_filename = file.name,
                        x4_save_time = details['save_time'],
                        file_hash = hash,
                        backup_time = now.timestamp(),
                        backup_filename = backup_filename,
                        backup_duration = backup_timespan,
                        game_version = details['game_version'],
                        original_game_version = details['original_version'],
                        playtime = details['gametime'],
                        x4_start_type = details['start_type'],
                        character_name = details['playername'],
                        money = details['money'],
                        moded = details['modified']
                    )
                    self.controller.event_generate("<<BackupThreadStarted>>")
                except Exception as e:
                    raise e
            
            # done with this loop, get ready for the next
            data['loops'] += 1
    
    def compute_file_hash(self, file_path):
        sha256 = hashlib.sha256()
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()

    def extract_backup_details(self, backup_fullpath):
        """uncompresses an X4 save file and extracts details from the XML
        
        Args:
            backup_fullpath (str): the full path to the backed up X4 save file
            tempfilepath (str): the full path to temporary extracted backup file
        """
        save_details = {
            'save_time': '',
            'game_version': '',
            'original_version': '',
            'modified': '',
            'gametime': '',
            'start_type': '',
            'playername': '',
            'money': ''
        }

        now = datetime.datetime.now()

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        tempfilepath = os.path.join(
            self.temp_dir,
            f'{now.strftime("%Y%m%d-%H%M%S")}.xml'
        )

        # extract the xml to a temp file in chunks so we don't kill memory
        with gzip.open(backup_fullpath, 'rb') as f_in:
            with open(tempfilepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out, 4096)
        
        #search the xml in a memory friendly way
        context = etree.iterparse(
            tempfilepath,
            # in order to save memory as we process the save file
            # we have to match on all major tags and clear them
            # from memory as we go, searching and recording what we need
            # this way the element.clear() calls works as expected
            # and it can clear no-longer needed elements from memory
            tag=(
                'savegame','info','save','game','player','patches','universe',
                'factions','jobs','god','controltextures','component',
                'conections','connection','connected','offset','physics',
                'economylog','stats','log','messages','script','md',
                'missions','aidirector','operations','ventures',
                'notifications','ui','signatures'
            )
        )
        
        for event, element in context:
            if element.tag == 'save':
                save_details['save_time'] = element.attrib['date'] if 'date' in element.attrib else ''
            
            if element.tag == 'game':
                save_details['game_version'] = "{} build {}".format(
                    element.attrib['version'] if 'version' in element.attrib else '',
                    element.attrib['build'] if 'build' in element.attrib else ''
                )
                save_details['original_version'] = "{} build {}".format(
                    element.attrib['original'] if 'original' in element.attrib else '',
                    element.attrib['originalbuild'] if 'originalbuild' in element.attrib else ''
                )
                save_details['modified'] = element.attrib['modified'] if 'modified' in element.attrib else ''
                save_details['gametime'] = element.attrib['time'] if 'time' in element.attrib else ''
                save_details['start_type'] = element.attrib['start'] if 'start' in element.attrib else ''

            if element.tag == 'player':
                save_details['playername'] = element.attrib['name'] if 'name' in element.attrib else ''
                save_details['money'] = element.attrib['money'] if 'money' in element.attrib else ''

            # while we can process the whole file in a memory
            # efficient way, for now we can stop afer info
            # as all the details we are interested in are
            # available at the start of the file before the universe
            if element.tag == 'info':
                element.clear()
                break
            
            # clear the elements that we are matching on
            # as we process the file to keep memory usage down
            element.clear()
        
        del context
        os.remove(tempfilepath)

        return save_details
