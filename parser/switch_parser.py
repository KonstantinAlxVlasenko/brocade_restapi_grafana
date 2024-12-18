import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

from .base_parser import BaseParser

from collection.switch_telemetry_request import SwitchTelemetryRequest


class SwitchParser(BaseParser):
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
    
    FABRIC_SWITCH_LEAFS = ['domain-id', 'fcid-hex', 'name', 'ip-address', 'fcip-address', 'principal', 
                           'path-count', 'firmware-version']

    # 'chassis-wwn', 'switch-user-friendly-name', 'chassis-user-friendly-name', 



    
    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        super().__init__(sw_telemetry)
        self._fc_switch: dict = self._get_fc_switch_value()
        self._vf_details: dict = self._get_vf_details()
        if self.fc_switch:
            self._set_default_counters()
            self._set_switch_role()
            self._set_switch_mode()
            self._set_switch_state()
            self._set_mode_status()
            self._set_uptime_hrf()
            self._set_uptime_status()
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
                    current_sw_dct = {key: fc_sw[key] for key in SwitchParser.FC_SWITCH_LEAFS}
                    current_sw_dct['switch-wwn'] = fc_sw['name']
                    current_sw_dct['switch-name'] = fc_sw['user-friendly-name']
                    # current_sw_dct['uport-gport-enabled-quantity'] = 0
                    # current_sw_dct['enabled-port-quantity'] = 0
                    # current_sw_dct['online-port-quantity'] = 0
                    # current_sw_dct['port-physical-state-status-id'] = None
                    if fc_logical_sw_container_lst:
                        # find logical switch dictionary with the same switch wwn
                        for fc_logical_sw in fc_logical_sw_container_lst:
                            if sw_wwn == fc_logical_sw['switch-wwn']:
                                current_logical_sw_dct = {key: fc_logical_sw[key] for key in SwitchParser.FC_LOGICAL_SWITCH_LEAFS}
                                # fc_logical_sw 'port-member-list' is a dictionary with single key 'port-member' and value is a list of ports
                                current_logical_sw_dct['port-member-list'] = fc_logical_sw['port-member-list']['port-member']
                                current_logical_sw_dct['port-member-quantity'] = len(fc_logical_sw['port-member-list']['port-member'])
                                # add logical switch parameters to switch parameters dictionary for current vf_id
                                current_sw_dct.update(current_logical_sw_dct)
                    # if vf mode is disabled and fc_interface container is retrieved from the switch all ports are in the single switch
                    if fc_sw['vf-id'] == -1:
                        if not self.sw_telemetry.fc_interface.get('error') and self.sw_telemetry.fc_interface[vf_id].get('Response'):
                            current_sw_dct['port-member-quantity'] = len(self.sw_telemetry.fc_interface[vf_id]['Response']['fibrechannel'])
                        else:
                            current_sw_dct['port-member-quantity'] = None
                        
                    # fill switch paremeters dictionary with empty values for missing keys (switch parameters)
                    none_dct = {key: current_sw_dct.get(key) for key in SwitchParser.FC_LOGICAL_SWITCH_LEAFS if not current_sw_dct.get(key)}
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


    def _get_vf_details(self) -> Dict[str, Union[str, int]]:
        """
        Method retrieves vf details (values for vf_details_keys).
        
        Returns:
            {dict}: vf details for each virtual switch on the chassis
        """
        
        vf_details_keys = ['switch-name', 'switch-wwn', 'vf-id', 'fabric-user-friendly-name']
        vf_details_dct = {}
        if not self.fc_switch:
            return
        
        for vf_id, sw_params_dct in self.fc_switch.items():
            vf_details_dct[vf_id] = {key: sw_params_dct[key] for key in vf_details_keys}
        return vf_details_dct


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
                up_time_str = SwitchParser.seconds_to_hrf(sw_params_dct['up-time'])
                up_time_days, up_time_hours, up_time_mins = SwitchParser.seconds_to_dhm(sw_params_dct['up-time'])
            else:
                up_time_str, up_time_days, up_time_hours, up_time_mins = (None,)* 4
            sw_params_dct['up-time-hrf'] = up_time_str
            sw_params_dct['up-time-d'] = up_time_days
            sw_params_dct['up-time-hr'] = up_time_hours
            sw_params_dct['up-time-min'] = up_time_mins


    def _set_uptime_status(self, min_uptime: int=10, max_uptime: int=525600) -> None:
        """"
        Method sets switch uptime status.
        Uptime is less than 10 min -> switch uptime status is 'Critical' (switch reboot occured).
        Uptime is more than 10 min and less than 1 year -> switch uptime status is 'OK' (switch is up and running).
        Uptime is more than 1 year -> switch uptime status is 'Warning' (switch should be rebooted).
        Otherwise switch uptime status is 'Unknown'.
        
        Args:
            min_uptime (int): switch in critial status until timer is expired (10 minutes by default).
            max_uptime (int): switch in warning status after timer is expired (1 year by default).
        
        Returns:
            None
        """

        for sw_params_dct in self.fc_switch.values():
            uptime_seconds = sw_params_dct['up-time']
            if uptime_seconds is None:
                uptime_status_id = 2
            # switch uptime is less than 10 minutes. Critical status
            elif uptime_seconds < min_uptime * 60:
                uptime_status_id = 4
            # switch uptime is more then 10 mins and less than 1 year.  Normal operation. OK status.
            elif uptime_seconds >= min_uptime * 60 and uptime_seconds < max_uptime * 60:
                uptime_status_id = 1
            # switch uptime is more then 1 year. Switch should be rebooted. Warning status.
            elif uptime_seconds >= max_uptime * 60:
                uptime_status_id = 3
            # othewise switch uptime status is Unknown.
            else:
                uptime_status_id = 2
            
            sw_params_dct['up-time-status-id'] = uptime_status_id
            sw_params_dct['up-time-status'] = SwitchParser.STATUS_ID[uptime_status_id]


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


    def _set_default_counters(self):
        """
        Method adds counters with default values to each switch parameters dictionary.
        Port quantity counters are set to 0, port status id values are set to None.
        
        Returns:
            None
        """

        sw_default_counters = {'uport-gport-enabled-quantity': 0,
                                'enabled-port-quantity': 0,
                                'online-port-quantity': 0,
                                'port-physical-state-status-id': None,
                                'in-throughput-status-id': None,
                                'out-throughput-status-id': None,
                                'high-severity-errors_port-status-id': None,
                                'medium-severity-errors_port-status-id': None, 
                                'low-severity-errors_port-status-id': None,
                                'temperature-status-id': None, 
                                'remote-media-temperature-status-id': None,
                                'rx-power-status-id': None,
                                'tx-power-status-id': None,
                                'remote-media-rx-power-status-id': None,
                                'remote-media-tx-power-status-id': None
                                }

        for sw_params_dct in self.fc_switch.values():
            if not sw_params_dct:
                continue
            sw_params_dct.update(sw_default_counters)


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
        
        # 'chassis-wwn', 'switch-user-friendly-name', 'chassis-user-friendly-name'

        # switches in the fabric (fabricshow) for each vf_id (fabric_id)
        fabric_dct = {}

        for vf_id, fabric_telemetry in self.sw_telemetry.fabric_switch.items():
            if fabric_telemetry.get('Response'):
                # list of dictionaries for each switch in the fabric (fabricshow) for vf_id (fabric_id)
                fabric_container_lst = fabric_telemetry['Response']['fabric-switch']
                # list of dictionaries for each switch in the fabric (fabricshow) for vf_id (fabric_id) (required parameters only)
                current_fabric_lst = []
                sw_details = self.get_switch_details(vf_id)

                for fc_sw in fabric_container_lst:
                    current_sw_dct = {key: fc_sw[key] for key in SwitchParser.FABRIC_SWITCH_LEAFS}
                    current_sw_dct['fabric-id'] = vf_id
                    # current_sw_dct['switch-wwn'] = current_sw_dct['name']
                    current_sw_dct['fabric-switch-wwn'] = fc_sw['name']
                    # current_sw_dct['switch-name'] = current_sw_dct['switch-user-friendly-name']
                    current_sw_dct['fabric-switch-name'] = fc_sw['switch-user-friendly-name']
                    current_sw_dct['fabric-chassis-wwn'] = fc_sw['chassis-wwn']
                    current_sw_dct['fabric-chassis-user-friendly-name'] = fc_sw['chassis-user-friendly-name']
                    current_sw_dct.update(sw_details)
                    # add switch dictionary to the current_fabric_lst
                    current_fabric_lst.append(current_sw_dct)
                # add list of swithes in the current fabric to to the total fabrics dictionary
                fabric_dct[vf_id] = current_fabric_lst
        return fabric_dct


    def get_switch_details(self, vf_id: int, keys=['switch-name', 'switch-wwn', 'vf-id', 'fabric-user-friendly-name']) -> Dict[str, Optional[str]]:
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


    def update_param_status(self, vf_id: int, param_status_name: str, status_id: int) -> None:
        """
        Method to set port parameter global status. 
        Method takes the value of the highest port parameter status id (worst case).
        
        Args:
            vf_id {int}: switch vf_id.
            param_status_name {str}: parameter status name.
            status_id {int}: parameter status id. 1 - OK, 2 - Unknown, 3 - Warning, 4 - Critical.
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with switchparameters values.
        """

        # current status id
        param_status_id = self.fc_switch[vf_id][param_status_name]
        # if global status id is not defined (method was not called before), set it to status_id
        if param_status_id is None:
            self.fc_switch[vf_id][param_status_name] = status_id
        else:
            # if currect status id is higher than global status id, set it to currect status id
            if status_id > param_status_id:
                self.fc_switch[vf_id][param_status_name] = status_id


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
    
    
    @staticmethod
    def seconds_to_dhm(seconds: int) -> str:
        """
        Method returns seconds to days, hours, minutes.
        
        Args:
            seconds: seconds number to convert
        
        Returns:
            Tuple of days, hours, minutes
        """
        
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60
        
        days = seconds // seconds_in_day
        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
        return days, hours, minutes


    @property
    def fc_switch(self):
        return self._fc_switch
    
    
    @property
    def fabric(self):
        return self._fabric
    

    @property
    def vf_details(self):
        return self._vf_details

    
