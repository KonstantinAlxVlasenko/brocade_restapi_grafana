# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 17:35:13 2024

@author: kavlasenko
"""

import re
from collections import defaultdict
from typing import Dict, List, Optional, Union

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser
from brocade_base_parser import BrocadeTelemetryParser


class BrocadeMAPSParser(BrocadeTelemetryParser):
    """
    Class to create maps parameters dictionaries and health status list.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        maps_config: active maps plicy and maps actions dictionary.
        ssp_report: Switch Status Policy report list (switch health status).
        system_resources: system resources dictionary (such as CPU, RAM, and flash memory usage).
        dashboard_rule: MAPS events or rules triggered and the objects on which the rules were triggered.
    """
    
    # Switch Status Policy report constants
    SSP_LEAFS = ['switch-health', 
                 'power-supply-health', 'fan-health', 'temperature-sensor-health', 
                 'flash-health', 
                 'marginal-port-health', 'faulty-port-health', 'missing-sfp-health', 'error-port-health', 
                 'expired-certificate-health', 'airflow-mismatch-health']
    
    _ssp_state = {'healthy': 1,  
                 'unknown': 2, 
                 'marginal': 3, 
                 'down': 4}
    
    SSP_STATE = defaultdict(lambda: BrocadeMAPSParser._ssp_state['unknown'])
    SSP_STATE.update(_ssp_state)
    
    DB_RULE_LEAFS = ['category', 'name', 'triggered-count',  'time-stamp', 
                     'repetition-count', 'object-element', 'object-value', 'severity']
    DB_RULE_IGNORE = ['CLEAR', 'UNQUAR', 'STATE_IN', 'STATE_ON', 'STATE_UP', 'BALANCED']


    SYSTEM_RESOURCE_THRESHOLDS = {'cpu-usage': 80, 'flash-usage': 85, 'memory-usage': 75}

    
    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, sw_parser: BrocadeSwitchParser, maps_parser_prev=None):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        super().__init__(sw_telemetry)
        self._sw_parser: BrocadeSwitchParser = sw_parser
        self._maps_config: dict = self._get_maps_policy_value()
        self._get_maps_actions_value()
        self._ssp_report: dict = self._get_ssp_report_value()
        self._ssp_report_parameters = self._get_ssp_report_parameters()
        self._ssp_report_changed = self._get_changed_ssp_report(maps_parser_prev)
        self._system_resources: dict = self._get_system_resource_values()
        self._system_resources_changed: dict = self._get_changed_system_resources(maps_parser_prev)
        self._dashboard_rule: dict = self._get_dashboard_rule_value()
        
        
    def _get_maps_policy_value(self) -> Dict[int, Union[str, int]]:
        """
        Method retrieves active maps policy from the maps_policy containers for each logical switch.
        
        Returns:
            Dictionary of dictionaries.
            External dictionary keys are logical switch vf-ids (if VF mode is disabled then vf-id is -1).
            Nested dictionary keys are vf-id, maps-policy.
            If maps configuration was not retrived but status code exist the maps-policy key contains error-message.
        """

        maps_config_dct = {}
        # parsing maps-policy for each logical switch
        for vf_id, maps_policy_telemetry in self.sw_telemetry.maps_policy.items():
            if maps_policy_telemetry.get('Response'):
                # check all maps policies and find single active policy
                active_policy = [vf_maps_policy['name'] 
                                 for vf_maps_policy in maps_policy_telemetry['Response']['maps-policy'] 
                                 if vf_maps_policy['is-active-policy']]
                active_policy = active_policy[0] if active_policy else None
            elif maps_policy_telemetry.get('status-code'):
                active_policy = maps_policy_telemetry['error-message']
            else:
                active_policy = None
            if active_policy:
                # add active policy or error-message dictionary to the maps configuration dictionary
                maps_config_dct[vf_id] = {'vf-id': vf_id, 'maps-policy': active_policy}
                # add switch details
                # sw_details = self._get_switch_details(vf_id)
                sw_details = self.sw_parser.get_switch_details(vf_id)
                maps_config_dct[vf_id].update(sw_details)
                
        return maps_config_dct
    


    def _get_switch_details(self, vf_id: int, keys=['switch-name', 'switch-wwn']) -> Dict[str, Optional[str]]:
        """
        Method to get switch details.
        
        Args:
            vf_id {int}: switch vf_id.
            keys {list}: extracted switch parameters titles.
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with switchparameters values.
        """
        
        sw_details = self.sw_parser.fc_switch.get(vf_id)
        if sw_details:
            return {key: sw_details[key] for key in keys}
        else:
            return {key: None for key in keys}


    def  _get_maps_actions_value(self) -> None:
        """
        Method retrieves maps actions from the maps_config containers for each logical switch.
        Retrieved maps actions are added to the maps_config attribute. 
        
        Returns:
            None
        """

        # parsing maps-actions for each logical switch
        for vf_id, maps_config_telemetry in self.sw_telemetry.maps_config.items():
            if maps_config_telemetry.get('Response'):
                maps_actions = maps_config_telemetry['Response']['maps-config']['actions']['action']
                maps_actions = ', '.join(maps_actions)
            # if maps_config_telemetry was not retrieved but status code exist the maps-actions key contains error-message
            elif maps_config_telemetry.get('status-code'):
                maps_actions = maps_config_telemetry['error-message']
            else:
                maps_actions = None
            # create 'empty' nested dictionary if logical switch is not in the maps configuration dictionary
            if maps_actions:
                if not vf_id in self.maps_config:
                    self.maps_config[vf_id] = {'vf-id': vf_id, 'maps-policy': None}
                    # add switch details
                    # sw_details = self._get_switch_details(vf_id)
                    sw_details = self.sw_parser.get_switch_details(vf_id)
                    self.maps_config[vf_id].update(sw_details)
                # add maps configuration dictionary for the current vf-id with the its maps-actions
                self.maps_config[vf_id]['maps-actions'] = maps_actions

    
    # def _get_ssp_report_value(self) -> Dict[str, Dict[str, Union[str, int]]]: # List[Dict[str, Union[str, int]]]:
    #     """
    #     Method extracts Switch Status Policy report values from the ssp_report container.
    #     The SSP report provides the overall health status of the switch.
        
    #     Returns:
    #         List of dictionaries.
    #         Dictionary keys are object name, its operational status and status id.
    #         Status id is a numerical status value to identify warning thresholds.
    #         ROMOVE: If ssp_report container was not retrived from the switch ssp_report contain error-message
    #         for each object name.
    #     """        
        
    #     # ssp_report_lst = []
    #     ssp_report_dct = {}
        
    #     if self.sw_telemetry.ssp_report.get('Response'):
    #         container = self.sw_telemetry.ssp_report['Response']['switch-status-policy-report']
            
    #         # ssp_report_dct = self.sw_telemetry.ssp_report['Response']['switch-status-policy-report'].copy()
    #         # missing_ssp_dct = {ssp_leaf: None for ssp_leaf in BrocadeMAPSParser.SSP_LEAFS if ssp_leaf not in ssp_report_dct}
    #         # ssp_report_dct.update(missing_ssp_dct)
    #         # ssp_report_dct['chassis-wwn'] = self.ch_wwn
    #         # ssp_report_dct['chassis-name'] = self.ch_name

    #         for ssp_leaf in BrocadeMAPSParser.SSP_LEAFS:
    #             if not ssp_leaf in container:
    #                 continue
    #             state = container[ssp_leaf]
    #             # ssp_report_lst.append({'chassis-wwn': self.ch_wwn,
    #             #                        'chassis-name': self.ch_name,
    #             #                        'name': ssp_leaf,
    #             #                        'operational-state': state.upper(),
    #             #                        'operational-state-id': BrocadeMAPSParser.SSP_STATE[state]})
    #             ssp_report_dct[ssp_leaf] = {'chassis-wwn': self.ch_wwn,
    #                                         'chassis-name': self.ch_name,
    #                                         'name': ssp_leaf,
    #                                         'operational-state': state.capitalize(),
    #                                         'operational-state-id': BrocadeMAPSParser.SSP_STATE[state]}
    #     # elif self.sw_telemetry.ssp_report.get('status-code'):
    #     #     for ssp_leaf in BrocadeMAPSParser.SSP_LEAFS:
    #     #         error = self.sw_telemetry.ssp_report['error-message']
    #     #         error = " (" + error + ")" if error else ''
    #     #         state = 'unknown'
    #     #         ssp_report_lst.append({'name': ssp_leaf,
    #     #                                'operationa-state': state.upper() + error,
    #     #                                'operational-state-id': BrocadeMAPSParser.SSP_STATE[state]})
    #     return ssp_report_dct
    


    def _get_ssp_report_value(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Method extracts Switch Status Policy report values from the ssp_report container.
        The SSP report provides the overall health status of the switch.
        
        Returns:
            dict: Dictionary keys are parameter name status and status id.
            Status id is a numerical status value.
        """        
        
        ssp_report_dct = {}
        
        if self.sw_telemetry.ssp_report.get('Response'):
            # container = self.sw_telemetry.ssp_report['Response']['switch-status-policy-report']
            
            ssp_report_dct = self.sw_telemetry.ssp_report['Response']['switch-status-policy-report'].copy()
            ssp_report_keys = list(ssp_report_dct.keys()).copy()
            for ssp_report_key in ssp_report_keys:
                state = ssp_report_dct[ssp_report_key]
                ssp_report_dct[ssp_report_key + BrocadeMAPSParser.STATUS_TAG] = ssp_report_dct.pop(ssp_report_key)
                ssp_report_dct[ssp_report_key + BrocadeMAPSParser.STATUS_ID_TAG] = BrocadeMAPSParser.SSP_STATE[state]
                if state:
                    ssp_report_dct[ssp_report_key + BrocadeMAPSParser.STATUS_TAG] = state.capitalize()
            # add chassis info
            ssp_report_dct['chassis-wwn'] = self.ch_wwn
            ssp_report_dct['chassis-name'] = self.ch_name
        return ssp_report_dct


    def _get_ssp_report_parameters(self) -> List[str]:
        """
        Method extracts Switch Status Policy report parameter names from the ssp_report container.
        The SSP report provides the overall health status of the switch.
        
        Returns:
            List[str]: Parameter names of the SSP report.
        """     

        if self.sw_telemetry.ssp_report.get('Response'):
            container = self.sw_telemetry.ssp_report['Response']['switch-status-policy-report']
            ssp_report_parameters = list(container.keys())
            
            return ssp_report_parameters

        

    def _get_system_resource_values(self) -> Dict[str, Union[int, str]]:
        """
        Method extracts system resources (such as CPU, RAM, and flash memory usage) values from the system_resources container.
        Note that usage is not real time and may be delayed up to 2 minutes.
        
        Returns:
            Dictionary with system resource name as keys and its usage as values.
        """        
        
        resources = ('cpu-usage', 'flash-usage', 'memory-usage', 'total-memory')

        if self.sw_telemetry.system_resources.get('Response'):
            system_resources_dct = self.sw_telemetry.system_resources['Response']['system-resources'].copy()
            missing_resources_dct = {resource: None for resource in resources if resource not in system_resources_dct}
            system_resources_dct.update(missing_resources_dct)
            system_resources_dct['chassis-wwn'] = self.ch_wwn
            system_resources_dct['chassis-name'] = self.ch_name
            for system_resource in BrocadeMAPSParser.SYSTEM_RESOURCE_THRESHOLDS:
                system_resource_status = system_resource + '-status'
                system_resource_status_id = system_resource_status + '-id'
                # 'unknown
                if system_resources_dct[system_resource] is None:
                    system_resources_dct[system_resource_status_id] = 2
                # ok status
                elif system_resources_dct[system_resource] < BrocadeMAPSParser.SYSTEM_RESOURCE_THRESHOLDS[system_resource]:
                    system_resources_dct[system_resource_status_id] = 1
                # critical status
                elif system_resources_dct[system_resource] >= BrocadeMAPSParser.SYSTEM_RESOURCE_THRESHOLDS[system_resource] + 10:
                    system_resources_dct[system_resource_status_id] = 4
                # warning status
                else:
                    system_resources_dct[system_resource_status_id] = 3
                system_resources_dct[system_resource_status] = BrocadeMAPSParser.STATUS_ID[system_resources_dct[system_resource_status_id]]

            return system_resources_dct
        else:
            return dict()
                
             
    def _get_dashboard_rule_value(self) -> Dict[int, List[Dict[str, Optional[Union[str, int]]]]]:
        """
        Function retrieves the MAPS events or rules triggered and the objects on which the rules were triggered 
        over a specified period of time for each logical switch.
        
        Severity level:
            0 - no event triggired or retrieved
            1 - information that event condition is cleared 
            2 - warning that event condition detected
            
        Virtual Fabric ID:
            -1: VF mode is disabled
            -2: VF mode is unknown (chassis container was not retrieved)
            -3: VF IDs are unknown (fc_logical_switch container was not retrieved)
            1-128: VF mode is enabled
        
        Returns:
            Dictionary of lists.
            External dictionary keys are logical switch vf-ids (if VF mode is disabled then vf-id is -1).
            Nested lists contain dictionaries. 
            Dictionary keys are category, rule name, time-stamp, triggered times, object, severity etc of the event.
        """

        dashboard_rule_dct = {}
        # parsing triggered events for for each logical switch
        for vf_id, dashboard_rule_telemetry in self.sw_telemetry.dashboard_rule.items():
            # get sw_name, sw_wwn, vf_id to add
            sw_details = self.sw_parser.get_switch_details(vf_id)
            
            if dashboard_rule_telemetry.get('Response'):
                # list of the triggered events for the current logical switch with vf_id
                dashboard_rule_dct[vf_id] = []
                
                # list of dictionaries. each dictionary is the triggered event
                container = dashboard_rule_telemetry['Response']['dashboard-rule']
                # cheking each event
                for db_rule in container:
                    db_rule_name = db_rule['name']
                    # check if rule name contains any event from the ignored list (means that event condition is cleared)
                    db_rule_ignore_flag = any([bool(re.search(f'.+?_{ignored_pattern}$', db_rule_name)) 
                                               for ignored_pattern in BrocadeMAPSParser.DB_RULE_IGNORE])
                    # event severity level (if event is in the ignored group then severity is 1 otherwise 2)
                    db_rule_severity = 1 if db_rule_ignore_flag else 2
                    # create dictionary containing triggered event details
                    current_db_rule_dct = {leaf: db_rule.get(leaf) for leaf in BrocadeMAPSParser.DB_RULE_LEAFS}
                    current_db_rule_dct['severity'] = db_rule_severity
                    # add sw_name, sw_wwn, vf-id
                    current_db_rule_dct.update(sw_details)
                    # triggered event might containt single or miltiple objects that violated the rule (ports for example)
                    for object_item in db_rule['objects']['object']:
                        # the object format is as follows: <element>:<value>
                        # for example, 'F-Port 10:90'
                        object_element, object_value = object_item.split(':')
                        current_db_rule_dct['object-element'] = object_element
                        current_db_rule_dct['object-value'] = object_value
                        # add event to the list for the each object
                        dashboard_rule_dct[vf_id].append(current_db_rule_dct)
            # if no events were triggered add error-message to the event dictionary with severity 0
            elif dashboard_rule_telemetry.get('status-code'):
                dashboard_rule_dct[vf_id] = []
                current_db_rule_dct = dict.fromkeys(BrocadeMAPSParser.DB_RULE_LEAFS)
                error_msg = dashboard_rule_telemetry['error-message']
                current_db_rule_dct['name'] = error_msg
                current_db_rule_dct['category'] = error_msg
                current_db_rule_dct['severity'] = 0
                current_db_rule_dct.update(sw_details)
                dashboard_rule_dct[vf_id].append(current_db_rule_dct)
        return dashboard_rule_dct


    def _get_changed_system_resources(self, other) -> Dict[str, Union[str, int]]:
        """
        Method detects if system resource usage and it's status have been changed.
        It compares parameters of two instances of BrocadeMAPSParser class.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeMAPSParser}: class instance retrieved from the previous sw_telemetry.
        
        Returns:
            dict: System resource change dictionary. Any chaged system resource usage are in this dictionary.
        """

        # system resource changed values
        system_resources_changed_dct = {}
                
        # other doesn't exist (for examle 1st iteration)
        # other is not same class
        # other's required atrribute is empty
        if other is None or str(type(self)) != str(type(other)) or not other.system_resources:
            return None
        
        # check if other is for the same switch
        elif self.same_chassis(other):

            # timestamps
            time_now = self.telemetry_date + ' ' + self.telemetry_time
            time_prev = other.telemetry_date + ' ' + other.telemetry_time
            # status keys
            system_resource_status_keys = [system_resource + '-status' for system_resource in BrocadeMAPSParser.SYSTEM_RESOURCE_THRESHOLDS]
            # changed system resources and statuses 
            system_resources_changed_dct = BrocadeMAPSParser.get_changed_chassis_params(self.system_resources, other.system_resources, 
                                                                                          changed_keys=list(BrocadeMAPSParser.SYSTEM_RESOURCE_THRESHOLDS.keys()) + system_resource_status_keys, 
                                                                                          const_keys=['chassis-name', 'chassis-wwn'], 
                                                                                          time_now=time_now, time_prev=time_prev)
        return system_resources_changed_dct


    # def _get_changed_ssp_report(self, other) -> Dict[str, Dict[str, Dict[str, Union[str, int]]]]:
    #     """
    #     Method detects if ssp report parameters (operational-state) have been changed for each ssp leaf.
    #     It compares ssp leafs parameters of two instances of BrocadeMAPSParser class.
    #     All changed parameters are added to to the dictionatry including current and previous values.
        
    #     Args:
    #         other {BrocadeMAPSParser}: class instance retrieved from the previous sw_telemetry.
        
    #     Returns:
    #         dict: ssp report change dictionary. Any ssp leaf with changed parameters are in this dictionary.
    #     """

    #     # switch ports with changed parameters
    #     ssp_report_changed_dct = {}

    #     # other is not exist (for examle 1st iteration)
    #     # other is not BrocadeFCPortParametersParser type
    #     # other's fcport_params atrribute is empty
    #     if other is None or str(type(self)) != str(type(other)) or not other.ssp_report:
    #         return None
        
    #     # check if other is for the same switch
    #     elif self.same_chassis(other):
    #         for ssp_leaf, ssp_leaf_now_dct in self.ssp_report.items():

    #             # if there is no ssp_leaf in other check next ssp_leaf 
    #             if ssp_leaf not in other.ssp_report:
    #                 continue

    #             # ssp leaf parameters from the previous telemetry    
    #             ssp_leaf_prev_dct = other.ssp_report[ssp_leaf]
    #             # timestamps
    #             time_now = self.telemetry_date + ' ' + self.telemetry_time
    #             time_prev = other.telemetry_date + ' ' + other.telemetry_time
    #             # change parameters
    #             ssp_leaf_changed = BrocadeMAPSParser.get_changed_chasssis_params(ssp_leaf_now_dct, ssp_leaf_prev_dct, 
    #                                                                                 changed_keys=['operational-state'], 
    #                                                                                 const_keys=['chassis-name', 'chassis-wwn', 'name'], 
    #                                                                                 time_now=time_now, time_prev=time_prev)
    #             if ssp_leaf_changed:
    #                 ssp_report_changed_dct[ssp_leaf] = ssp_leaf_changed
    #     return ssp_report_changed_dct



    def _get_changed_ssp_report(self, other) -> Dict[str, Dict[str, Dict[str, Union[str, int]]]]:
        """
        Method detects if ssp report parameters (operational-state) have been changed for each ssp leaf.
        It compares ssp leafs parameters of two instances of BrocadeMAPSParser class.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeMAPSParser}: class instance retrieved from the previous sw_telemetry.
        
        Returns:
            dict: ssp report change dictionary. Any ssp leaf with changed parameters are in this dictionary.
        """

        # switch ports with changed parameters
        ssp_report_changed_dct = {}

        # other is not exist (for examle 1st iteration)
        # other is not BrocadeFCPortParametersParser type
        # other's fcport_params atrribute is empty
        if other is None or str(type(self)) != str(type(other)) or not other.ssp_report:
            return None
        
        # check if other is for the same switch
        elif self.same_chassis(other):
            ssp_changed_status_keys = [key for key in self.ssp_report.keys() if key.endswith(BrocadeMAPSParser.STATUS_TAG)]

            # timestamps
            time_now = self.telemetry_date + ' ' + self.telemetry_time
            time_prev = other.telemetry_date + ' ' + other.telemetry_time
            # change parameters
            ssp_report_changed_dct = BrocadeMAPSParser.get_changed_chassis_params(self.ssp_report, other.ssp_report, 
                                                                                changed_keys=ssp_changed_status_keys, 
                                                                                const_keys=['chassis-name', 'chassis-wwn'], 
                                                                                time_now=time_now, time_prev=time_prev)
        return ssp_report_changed_dct



    @property
    def sw_parser(self):
        return self._sw_parser
    
    
    @property
    def maps_config(self):
        return self._maps_config
    

    @property
    def ssp_report(self):
        return self._ssp_report
    

    @property
    def ssp_report_parameters(self):
        return self._ssp_report_parameters
    

    @property
    def ssp_report_changed(self):
        return self._ssp_report_changed
    

    @property
    def system_resources(self):
        return self._system_resources
    

    @property
    def system_resources_changed(self):
        return self._system_resources_changed
    

    @property
    def dashboard_rule(self):
        return self._dashboard_rule