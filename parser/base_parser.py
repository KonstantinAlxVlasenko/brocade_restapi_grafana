from typing import Dict, List, Literal, Optional, Tuple, Union

from collection.switch_telemetry_request import SwitchTelemetryRequest


class BaseParser:
    """
    Class to create switch telemetry parser.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    STATUS_VALUE = {'ok': 1, 'unknown': 2, 'warning': 3, 'critical': 4}

    # STATUS_VALUE = {'OK': 1, 'Unknown': 2, 'Warning': 3, 'Critical': 4}

    STATUS_ID = {1: 'OK', 2: 'Unknown', 3: 'Warning', 4: 'Critical'}

    FC_PORT_ADD_PARAMS = ['switch-name', 'switch-wwn', 'fabric-user-friendly-name', 'vf-id', 'port-name', 'physical-state', 'physical-state-id',
                        'port-enable-status', 'port-enable-status-id', 'speed', 'max-speed',
                        'port-speed-hrf', 'auto-negotiate', 'port-speed-gbps', 'port-throughput-Mbytes',
                        'port-type', 'port-type-id']
    
    FC_PORT_PATH = ['fabric-user-friendly-name', 'vf-id', 'switch-name', 'switch-wwn', 'port-name', 'name', 'slot-number', 'port-number']

    STATUS_TAG = '-status'
    STATUS_ID_TAG = '-status-id'
    PREV_TAG = '-prev'

    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
        """

        self._sw_telemetry: SwitchTelemetryRequest = sw_telemetry
        self._ch_wwn = self._get_chassis_wwn()
        self._ch_name = self._get_chassis_name()
        self._telemetry_date = self._get_telemetry_datetime('date')
        self._telemetry_time = self._get_telemetry_datetime('time')


    def _get_chassis_wwn(self) -> str:
        """
        Method extracts chassis wwn from the chassis module.
        
        Returns:
            str: chassis wwn. 
        """
        
        if self.sw_telemetry.chassis.get('Response'):
            return self.sw_telemetry.chassis['Response']['chassis']['chassis-wwn']
        

    def _get_chassis_name(self) -> str:
        """
        Method extracts chassis name from the chassis module.
        
        Returns:
            str: chassis name. 
        """
        
        if self.sw_telemetry.chassis.get('Response'):
            return self.sw_telemetry.chassis['Response']['chassis']['chassis-user-friendly-name']
        

    def _get_telemetry_datetime(self, key: Literal['date'] | Literal['time']) -> str:
        """
        Method extracts date or time from the chassis module.
        
        Returns:
            str: date, time. 
        """
        return self.sw_telemetry.chassis[key]
                
    
    def same_chassis(self, other: 'BaseParser') -> bool:
        """Method detects if two instances of BrocadeTelemetryParser class are from the same chassis.

        Args:
            other (BrocadeTelemetryParser): BrocadeTelemetryParser class instance retrieved from the previous sw_telemetry.

        Returns:
            bool: same chassis or not.
        """

        return self.ch_wwn == other.ch_wwn
    




    @staticmethod
    def get_changed_vfid_ports(ports_vfid_now_dct, ports_vfid_prev_dct, changed_keys, const_keys, time_now, time_prev):
        """
        Method filters ports where values for changed_keys are differs in ports_vfid_now_dct and ports_vfid_prev_dct.
        If value is changed then current and previous values are added to the port dictionary. 
        If changed values are present and dictionary for the port is not empty 
        then const_keys which are port_id values and timestamps are added to the port dictionary.
        
        Args:
            ports_vfid_now_dct {dict}: ports values of the certain switch vfid retrieved from the current sw_telemetry.
            ports_vfid_prev_dct {dict}: ports values of the certain switch vfid retrieved from the previous sw_telemetry.
            changed_keys {list}: keys which are checked for changed values.
            const_keys {list}: keys which are added to the non-empty port dictionary with changed values.
            time_now (str): timestamp for the current sw_telemetry.
            time_prev (str): timestamp for the previous sw_telemetry.
        
        Returns:
            dict: ports of the certain switch vfid with changed values.
        """

        ports_vfid_changed_dct = {}
        
        for slot_port, port_now_dct in ports_vfid_now_dct.items():
            # if there is no port number in previous check next slot_port
            if slot_port not in ports_vfid_prev_dct:
                continue
            
            # slot_port port values from the previous
            port_prev_dct = ports_vfid_prev_dct[slot_port]
            # find changed values for the changed_keys
            port_changed_dct = BaseParser.get_changed_values(port_now_dct, port_prev_dct, changed_keys)
            # add slot_port constant values to the non-empty port dictionary
            BaseParser.copy_dict_values(port_changed_dct, port_now_dct, keys=const_keys)                    

            if port_changed_dct:
                # add time stamps
                port_changed_dct['time-generated-hrf'] = time_now
                port_changed_dct['time-generated-prev-hrf'] = time_prev
                # add slot_port port dictionary to the vfid dictionary
                ports_vfid_changed_dct[slot_port] = port_changed_dct
        return ports_vfid_changed_dct


    @staticmethod
    def get_changed_chassis_params(now_dct, prev_dct, changed_keys, const_keys, time_now, time_prev):
        """
        Method filters ports where values for changed_keys are differs in ports_vfid_now_dct and ports_vfid_prev_dct.
        If value is changed then current and previous values are added to the port dictionary. 
        If changed values are present and dictionary for the port is not empty 
        then const_keys which are port_id values and timestamps are added to the port dictionary.
        
        Args:
            ports_vfid_now_dct {dict}: ports values of the certain switch vfid retrieved from the current sw_telemetry.
            ports_vfid_prev_dct {dict}: ports values of the certain switch vfid retrieved from the previous sw_telemetry.
            changed_keys {list}: keys which are checked for changed values.
            const_keys {list}: keys which are added to the non-empty port dictionary with changed values.
            time_now (str): timestamp for the current sw_telemetry.
            time_prev (str): timestamp for the previous sw_telemetry.
        
        Returns:
            dict: ports of the certain switch vfid with changed values.
        """

        # find changed values for the changed_keys
        chassis_changed_dct = BaseParser.get_changed_values(now_dct, prev_dct, changed_keys)
        # add constant values to the non-empty port dictionary
        BaseParser.copy_dict_values(chassis_changed_dct, now_dct, keys=const_keys)                    

        if chassis_changed_dct:
            # add time stamps
            chassis_changed_dct['time-generated-hrf'] = time_now
            chassis_changed_dct['time-generated-prev-hrf'] = time_prev

        return chassis_changed_dct


    @staticmethod
    def get_changed_values(now_dct: dict, prev_dct: dict, keys: List[str], tag: str='-prev') -> dict:
        """
        Method detects if port paramters from the keys list have been changed.
        It compares values of the current and previous dicts.
        All changed values are added to to the dictionatry including current and previous values.
        
        Args:
            now_dct {dict}: current dictionary.
            prev_dct {dict}: previous dictionary to find changes with. 
        
        Returns:
            dict: dictionary with changed values.
        """

        # dictionary with with changed port parameters 
        changed_values_dct = {}
        
        for key in keys:
            if not key in set(now_dct).intersection(prev_dct):
            # if not key in prev_dct or not key in now_dct:
                continue                                                
            if prev_dct[key] != now_dct[key]:
                changed_values_dct[key] = now_dct[key]
                changed_values_dct[key + tag] =  prev_dct[key]
        return changed_values_dct
    

    @staticmethod
    def copy_dict_values(dest_dct: dict, source_dct: dict, keys: List[str], ignore_empty_dest: bool = True) -> None:
        """Method copies values from source_dct to dest_dct.

        Args:
            dest_dct (dict): destination dictionary.
            source_dct (dict): source dictionary.
            keys (List[str]): keys which values are copied from source_dct to dest_dct.
            ignore_empty_dest (bool, optional): ignore copying to empty dest_dct. Defaults to True.
        """
        
        copy = False

        # ignore empty dest_dct flag is on
        if ignore_empty_dest:
            # copy if dest_dct is not empty
            if dest_dct:
                copy = True
        # ignore empty dest_dct flag is off
        else:
            # copy in any case 
            copy = True
                                
        if copy:
            for key in  keys:
                dest_dct[key] = source_dct[key]


    def __repr__(self):
        return (f"{self.__class__.__name__} " 
                f"ip_address: {self.sw_telemetry.sw_ipaddress}, "
                f"date: {self.telemetry_date if self.telemetry_date else 'None'}, "
                f"time: {self.telemetry_time if self.telemetry_time else 'None'}")


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def ch_wwn(self):
        return self._ch_wwn

    @property
    def ch_name(self):
        return self._ch_name


    @property
    def telemetry_date(self):
        return self._telemetry_date
    

    @property
    def telemetry_time(self):
        return self._telemetry_time