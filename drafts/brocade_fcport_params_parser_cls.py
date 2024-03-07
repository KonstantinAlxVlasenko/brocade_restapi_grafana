# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 13:01:32 2024

@author: kavlasenko
"""

import re
from typing import Dict, List, Tuple, Union, Optional

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser

class BrocadeFCPortParametersParser:
    """
    Class to create fc port parameters dictionaries to imitate port status from switchshow output.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        sw_parser: switch parameters retrieved from the sw_telemetry.
        port_owner: dictonary with port name as key and switchname to which port belongs to as value.
        port_status: fc port parameters dictionary.
    """

    FC_INTERFACE_LEAFS = ['wwn', 'name', 'pod-license-status', 'is-enabled-state', 'persistent-disable', 
                          'auto-negotiate', 'speed', 'max-speed', 'neighbor-node-wwn']
    
    PORT_TYPE_ID = {0: 'Unknown',
                    7: 'E-Port',
                    10: 'G-Port',
                    11: 'U-Port',
                    15: 'F-Port',
                    16: 'L-Port',
                    17: 'FCoE Port',
                    19: 'EX-Port',
                    20: 'D-Port',
                    21: 'SIM Port',
                    22: 'AF-Port',
                    23: 'AE-Port',
                    25: 'VE-Port',
                    26: 'Ethernet Flex Port',
                    29: 'Flex Port',
                    30: 'N-Port',
                    32768: 'LB-Port'}
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, sw_parser: BrocadeSwitchParser):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._sw_parser: BrocadeSwitchParser = sw_parser
        self._port_owner = self._get_ports_owner()
        self._fcport_params = self. _get_port_params_values()


    def _get_ports_owner(self) -> Dict[str, Union[int, str]]:
        """
        Method creates ports owner (switchname) dictionary.
        
        Returns:
            dict: Dictonary with port name as key and switchname to which port belongs to as value.
        """

        port_owner_dct = {}
        for fc_sw in self.sw_parser.fc_switch.values():
            if fc_sw.get('port-member-list'):
                sw_name = fc_sw['user-friendly-name']
                port_member_lst = fc_sw['port-member-list']
                current_sw_port_owner_dct = {port: sw_name for port in port_member_lst}
                port_owner_dct.update(current_sw_port_owner_dct)
        return port_owner_dct
    
    
    def _get_port_params_values(self) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method retrieves each fc port parameters and status.
        
        Returns:
            dict: FC port parameters. Dictionary of dictionaries of dictionaries.
                External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
                First level nested dictionary keys are slot_port_numbers.
                Second level nested dictionary keys are fc port parameters names.
        """
        
        fcport_params_dct = {}

        for vf_id, fc_interface_telemetry in self.sw_telemetry.fc_interface.items():
            if fc_interface_telemetry.get('Response'):
                # list with fc_interface containers for the each port in the vf_id switch
                fc_interface_container_lst = fc_interface_telemetry['Response']['fibrechannel']
                fcport_params_dct[vf_id] = {}
                
                for fc_interface_container in fc_interface_container_lst:
                    # slot_port_number in the format 'slot_number/port_number' (e.g. '0/1')
                    slot_port_number = fc_interface_container['name']
                    # split slot and port number
                    slot_number, port_number = slot_port_number.split('/')
                    # drop leading '0x' from the port id value (e.g. '0x030100')
                    port_fcid = re.search('0x(.+)', fc_interface_container['fcid-hex']).group(1)
                    # convert speed from bps to gbps
                    port_max_speed = int(fc_interface_container['max-speed']/1000_000_000)
                    port_speed = int(fc_interface_container['speed']/1000_000_000)
                    # add leading 'N' or closing 'G' to the port_seed value
                    port_speed = BrocadeFCPortParametersParser._label_auto_fixed_speed_mode(port_speed, fc_interface_container['auto-negotiate'])
                    # join wwns conneected to the port
                    # neighbor_port_wwn = ', '.join(fc_interface_container['neighbor']['wwn']) if fc_interface_container['neighbor'] else None
                    neighbor_port_wwn = fc_interface_container['neighbor']['wwn'] if fc_interface_container['neighbor'] else None
                    # port owner (remove closing '.')
                    sw_name = self._get_port_owner(slot_port_number, vf_id)
                    # dynamic or static portname
                    port_name = fc_interface_container['user-friendly-name'].rstrip('.')
                    # port enabled or disabled
                    port_enable_status = BrocadeFCPortParametersParser._get_port_enable_status(fc_interface_container)
                    # online, offline, ,faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc
                    physical_state = BrocadeFCPortParametersParser._get_port_physical_state(fc_interface_container)
                    # flag if fc port is enabled but has no device connected
                    nodevice_enabled_port_flag = BrocadeFCPortParametersParser._get_nodevice_enabled_port_flag(fc_interface_container)

                    # create dictionary with current port parameters 
                    fcport_params_current_dct = {
                        'swicth-name': sw_name,
                        'vf-id': vf_id,
                        'port-index': fc_interface_container['default-index'],
                        'slot-number': int(slot_number),
                        'port-number': int(port_number),
                        'port-name': port_name,
                        'port-id': port_fcid, 
                        'link-speed': port_speed,
                        'port-max-speed-gbps': port_max_speed,
                        'physical-state': physical_state,
                        'port-type': BrocadeFCPortParametersParser.PORT_TYPE_ID.get(fc_interface_container['port-type'], fc_interface_container['port-type']),
                        'neighbor-port-wwn': neighbor_port_wwn,
                        'port-enable-status': port_enable_status,
                        'nodevice-enabled-port': nodevice_enabled_port_flag
                        }
                    # dictionary with unchanged values from fc_interface_container
                    fcport_params_current_default_dct = {leaf: fc_interface_container.get(leaf) for leaf in BrocadeFCPortParametersParser.FC_INTERFACE_LEAFS}
                    fcport_params_current_dct.update(fcport_params_current_default_dct)
                    # add current port status dictionary to the summary port status dictionary with vf_id and slot_port as consecutive keys
                    fcport_params_dct[vf_id][fc_interface_container['name']] = fcport_params_current_dct
        return fcport_params_dct


    @staticmethod
    def _get_nodevice_enabled_port_flag(fc_interface_container):
        """
        Method to check if fc port is enabled but has no device connected. 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            int: 1 if fc port is enabled but has no device connected.
                0 in all other cases.
        """

        if fc_interface_container['is-enabled-state'] and not fc_interface_container['neighbor']:
            return 1
        else:
            return 0


    @staticmethod
    def _get_port_physical_state(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[str]:
        """
        Method to get the physical state of the port 
        (online, offline, ,faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc). 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            str: Physical state of the port 
                (online, offline, ,faulty, no_module, laser_flt, no_light, no_sync, in_sync, mod_inv, mod_val etc).
        """  

        if fc_interface_container.get('physical-state'):
            # capitalize each segment of the string to correspond to the physical state in switchshow output
            physical_state = fc_interface_container['physical-state'].split('_')
            physical_state = [symbol.capitalize() for symbol in physical_state]
            physical_state = '_'.join(physical_state)
            return physical_state


    @staticmethod
    def _get_port_enable_status(fc_interface_container: Dict[str, Optional[Union[str,int]]]) -> Optional[str]:
        """
        Method to get port enable status ('Enabled', 'Disabled', 'Disabled (Persistent)'). 
        
        Args:
            fc_interface_container {dict}: container with fc port parameters leafs.
        
        Returns:
            str: Port enable status ('Enabled', 'Disabled', 'Disabled (Persistent)')
        """        

        if fc_interface_container['is-enabled-state'] is None:
            port_enable_status = None
        elif fc_interface_container['is-enabled-state']:
            port_enable_status = 'Enabled'
        else:
            port_enable_status = 'Disabled'
            if fc_interface_container['persistent-disable']:
                port_enable_status = port_enable_status + ' (Persistent)'
        return port_enable_status

    
    def _get_port_owner(self, slot_port_number: str, vf_id: int) -> Optional[str]:
        """
        Method to get slot_port_number switchname owner.
        
        Args:
            slot_port_number {str}: slot and port number in the format'slot/port' (e.g. '0/1').
                                    vf_id: switch vf_id.
        
        Returns:
            str: Switchname to which port belongs to.
        """

        if self.port_owner:
            sw_name = self.port_owner[slot_port_number]
        elif vf_id == -1 and self.sw_parser.fc_switch[vf_id].get('user-friendly-name'):
            sw_name = self.sw_parser.fc_switch[vf_id]['user-friendly-name']
        else:
            sw_name = None
        return sw_name
        

    @staticmethod
    def _label_auto_fixed_speed_mode(port_speed: int, auto_negotiate_mode: Optional[Union[str, int]]) -> Optional[str]: 
        """
        Method to label the port_speed value with leading 'N' or closing 'G' based on the auto-negotiate mode.
        
        Args:
            port_speed {int}: port speed value in gbps.
            auto_negotiate_mode {int}: auto-negotiate mode off(0), on (1).
        
        Returns:
            str: String in format 'Nx' or 'xG'.
        """

        if port_speed is None:
            return None
        
        if auto_negotiate_mode:
            port_speed = 'N' + str(port_speed)
        else:
            port_speed = str(port_speed) + 'G'
        return port_speed
        
        
    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def sw_parser(self):
        return self._sw_parser
    

    @property
    def port_owner(self):
        return self._port_owner
    

    @property
    def fcport_params(self):
        return self._fcport_params