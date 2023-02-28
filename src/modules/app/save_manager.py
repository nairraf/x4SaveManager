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
    def __init__(self, controller: WindowController):
        """Manages the backup save process

        Args:
            controller (WindowController): the root TK controller
        """
        self.controller = controller
        self.backup_thread = None
        self.backup_in_progress = False
        self.cancel_backup = threading.Event()

    def stop_backup(self):
        self.cancel_backup.set()
        self.backup_in_progress = False
        self.controller.startpage.hide_backup_frame()
        self.controller.event_generate("<<BackupIdle>>")

    def start_backup(self):
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
    
    def start_backup_thread(self, settings, message_queue, playthrough):
        from modules.app import Model
        db = Model(self.controller, settings["APP"]['DBPATH'])

        backup_path = settings["APP"]["BACKUPPATH"]
        x4_save_path = settings["APP"]["X4SAVEPATH"]
        save_seconds = settings["APP"]["BACKUPFREQUENCY_SECONDS"]
        temp_dir = os.path.join(
            backup_path, 'temp'
        )
        
        # make sure that we have a temp dir, and it's empty
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        for file in os.scandir(temp_dir):
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
                    break

            # make sure we aren't canceled before continuing
            if self.cancel_backup.is_set():
                break
            
            # check to see if we have any x4saves that haven't been backed up
            # first - we get a list of all save files
            # second - we get the hashes for each save file
            #          and then check the DB for that hash
            # third - if the hash/file hasn't been backed up, back it up

            for file in os.scandir(x4_save_path):
                if not file.is_file() or 'xml.gz' not in file.name:
                    break

                sha256 = hashlib.sha256()
                with open(file.path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                hash = sha256.hexdigest()
                
                if db.check_backup_exists(hash):
                    break

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
                x4save_time = os.path.getctime(file.path)
                try:
                    data['processing'] = 1
                    message_queue.put(data)
                    self.controller.event_generate("<<NewQueueData>>")
                    shutil.copyfile(file.path, backup_fullpath)
                    tempfilepath = os.path.join(
                        temp_dir,
                        f'{now.strftime("%Y%m%d-%H%M%S")}.xml'
                    )
                    # extract the xml in chunks so we don't kill memory
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
                            'savegame','info','game','player','patches','universe',
                            'factions','jobs','god','controltextures','component',
                            'conections','connection','connected','offset','physics',
                            'economylog','stats','log','messages','script','md',
                            'missions','aidirector','operations','ventures',
                            'notifications','ui','signatures'
                        )
                    )
                    game_version = ''
                    original_version = ''
                    modified = ''
                    gametime = ''
                    start_type = ''
                    playername = ''
                    money = ''

                    for event, element in context:
                        if element.tag == 'game':
                            game_version = "{} build {}".format(
                                element.attrib['version'] if 'version' in element.attrib else '',
                                element.attrib['build'] if 'build' in element.attrib else ''
                            )
                            original_version = "{} build {}".format(
                                element.attrib['original'] if 'original' in element.attrib else '',
                                element.attrib['originalbuild'] if 'originalbuild' in element.attrib else ''
                            )
                            modified = element.attrib['modified'] if 'modified' in element.attrib else ''
                            gametime = element.attrib['time'] if 'time' in element.attrib else ''
                            start_type = element.attrib['start'] if 'start' in element.attrib else ''

                        if element.tag == 'player':
                            playername = element.attrib['name'] if 'name' in element.attrib else ''
                            money = element.attrib['money'] if 'money' in element.attrib else ''

                        # while we can process the whole file in a memory
                        # efficient way, for now we can stop afer info
                        # as all the details we are interested in are
                        # available at the start of the file before the universe
                        if element.tag == 'info':
                            break
                        
                        # clear the elements that we are matching on
                        # as we process the file to keep memory usage down
                        element.clear()
                    
                    del context

                    os.remove(tempfilepath)
                    timer_stop = perf_counter()
                    backup_timespan = timer_stop - timer_start
                    data['x4saves'][-1]['backup_timespan'] = backup_timespan

                    db.add_backup(
                        playthrough_id = playthrough['id'],
                        x4_filename = file.name,
                        x4_save_time = x4save_time,
                        file_hash = hash,
                        backup_time = now.timestamp(),
                        backup_filename = backup_filename,
                        backup_duration = backup_timespan,
                        game_version = game_version,
                        original_game_version = original_version,
                        playtime = gametime,
                        x4_start_type = start_type,
                        character_name = playername,
                        money = money,
                        moded = modified
                    )
                    self.controller.event_generate("<<BackupThreadStarted>>")
                except Exception as e:
                    raise e
            
            # done with this loop, get ready for the next
            data['loops'] += 1
    
