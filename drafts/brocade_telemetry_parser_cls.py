from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from typing import Dict, List, Optional, Tuple, Union


class BrocadeTelemetryParser:

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._ch_wwn = self._get_chassis_wwn()
        self._telemetry_date = self._get_telemetry_datetime('date')
        self._telemetry_time = self._get_telemetry_datetime('time')


    def _get_chassis_wwn(self) -> str:
        """
        Method extracts chassis parameters from the chassis module.
        
        Returns:
            Chassis parameters dictionary.
            Dictionary keys are CHASSIS_LEAFS. 
        """
        
        if self.sw_telemetry.chassis.get('Response'):
            return self.sw_telemetry.chassis['Response']['chassis']['chassis-wwn']
        

    def _get_telemetry_datetime(self, key: str) -> str:
        return self.sw_telemetry.chassis[key]
                
    
    def same_chassis(self, other: 'BrocadeTelemetryParser') -> bool:
        return self.ch_wwn == other.ch_wwn


    def __repr__(self):
        return (f"{self.__class__.__name__} " 
                f"ip_address: {self.sw_telemetry.sw_ipaddress}, "
                f"date: {self.telemetry_date if self.telemetry_date else 'None'}, "
                f"time: {self.telemetry_time if self.telemetry_time else 'None'}")
    

    @staticmethod
    def get_changed_ports(ports_vfid_now_dct, ports_vfid_prev_dct, changed_keys, const_keys, time_now, time_prev):
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
            port_changed_dct = BrocadeTelemetryParser.get_changed_values(port_now_dct, port_prev_dct, changed_keys)
            # add slot_port constant values to the non-empty port dictionary
            BrocadeTelemetryParser.copy_dict_values(port_changed_dct, port_now_dct, keys=const_keys)                    

            if port_changed_dct:
                # add time stamps
                port_changed_dct['time-generated-hrf'] = time_now
                port_changed_dct['time-generated-prev-hrf'] = time_prev
                # add slot_port port dictionary to the vfid dictionary
                ports_vfid_changed_dct[slot_port] = port_changed_dct
        return ports_vfid_changed_dct



    @staticmethod
    def get_changed_values(now_dct: dict, prev_dct: dict, keys: List[str], tag: str='-prev') -> dict:
        """
        Method detects if port paramters from the FC_PORT_PARAMS_CHANGED list have been changed for the current port.
        It compares port parameters of the current and previous fc port parameters dicts.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            fcport_params_port_now_dct {dict}: current fc port parameters dictionary.
            fcport_params_port_prev_dct {dict}: previous fc port parameters dictionary to find changes with. 
        
        Returns:
            dict: dictionary with changed port parameters.
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
        
        copy = False

        if ignore_empty_dest:
            if dest_dct:
                copy = True
        else:
            copy = True
                                
        if copy:
            for key in  keys:
                dest_dct[key] = source_dct[key]
        

    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def ch_wwn(self):
        return self._ch_wwn
    

    @property
    def telemetry_date(self):
        return self._telemetry_date
    

    @property
    def telemetry_time(self):
        return self._telemetry_time