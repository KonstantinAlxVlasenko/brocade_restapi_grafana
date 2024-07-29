# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 13:36:35 2024

@author: kavlasenko
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Union, Optional

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeSwitchParser:
    """
    Class to create switch level parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
        fc_switch: switch parameters dictionary
        REMOVE: fid_name: dictionary with fabric_name and switch_name for each vf_id in chassis
        fabric: dictionary with licenses installed on the switch
    """
    
    
    FC_SWITCH_LEAFS = ['name', 'domain-id', 'user-friendly-name', 'is-enabled-state', 
                      'up-time', 'principal', 'ip-address', 'subnet-mask', 'model', 'firmware-version', 
                      'vf-id', 'fabric-user-friendly-name', 'ag-mode', 'operational-status']
    
    FC_LOGICAL_SWITCH_LEAFS = ['base-switch-enabled',  'default-switch-status',  
                              'fabric-id', 'logical-isl-enabled', 'port-member-list']
    
    FABRIC_SWITCH_LEAFS = ['domain-id', 'fcid-hex', 'chassis-wwn', 'name', 'ip-address', 
                          'fcip-address', 'principal', 'chassis-user-friendly-name', 
                          'switch-user-friendly-name', 'path-count', 'firmware-version']

    
    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        # self._fc_switch, self._vfid_name = self._get_fc_switch_value()
        self._fc_switch: dict = self._get_fc_switch_value()
        if self.fc_switch:
            self._set_switch_role()
            self._set_switch_mode()
            self._set_switch_state()
            self._set_mode_status()
            self._set_uptime_hrf()
            self._set_ipaddress_str()
        self._fabric: dict = self._get_fabric_switch_value()

        
    def _get_fc_switch_value(self) -> Dict[int, Dict[str, Union[str, int, List[str]]]]:
        """
        Method retrieves each virtual switch parameters if vf mode is enabled,
        single physical switch parameters if vf mode is disabled and 
        
        remove: Information retrieved from the fc_switch, fc_logical_switch and fabric_switch containers if vf mode is enabled,
        from the fc_switch and fabric_switch containers if vf mode is disabled.
        
        Returns:
            Switch parameters. Dictionary of dictionaries.
            External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
            Nested dictionary keys are switch parameters names.
            If switch vf mode is disabled then logical switch related parameters are None.
            
            REMOVE: Vf_id details. Dictionary of dictionaries.
            External dictionary keys are logical switch vf-ids (if vf mode is disabled then vf-id is -1).
            Nested dictionary keys are fabric_name and switch_name.
        """
        
        # switch parameters dictionary
        fc_switch_dct = {}
        
        # dictonary with fabric_name and switch_name for each vf_id
        # vfid_naming_dct = {}
        
        # list of dictionaries with logical switch parameters
        fc_logical_sw_container_lst = self._get_logical_sw_list()
        
        for vf_id, fc_switch_telemetry in self.sw_telemetry.fc_switch.items():
            if fc_switch_telemetry.get('Response'):
                # fc switch container list for current vf_id (list with single dictionary)
                fc_sw_container_lst = fc_switch_telemetry['Response']['fibrechannel-switch']
                for fc_sw in fc_sw_container_lst:
                    sw_wwn = fc_sw['name']
                    # vfid_naming_dct[vf_id] = {'switch-name': fc_sw['user-friendly-name'], 'fabric-name': fc_sw['fabric-user-friendly-name']}
                    current_sw_dct = {key: fc_sw[key] for key in BrocadeSwitchParser.FC_SWITCH_LEAFS}
                    current_sw_dct['switch-wwn'] = fc_sw['name']
                    current_sw_dct['switch-name'] = fc_sw['user-friendly-name']
                    current_sw_dct['uport-gport-enabled-quantity'] = 0
                    current_sw_dct['enabled-port-quantity'] = 0
                    current_sw_dct['online-port-quantity'] = 0
                    if fc_logical_sw_container_lst:
                        # find logical switch dictionary with the same switch wwn
                        for fc_logical_sw in fc_logical_sw_container_lst:
                            if sw_wwn == fc_logical_sw['switch-wwn']:
                                current_logical_sw_dct = {key: fc_logical_sw[key] for key in BrocadeSwitchParser.FC_LOGICAL_SWITCH_LEAFS}
                                # fc_logical_sw 'port-member-list' is a dictionary with single key 'port-member' and value is a list of ports
                                current_logical_sw_dct['port-member-list'] = fc_logical_sw['port-member-list']['port-member']
                                current_logical_sw_dct['port-member-quantity'] = len(fc_logical_sw['port-member-list']['port-member'])
                                # add logical switch parameters to switch parameters dictionary for current vf_id
                                current_sw_dct.update(current_logical_sw_dct)
                    # if vf mode is disabled and fc_interface container is retrieved from the switch all ports are in the single switch
                    if fc_sw['vf-id'] == -1 and not self.sw_telemetry.fc_interface.get('error'):
                        current_sw_dct['port-member-quantity'] = len(self.sw_telemetry.fc_interface[vf_id]['Response']['fibrechannel'])
                        
                    # fill switch paremeters dictionary with empty values for missing keys (switch parameters)
                    none_dct = {key: current_sw_dct.get(key) for key in BrocadeSwitchParser.FC_LOGICAL_SWITCH_LEAFS if not current_sw_dct.get(key)}
                    current_sw_dct.update(none_dct)
                    # add current vf_id switch parameters dictionary to the total switch parameters dictionary
                    fc_switch_dct[vf_id] = current_sw_dct
        # return fc_switch_dct, vfid_naming_dct
        return fc_switch_dct
    

    def _get_logical_sw_list(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method retrieves logical switch list.
        
        Returns:
            Logical switch list.
        """
        
        if self.sw_telemetry.fc_logical_switch.get('Response'):
            fc_logical_sw_container_lst = self.sw_telemetry.fc_logical_switch['Response']['fibrechannel-logical-switch']
        else:
            fc_logical_sw_container_lst = []
        return fc_logical_sw_container_lst


    def _set_ipaddress_str(self) -> None:
        """
        Method converts list of ip adresses to string.

        Returns:
            None
        """

        for sw_params_dct in self.fc_switch.values():
            if sw_params_dct.get('ip-address'):
                sw_params_dct['ip-address'] = ', '.join(sw_params_dct['ip-address']['ip-address'])
        

    def _set_uptime_hrf(self) -> None:
        """"
        Method converts switch uptime in seconds to the human readable format x days y hrs z mins.
        
        Returns:
            None
        """
                
        for sw_params_dct in self.fc_switch.values():
            if sw_params_dct['up-time'] is not None:
                up_time_str = BrocadeSwitchParser.seconds_to_hrf(sw_params_dct['up-time'])
            else:
                up_time_str = None
            sw_params_dct['up-time-hrf'] = up_time_str
        

    def _set_mode_status(self) -> None:
        """
        Method converts switch modes defined as 0 and 1 in switch parameters to 'Enabled' or 'Disabled' respectively.
        Endings 'enabled' or 'status' are removed from the switch mode title.
        
        Returns:
            None
        """
        
        state_dct = {0: 'Disabled', 1: 'Enabled'}
        # switch mode titles with dictionary values defined in binary format
        sw_modes_bin = ['base-switch-enabled', 'default-switch-status', 'logical-isl-enabled']

        for sw_params_dct in self.fc_switch.values():
            for sw_mode_bin in sw_modes_bin:
                # drop 'enabled' or 'status' endings from the switch mode title
                sw_mode_hrf = re.search(r'(.+?)(?:-enabled|-status)', sw_mode_bin).group(1)
                # replace binary value to the 'Enabled' or 'Disabled' string
                if sw_params_dct[sw_mode_bin] is None:
                    sw_params_dct[sw_mode_hrf] = None
                else:
                    sw_params_dct[sw_mode_hrf] = state_dct.get(sw_params_dct[sw_mode_bin], 'Unknown')


    def _set_switch_state(self) -> None:
        """
        Method sets switch state to 'Online' or 'Offline' by converting 'is-enabled-state' parameter defined as True or False of respectively.
        
        Returns:
            None
        """
        
        for sw_params_dct in self.fc_switch.values():
            if sw_params_dct.get('is-enabled-state') is None:
                switch_state = 'Unknown'
                switch_state_id = None
                sw_params_dct['switch-state-id'] = None
            else:
                switch_state = 'Online' if sw_params_dct['is-enabled-state'] else 'Offline'
                switch_state_id = 1 if sw_params_dct['is-enabled-state'] else 0
            sw_params_dct['switch-state'] = switch_state
            sw_params_dct['switch-state-id'] = switch_state_id
            

    def _set_switch_mode(self) -> None:
        """"
        Method sets switch mode to 'Native' or 'Access Gateway' by converting 'ag-mode' parameter.
        'ag-mode' = 0: 'Not supported', 1: 'Disabled', 3: 'Enabled'.
        
        Returns:
            None
        """
        
        for sw_params_dct in self.fc_switch.values():
            if sw_params_dct['ag-mode'] == 3:
                switch_mode = 'Access Gateway'
            elif sw_params_dct['ag-mode'] in [0 , 1]:
                switch_mode = 'Native'
            else:
                switch_mode = 'Unknown'
            sw_params_dct['switch-mode'] = switch_mode
    
    
    def _set_switch_role(self) -> None:
        """
        Method sets switch role based on switch parameters.
        switch disabled: 'Disabled',
        principal on: 'Principal',
        ag mode on: None,
        principal off: 'Subordinate',
        none of the above: 'Unknown'.
        
        Returns:
            None
        """

        for sw_params_dct in self.fc_switch.values():
            
            if sw_params_dct.get('is-enabled-state') is False:
                switch_role = 'Disabled'
                switch_role_id = -1
            elif sw_params_dct['principal'] == 1:
                switch_role = 'Principal'
                switch_role_id = 1
            elif sw_params_dct['ag-mode'] == 3:
                switch_role = None
                switch_role_id = None
            elif sw_params_dct['principal'] == 0:
                switch_role = 'Subordinate'
                switch_role_id = 0
            else:
                switch_role = 'Unknown'
                switch_role_id = None
            sw_params_dct['switch-role'] = switch_role
            sw_params_dct['switch-role-id'] = switch_role_id
    
    
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
        
        # switches in the fabric (fabricshow) for each vf_id (fabric_id)
        fabric_dct = {}

        for vf_id, fabric_telemetry in self.sw_telemetry.fabric_switch.items():
            if fabric_telemetry.get('Response'):
                # list of dictionaries for each switch in the fabric (fabricshow) for vf_id (fabric_id)
                fabric_container_lst = fabric_telemetry['Response']['fabric-switch']
                # list of dictionaries for each switch in the fabric (fabricshow) for vf_id (fabric_id) (required parameters only)
                current_fabric_lst = []

                for fc_sw in fabric_container_lst:
                    current_sw_dct = {key: fc_sw[key] for key in BrocadeSwitchParser.FABRIC_SWITCH_LEAFS}
                    current_sw_dct['fabric-id'] = vf_id
                    current_sw_dct['switch-wwn'] = current_sw_dct['name']
                    current_sw_dct['switch-name'] = current_sw_dct['switch-user-friendly-name']
                    # add fabric_name from the fc_switch attribute
                    if self.fc_switch.get(vf_id):
                        current_sw_dct['fabric-user-friendly-name'] = self.fc_switch[vf_id]['fabric-user-friendly-name']
                    else:
                        current_sw_dct['fabric-user-friendly-name'] = None
                    
                    # if self.vfid_name.get(vf_id):
                    #     current_sw_dct['fabric-name'] = self.vfid_name[vf_id]['fabric-name']
                    
                    # add switch dictionary to the current_fabric_lst
                    current_fabric_lst.append(current_sw_dct)
                # add list of swithes in the current fabric to to the total fabrics dictionary
                fabric_dct[vf_id] = current_fabric_lst
        return fabric_dct


    def get_switch_details(self, vf_id: int, keys=['switch-name', 'switch-wwn', 'vf-id']) -> Dict[str, Optional[str]]:
        """
        Method to get switch details.
        
        Args:
            vf_id {int}: switch vf_id.
            keys {list}: extracted switch parameters titles.
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with switchparameters values.
        """
        
        sw_details = self.fc_switch.get(vf_id)
        if sw_details:
            return {key: sw_details[key] for key in keys}
        else:
            return {key: None for key in keys}


    @staticmethod
    def seconds_to_hrf(seconds: int) -> str:
        """
        Method converts seconds to the string format.
        
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
    
    
    @property
    def fabric(self):
        return self._fabric
    

    # @property
    # def vfid_name(self):
    #     return self._vfid_name
    
