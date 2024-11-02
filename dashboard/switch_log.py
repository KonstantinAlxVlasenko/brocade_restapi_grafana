import database as db
from typing import Dict, List

from .base_toolbar import BaseToolbar



class SwitchLog:
    """
    Class contains switch log.
    Switch log loaded from the initiator_filename on exporter initialization.
    On each iteration new entries are added to switch log and saved to the initiator_filename (if new entries appeared).
    If the log size exceeds the threshold then oldestentries are removed from the log.

    Attributes:
        initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
    """


    def __init__(self, initiator_filename: str) -> None:
        """
        Args:
            initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
        """

        # number of the last log entry in the log dashboard
        self._last_entry_id = 0
        # filename where switch log is stored
        self._sw_log_filename = initiator_filename + db.SWITCH_LOG_FILENAME_EXT

        if db.file_exist(db.SWITCH_LOG_DIR, self.sw_log_filename):
            print(f'Load switch log from {self.sw_log_filename=}')
            self._saved_log = db.load_object(db.SWITCH_LOG_DIR, self.sw_log_filename)
        else:
            print("Create empty switch log")
            self._saved_log = dict()

        # add current logs to the loaded switch_log
        self._current_log = {'port-name': list(), 
                             'current-value': list(),
                             'previous-value': list()}
        # log change flag
        # shows if on current iteration log need to be save to the file
        self._current_log_empty = True


    def _reset_current_log(self) -> None:
        """Method resets current_log dictionary.
        All logs ate empty lists

        Args:
            None

        Returns: None
        """

        self._current_log = {key: list() for key in self.current_log}
        self._current_log_empty = True


    def align_current_log(self) -> None:
        """Method aligns each dictionary in current_log sections with log_unit_keys and section_key.
        Then removes duplicate dictionaries in each log section.
        
        Args:
            None

        Returns: None
        """

        # section key defined by log section name
        section_keys = {'port-name': 'port-name', 
                        'current-value': BaseToolbar.current_value_key, 
                        'previous-value': BaseToolbar.previous_value_key}
        
        for section in self.current_log:
            # make copy of current log section to align it
            log_section = self.current_log[section].copy() 
            # align each dictionary in log section with log_unit_keys and section_key 
            log_section = [SwitchLog.align_dct(dct, BaseToolbar.log_unit_keys + [section_keys[section]]) for dct in log_section]
            # drop duplicate dictionaries in current log section
            log_section = SwitchLog.remove_list_duplicates(log_section)
            # assign new log section to current_log 
            self.current_log[section] = log_section.copy()


    def get_unit_removal_candidates(self) -> List[dict]:
        """Method filters 'current-value' log entries which is removed after new log entries are added.
        Unique port unit entries are withdrawn from the removed 'current-value' log entries.
        
        Args:
            None

        Returns: List[dict]
        """

        # get how many slots are left in the log after adding new log entries
        spare_entries_number = self.get_log_spare_entries_number()

        unit_removal_candidates_lst = []
        # if log size exceeds the threshold find entries to remove
        if spare_entries_number < 0:
            # combine loaded and current logs
            total_log_entries_lst = self.saved_log['current-value'] + self.current_log['current-value'] \
                if self.saved_log.get('current-value') else self.current_log['current-value']
            # oldest log entries to remove from the log 
            removed_log_entries_lst = total_log_entries_lst[:abs(spare_entries_number)]
            for log_entry in removed_log_entries_lst:
                # get unit entry from the removed 'current-value' log entry
                current_unit_dct = SwitchLog.align_dct(log_entry, BaseToolbar.log_unit_keys)
                # if unit is a port and unique add it to the unit_removal_candidates
                if current_unit_dct.get('slot-number') is not None and \
                    not current_unit_dct in unit_removal_candidates_lst:
                    unit_removal_candidates_lst.append(current_unit_dct)
        return unit_removal_candidates_lst


    def get_log_spare_entries_number(self) -> int:
        """Method returns how many entries are left in the switch log after adding current log entries.
        If log size exceeds the threshold spare entries number is negative.
        
        Args:
            None

        Returns: int
        """

        # entries number of the switch log 
        saved_log_entries_number = len(self.saved_log['current-value']) if self.saved_log.get('current-value') else 0
        # entries number in the current iteration log
        current_log_entries_number = len(self.current_log['current-value'])
        # free log slots number
        spare_entries_number = db.MAX_SWITCH_LOG_LINES - (saved_log_entries_number + current_log_entries_number)
        return spare_entries_number


    def add_current_to_switch_log(self) -> None:
        """Method adds current log entries to the switch log if section is not empty.
        Log is limited to MAX_SWITCH_LOG_LINES. If log size exceeds the threshold oldest entries are removed.
        
        Args:
            None

        Returns:
            None
        """

        for key in self.current_log:
            if not self.current_log[key]:
                continue
            
            # set empty_log flag to False if section is not empty
            self._current_log_empty = False
            # backup log section
            bckp_log_section = self.saved_log[key].copy() if self.saved_log.get(key) else list()
            # create empty limited list
            log_section = db.LimitedList(max_size=db.MAX_SWITCH_LOG_LINES)
            # add backup log section to the limited list
            log_section.extend(bckp_log_section)
            # add current log section to the limitied list
            log_section.extend(self.current_log[key].copy())
            # convert limited list to the regular list
            log_section = list(log_section)
            # add limited list to the switch_log under current key
            self.saved_log[key] = log_section.copy()


    def clean_portname_section(self, unit_removal_candidates_lst: List[Dict[str, str]])-> None:
        """Methods checks units from unit_removal_candidates_lst and if they are not in current-value log section
        but still present in port-name log section removes it from the port-name log section.

        Args:
            unit_removal_candidates_lst (List[Dict[str, str]]): List of port units which entries was deleted from the current-value log section 
                                                                but still may be in the port-name log section. 
                                                                As well as other entries in current-value log section may contain these port units.
                                                                Than that units remain in port-name log section.
        
        Returns: 
            None
        """

        if not self.saved_log.get('current-value'):
            return
        if not self.saved_log.get('port-name'):
            return
        if not unit_removal_candidates_lst:
            return

        # current-value log section units
        current_value_unit_entries = [SwitchLog.align_dct(dct, BaseToolbar.log_unit_keys) for dct in self.saved_log['current-value']]
        # port-name log section units
        port_name_unit_entries = [SwitchLog.align_dct(dct, BaseToolbar.log_unit_keys) for dct in self.saved_log['port-name']]

        # check each cndidate unit for removal from unit_removal_candidates_lst
        for unit_removal_candidate in unit_removal_candidates_lst:
            # if unit candidate is not in the current-value log section
            if not unit_removal_candidate in current_value_unit_entries and \
            unit_removal_candidate in port_name_unit_entries: # but unit candidate is in the port-name log section
                # then it's ghost unit and should be removed
                # record the index of the ghost unit
                remove_unit_index = port_name_unit_entries.index(unit_removal_candidate)
                # port-name log section and port_name_unit_entries list elements indexes must match during loop iterations
                # that's why element is not deleted from the port-name log section but reset to None value
                self.saved_log['port-name'][remove_unit_index] = None
        
        # remove None values from the port-name log section
        self.saved_log['port-name'] = [port_name_entry for port_name_entry in self.saved_log['port-name'] if port_name_entry]

        # if port-name log section is empty delete the section from the log
        if not self.saved_log['port-name']:
            del self.saved_log['port-name']


    def write_switch_log(self) -> None:
        """Method writes the switch log to the file if log entry is added on current iteration
        Args: 
            None
        
        Returns: 
            None
        """
        
        if not self.current_log_empty:
            db.save_object(self.saved_log, db.SWITCH_LOG_DIR, self.sw_log_filename)


    def import_current_log(self) -> None:
        """Method aligns current switch log (current iteration log) to correspond switch log format, 
        adds current log entries to the switch log, 
        removes ghost units from port-name section of the combined switch log and current log,
        writes combined switch log to the file in the databse folder and resets current log sections to empty lists.
        
        Args:
            None

        Returns:
            None
        """

        # align current log to switch log sections format
        self.align_current_log()
        # current-value log section units which should be removed if log size threshold exceeds  
        unit_removal_candidates_lst = self.get_unit_removal_candidates()
        # add current log entries to the switch log with remove oldest entries if log size threshold exceeds
        self.add_current_to_switch_log()
        # remove ghost units from port-name section of the combined switch log and current log
        self.clean_portname_section(unit_removal_candidates_lst)
        # write updated switch log to the file in the database folder if new entries were added
        self.write_switch_log()
        # currrent log sections are reset to empty lists and empty flag is set to True
        self._reset_current_log()


    @staticmethod
    def align_dct(dct: dict, keys: list) -> dict:
        """Method to extract from dictionary required key, value pairs only.
        If key is not in dictionary None value is used in the new dictionary.
        
        Args:
            dct (dict): dictionary to extract key, values from.
            keys (list): keys to extract from the dictionary.

        Returns: dict
        """
        return {k: dct.get(k) for k in keys}


    @staticmethod
    def remove_list_duplicates(lst: list) -> list:
        """Method to remove duplicates from the list.
        
        Args:
            lst (list): initial list.

        Returns: duplicates free list
        """

        result = []
        [result.append(item) for item in lst if item not in result]
        return result


    @property
    def sw_log_filename(self):
        return self._sw_log_filename
    

    @property
    def last_entry_id(self):
        return self._last_entry_id


    @property
    def current_log_empty(self):
        return self._current_log_empty
    

    @property
    def current_log(self):
        return self._current_log
    

    @property
    def saved_log(self):
        return self._saved_log

    