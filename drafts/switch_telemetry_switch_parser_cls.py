# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 13:36:35 2024

@author: kavlasenko
"""

import re
from typing import List, Dict, Union, Tuple
from collections import defaultdict





class BrocadeSwitchParser:
    """
    Class to create switch level parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
        fc_switc: switch parameters dictionary
        vfid_name: dictionary with fabric_name and switch_name for each vf_id in chassis
        fabric: dictionary with licenses installed on the switch
    """
    
    

    
    
    FC_SWITCH_LEAFS = ['name', 'domain-id', 'user-friendly-name', 'is-enabled-state', 
                      'up-time', 'principal', 'ip-address', 'model', 'firmware-version', 
                      'vf-id', 'fabric-user-friendly-name', 'ag-mode']
    
    FC_LOGICAL_SWITCH_LEAFS = ['base-switch-enabled',  'default-switch-status',  
                              'fabric-id', 'logical-isl-enabled', 'port-member-list']
    
    FABRIC_SWITCH_LEAFS = ['domain-id', 'fcid-hex', 'chassis-wwn', 'name', 'ip-address', 
                          'fcip-address', 'principal', 'chassis-user-friendly-name', 
                          'switch-user-friendly-name', 'path-count', 'firmware-version']
    
    
    AG_MODE = {0: 'Not supported', 1: 'Disabled', 3: 'Enabled'}

    
    def __init__(self, sw_telemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry = sw_telemetry
        # self._fc_switch, self._vfid_name = self._get_fc_switch_value()
        self._fc_switch = self._get_fc_switch_value()
        if self.fc_switch:
            self._set_switch_role()
            self._set_switch_mode()
            self._set_switch_state()
            self._set_mode_status()
            self._set_uptime_hrf()
            self._set_ipaddress_hrf()
        self._fabric = self._get_fabric_switch_value()

        
    def _get_fc_switch_value(self) -> Tuple[Dict[str, Dict[str, Union[str, int]]], Dict[int, Dict[str, str]]]:
        """
        Method retrieves each virtual switch parameters if vf mode is enabled,
        single physical switch parameters if vf mode is disabled and 
        
        Information retrieved from the fc_switch, fc_logical_switch and fabric_switch containers if vf mode is enabled,
        from the fc_switch and fabric_switch containers if vf mode is disabled.
        
        Returns:
            Switch parameters. Dictionary of dictionaries.
            External dictionary keys are switch wwn.
            Nested dictionary keys are switch parameters names.
            If switch vf mode is disabled then logical switch related parameters are None.
            
            Vf_id details. Dictionary of dictionaries.
            External dictionary keys are logical switch vf-ids (if vf mode is disabled then vf-id is -1).
            Nested dictionary keys are fabric_name and switch_name.
        """
        

        # dictonary with switch parameters
        fc_switch_dct = {}
        # dictonary with fabric_name and switch_name for each vf_id
        # vfid_naming_dct = {}
        
        
        if self.sw_telemetry.fc_logical_switch.get('Response'):
            fc_logical_sw_container_lst = self.sw_telemetry.fc_logical_switch['Response']['fibrechannel-logical-switch']
        else:
            fc_logical_sw_container_lst = []
                        
        
        for vf_id, fc_switch_telemetry in self.sw_telemetry.fc_switch.items():
            if fc_switch_telemetry.get('Response'):
                fc_sw_container_lst = fc_switch_telemetry['Response']['fibrechannel-switch']

                for fc_sw in fc_sw_container_lst:
                    # fos_version = fc_sw['firmware-version']
                    sw_wwn = fc_sw['name']
                    
                    # vfid_naming_dct[vf_id] = {'switch-name': fc_sw['user-friendly-name'], 'fabric-name': fc_sw['fabric-user-friendly-name']}
                    current_sw_dct = {key: fc_sw[key] for key in BrocadeSwitchParser.FC_SWITCH_LEAFS}                        
                        
                    if fc_logical_sw_container_lst:
                        
                        for fc_logical_sw in fc_logical_sw_container_lst:
                            
                            if sw_wwn == fc_logical_sw['switch-wwn']:
                                current_logical_sw_dct = {key: fc_logical_sw[key] for key in BrocadeSwitchParser.FC_LOGICAL_SWITCH_LEAFS}
                                current_logical_sw_dct['port-member-list'] = current_logical_sw_dct['port-member-list']['port-member']
                                
                                current_logical_sw_dct['port-member-quantity'] = len(fc_logical_sw['port-member-list']['port-member'])
                                current_sw_dct.update(current_logical_sw_dct)
                    
                    if fc_sw['vf-id'] == -1 and not self.sw_telemetry.fc_interface.get('error'):
                        current_sw_dct['port-member-quantity'] = len(self.sw_telemetry.fc_interface[vf_id]['Response']['fibrechannel'])
                        
                        
                    none_dct = {key: current_sw_dct.get(key) for key in BrocadeSwitchParser.FC_LOGICAL_SWITCH_LEAFS if not current_sw_dct.get(key)}
                    current_sw_dct.update(none_dct)
                              
                    fc_switch_dct[vf_id] = current_sw_dct
        # return fc_switch_dct, vfid_naming_dct
        return fc_switch_dct
    
    
    def _set_ipaddress_hrf(self) -> None:
        for sw_params_dct in self.fc_switch.values():
            # print(sw_params_dct)
            if sw_params_dct.get('ip-address'):
                sw_params_dct['ip-address'] = ', '.join(sw_params_dct['ip-address']['ip-address'])
        

    def _set_uptime_hrf(self) -> None:
        
        for sw_params_dct in self.fc_switch.values():
            # print(sw_params_dct)
            if sw_params_dct['up-time'] is not None:
                up_time_str = BrocadeSwitchParser.seconds_to_txt(sw_params_dct['up-time'])
            else:
                up_time_str = None
            sw_params_dct['up-time-hrf'] = up_time_str
        


    def _set_mode_status(self) -> None:
        
        state_dct = {0: 'Disabled', 1: 'Enabled'}
        for sw_params_dct in self.fc_switch.values():
            # print(sw_params_dct)
            for key_mode_secs in ['base-switch-enabled', 'default-switch-status', 'logical-isl-enabled']:
                key_mode_hrf = re.search(r'(.+?)(?:-enabled|-status)', key_mode_secs).group(1)
                sw_params_dct[key_mode_hrf] = state_dct.get(sw_params_dct[key_mode_secs], 'Unknown')



    def _set_switch_state(self) -> None:
        
        for sw_params_dct in self.fc_switch.values():
            # print(sw_params_dct)
            if sw_params_dct.get('is-enabled-state') is None:
                switch_state = 'Unknown'
            else:
                switch_state = 'Online' if sw_params_dct['is-enabled-state'] else 'Offline'
            sw_params_dct['switch-state'] = switch_state
            



    def _set_switch_mode(self) -> None:
        
        for sw_params_dct in self.fc_switch.values():
            # print(sw_params_dct)
            if sw_params_dct['ag-mode'] == 3:
                switch_mode = 'Access Gateway'
            elif sw_params_dct['ag-mode'] in [0 , 1]:
                switch_mode = 'Native'
            else:
                switch_mode = 'Unknown'
            sw_params_dct['switch-mode'] = switch_mode
    
    
    def _set_switch_role(self) -> None:
        
        for sw_params_dct in self.fc_switch.values():
            
            # print(sw_params_dct)
            
            if sw_params_dct['principal'] == 1:
                switch_role = 'Principal'
            elif sw_params_dct['ag-mode'] == 3:
                switch_role = None
            elif sw_params_dct['principal'] == 0:
                switch_role = 'Subordinate'
            else:
                switch_role = 'Unknown'
            sw_params_dct['switch-role'] = switch_role
    
    
    
    
    
    def _get_fabric_switch_value(self) -> Dict[int, List[Dict[str, Union[str, int]]]]:
        """Method retrieves information which swithes are in the fabric with each vf_id switch 
        (vf_id = -1 if vf mode is disabled).
        
        
        Returns:
            Switches in the fabric (fabricshow) for each vf_id. Dictionary with list of dictionaries.
            External dictionary keys are vf ids.
            Value is the list of dictionaries. Eeach dictionary is a switch in the vf_id fabric.
            Nested dictionary keys are fabricshow titles (FABRIC_SWITCH_LEAFS).
            If switch vf mode is disabled vf_id is -1.
        """
        
        fabric_dct = {}



        
        for vf_id, fabric_telemetry in self.sw_telemetry.fabric_switch.items():
            if fabric_telemetry.get('Response'):
                fabric_container_lst = fabric_telemetry['Response']['fabric-switch']
                current_fabric_lst = []

                for fc_sw in fabric_container_lst:
                    current_sw_dct = {key: fc_sw[key] for key in BrocadeSwitchParser.FABRIC_SWITCH_LEAFS}
                    current_sw_dct['vf-id'] = vf_id
                    if self.fc_switch.get(vf_id):
                        current_sw_dct['fabric-user-friendly-name'] = self.fc_switch[vf_id]['fabric-user-friendly-name']
                    else:
                        current_sw_dct['fabric-user-friendly-name'] = None
                    # if self.vfid_name.get(vf_id):
                    #     current_sw_dct['fabric-name'] = self.vfid_name[vf_id]['fabric-name']
                    current_fabric_lst.append(current_sw_dct)
                    fabric_dct[vf_id] = current_fabric_lst

        return fabric_dct
    
    
    @staticmethod
    def seconds_to_txt(seconds: int) -> str:
        """
        Method converts seconds to the string format
        
        Args:
            seconds: seconds number to convert
        
        Returns:
            String in format 'x days y hrs z mins'
        """
        
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60
        
        days = seconds // seconds_in_day
        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
        
        return f"{days} day{'' if days == 1 else 's'} " +\
                f"{hours} hr{'' if hours == 1 else 's'} " +\
                f"{minutes} min{'' if minutes == 1 else 's'}"
    
    
    
    def __repr__(self):

        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"
        


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def fc_switch(self):
        return self._fc_switch
    
    
    # @property
    # def vfid_name(self):
    #     return self._vfid_name
    
    @property
    def fabric(self):
        return self._fabric
    
