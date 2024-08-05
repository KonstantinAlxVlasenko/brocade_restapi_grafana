# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:17:39 2024

@author: kavlasenko
"""

import math
from typing import Dict, List, Optional, Tuple, Union

from brocade_base_parser import BrocadeTelemetryParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser


class BrocadeSFPMediaParser(BrocadeTelemetryParser):
    """
    Class to create sfp media parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        fcport_params_parser: fc ports parameters retrieved from the sw_telemetry.
        sfp_media: sfp media parameters dictionary ({vf_id:{slot_port_id:{param1: value1, param2: valuue2}}}).
    """

    MEDIA_RDP_LEAFS = ['connector', 'current', 'identifier', 'media-distance', 
                       'media-speed-capability', 'name', 'part-number', 'power-on-time',
                       'rx-power', 'serial-number', 'temperature', 
                       'tx-power', 'vendor-name', 'vendor-oui', 'vendor-revision', 
                       'voltage', 'wavelength', 
                       'remote-identifier', 'remote-laser-type', 'remote-media-current', 
                       'remote-media-rx-power', 'remote-media-speed-capability', 
                       'remote-media-temperature', 'remote-media-tx-power', 
                       'remote-media-voltage']
    
    # FC_PORT_PARAMS = ['switch-name', 'switch-wwn', 'fabric-user-friendly-name', 'vf-id', 'port-name', 'physical-state', 'physical-state-id',
    #                   'port-enable-status', 'port-enable-status-id', 
    #                   'port-speed-hrf', 'auto-negotiate', 'port-speed-gbps', 
    #                   'port-type', 'port-type-id']

    REMOTE_OPTICAL_PRODUCT_LEAFS = ['part-number', 'serial-number', 'vendor-name']


    MEDIA_RDP_CHANGED = ['vendor-name', 'part-number', 'serial-number', 
                         'wavelength', 'media-distance', 'media-speed-capability',
                         'remote-vendor-name', 'remote-part-number', 'remote-serial-number',
                         'remote-media-speed-capability']
    
    MEDIA_POWER_CHANGED = ['rx-power', 'tx-power', 'remote-media-rx-power', 'remote-media-tx-power',
                           'rx-power-dbm', 'tx-power-dbm', 'remote-media-rx-power-dbm', 'remote-media-tx-power-dbm']
    
    MEDIA_POWER_STATUS_CHANGED = ['rx-power-status', 'tx-power-status', 'remote-media-rx-power-status', 'remote-media-tx-power-status']
    

    # SFP_LW_TX_POWER_ALERT = {'high-alarm': 2500, 'low-alarm': 1000, 'high-warning': 2300, 'low-warning': 1200}

    # SFP_LW_RX_POWER_ALERT = {'high-alarm': 630, 'low-alarm': 50, 'high-warning': 580, 'low-warning': 100}

    # SFP_SW_TX_POWER_ALERT = {'high-alarm': 1500, 'low-alarm': 150, 'high-warning': 1400, 'low-warning': 200}

    # SFP_SW_RX_POWER_ALERT = {'high-alarm': 1500, 'low-alarm': 150, 'high-warning': 1400, 'low-warning': 200}

    # SFP_TEMPERATURE_ALERT = {'high-alarm': 75, 'low-alarm': -5, 'high-warning': 70, 'low-warning': 0}

        
    SFP_POWER_ALERT = {'lw_tx': {'high-alarm': 2500, 'low-alarm': 1000, 'high-warning': 2300, 'low-warning': 1200},
                       'lw_rx': {'high-alarm': 630, 'low-alarm': 50, 'high-warning': 580, 'low-warning': 100},
                       'sw_tx': {'high-alarm': 1500, 'low-alarm': 150, 'high-warning': 1400, 'low-warning': 200},
                       'sw_rx': {'high-alarm': 1500, 'low-alarm': 150, 'high-warning': 1400, 'low-warning': 200}}

    SFP_TEMPERATURE_ALERT = {'high-alarm': 75, 'low-alarm': -5, 'high-warning': 70, 'low-warning': 0}
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fcport_params_parser: BrocadeSwitchParser, sfp_media_parser=None):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        super().__init__(sw_telemetry)
        # self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._fcport_params_parser: BrocadeSwitchParser = fcport_params_parser
        self._sfp_media = self._get_sfp_media_values()
        if self.sfp_media:
            self._sfp_media_changed = self._get_changed_sfpmedia(sfp_media_parser)
        else:
            self._sfp_media_changed = {}

    
    def _get_sfp_media_values(self) -> Dict[str, Union[str, int]]:
        """
        Method retrieves each port sfp parameters.
        
        Returns:
            dict: SFP media parameters. Dictionary of dictionaries of dictionaries.
                External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
                First level nested dictionary keys are slot_port_numbers.
                Second level nested dictionary keys are sfp media parameters names.
        """

        sfp_media_dct = {}

        for vf_id, sfp_media_telemetry in self.sw_telemetry.media_rdp.items():
            if sfp_media_telemetry.get('Response'):
                # list with sfp_media containers for the each port in the vf_id switch
                sfp_media_container_lst = sfp_media_telemetry['Response']['media-rdp']
                sfp_media_dct[vf_id] = {}
                
                for sfp_media_container in sfp_media_container_lst:
                    # get sfp media parameters from the container
                    sfp_media_current_dct = {leaf: sfp_media_container.get(leaf) for leaf in BrocadeSFPMediaParser.MEDIA_RDP_LEAFS}
                    # convert uW values to the dBm
                    self._add_sfp_dbm_power(sfp_media_current_dct)
                    # slot_port_number in the format 'protocol/slot_number/port_number' (e.g. 'fc/0/1')
                    slot_port_number = sfp_media_container['name']
                    # split protocol slot and port number
                    protocol, slot_number, port_number = slot_port_number.split('/')
                    slot_port_number = slot_number + '/' + port_number
                    sfp_media_current_dct['slot-number'] = int(slot_number)
                    sfp_media_current_dct['port-number'] = int(port_number)
                    sfp_media_current_dct['port-protocol'] = protocol
                    # convert parameters presented as list to a single string
                    sfp_media_current_dct['media-distance'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['media-distance'], 'distance')
                    sfp_media_current_dct['media-speed-capability'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['media-speed-capability'], 'speed')
                    sfp_media_current_dct['remote-media-speed-capability'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['remote-media-speed-capability'], 'speed')
                    # add remote sfp parameters presented as nested dictionary to the outer sfp dictionary
                    remote_optical_product_dct = BrocadeSFPMediaParser._get_remote_optical_product_data(sfp_media_container)
                    sfp_media_current_dct.update(remote_optical_product_dct)
                    # present sfp module power-on-time in human readable format
                    BrocadeSFPMediaParser._set_poweron_time_hrf(sfp_media_current_dct)
                    # add port parameters to the sfp media dictionary
                    fcport_params_dct = self._get_port_params(vf_id, protocol, slot_port_number)
                    sfp_media_current_dct.update(fcport_params_dct)
                    # add power status ('ok', ''warning', 'critical) for the power parameters
                    self._add_power_status(sfp_media_current_dct)
                    # add current sfp media dictionary to the summary sfp media dictionary with vf_id and slot_port as consecutive keys
                    sfp_media_dct[vf_id][sfp_media_container['name']] = sfp_media_current_dct
        return sfp_media_dct


    def _get_port_params(self, vf_id: int, protocol: str, slot_port_number: str) -> Dict[str, Optional[str]]:
        """
        Method to get port parameters.
        
        Args:
            vf_id {int}: switch vf_id.
            protocol {str}: port protocol type.
            slot_port_number {str}: slot and port number in the format'slot/port' (e.g. '0/1').
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with FC_PORT_PARAMS values.
        """

        if protocol.lower() == 'fc':
            fc_port_params_current = self.fcport_params_parser.fcport_params[vf_id][slot_port_number]
            fcport_params = {param: fc_port_params_current.get(param) for param in BrocadeSFPMediaParser.FC_PORT_ADD_PARAMS}
        else:
            fcport_params = {param: None for param in BrocadeSFPMediaParser.FC_PORT_PARAMS}
        return fcport_params


    @staticmethod
    def _get_remote_optical_product_data(sfp_media_container: dict) -> Dict[str, Optional[str]]:
        """Method to get remote sfp product data.

        Args:
            sfp_media_container (dict): rest_api container of the single sfp media.
        
        Returns:
            Dict[str, Optional[str]]: dictionary with remote sfp product data.
        """
        
        if sfp_media_container.get('remote-optical-product-data'):
            remote_optical_product_dct = {'remote-' + key: sfp_media_container['remote-optical-product-data'].get(key) 
                                          for key in BrocadeSFPMediaParser.REMOTE_OPTICAL_PRODUCT_LEAFS}
        else:
            remote_optical_product_dct = {'remote-' + key: None 
                                          for key in BrocadeSFPMediaParser.REMOTE_OPTICAL_PRODUCT_LEAFS}
        return remote_optical_product_dct


    @staticmethod
    def _set_poweron_time_hrf(sfp_media_current_dct: dict) -> None:
        """Method to present sfp module power-on-time in human readable format and add it sfp parameters dictionary.

        Args:
            sfp_media_current_dct (dict): dictionary with sfp parameters for the single port.
        
        Returns:
            None
        """

        if sfp_media_current_dct['power-on-time']:
            sfp_media_current_dct['power-on-time-hrf'] = BrocadeSFPMediaParser.hours_to_hrf(sfp_media_current_dct['power-on-time'])
        else:
            sfp_media_current_dct['power-on-time-hrf'] = sfp_media_current_dct.get('power-on-time')

                               
    @staticmethod
    def _convert_list_to_string(value_dct: dict, key: str) -> Optional[str]:
        """
        Method converts dictionary value which is list type to a single string.
        Input: value_dct = {key: [1, 2, 3]} or {key: ['1', '2', '3']}
        Output: value_dct = '1, 2, 3'
        
        Args:
            value_dct {dict}: dictionary with a single key.
            key {str}: dictionary key title which contains list of integers or list of strings
        
        Returns:
            str: joined list of values.
        """

        if value_dct and value_dct.get(key):
            if isinstance(value_dct[key], list):
                # convert list elements to the string type
                str_list = [str(value) for value in value_dct[key]]
                return ', '.join(str_list)
            else:
                return value_dct[key]


    @staticmethod
    def hours_to_hrf(hours_input: int) -> str:
        """
        Method converts hours to the human readable format (string).
        
        Args:
            hours_input {int}: hours number to convert
        
        Returns:
            String in format 'x yrs y days z hours'
        """
        
        hours_in_year = 8760
        hours_in_day = 24

        years = hours_input // hours_in_year
        days = (hours_input - (years * hours_in_year)) // hours_in_day
        hours = hours_input - years * hours_in_year - days * hours_in_day

        hrf_str = f"{days} day{'' if hours == 1 else 's'} " +\
                    f"{hours} hr{'' if hours == 1 else 's'}"        
        if years:
            hrf_str = f"{years} yr{'' if years == 1 else's'} " + hrf_str         
        return hrf_str


    def _add_power_status(self, sfp_media_dct) -> None:
        """
        Method adds power status id and power status ('ok', 'unknown', 'warning', 'critical') to the sfp media dictionary for the 
        'rx-power', 'tx-power', 'remote-media-rx-power', 'remote-media-tx-power'
        depending on power value for Online ports.
                
        Args: 
            sfp_media_dct (dict): sfp parameters dictionary for a single port
        
        Returns:
            None
        """
        
        # check longwave or shortwave transceiver installed
        sfp_distance = None
        if sfp_media_dct.get('media-distance'):
            if 'short' in sfp_media_dct['media-distance']:
                sfp_distance = 'sw'
            elif 'long' in sfp_media_dct['media-distance']:
                sfp_distance = 'lw'

        # check power value for Online ports only
        if sfp_media_dct.get('physical-state') == 'Online':
            if sfp_media_dct.get('rx-power') is not None:
                rx_power_status_id = 2
                if sfp_distance == 'sw':
                    rx_power_status_id = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_rx'])

                elif sfp_distance == 'lw':
                    rx_power_status_id = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['lw_rx'])
                
                sfp_media_dct['rx-power-status-id'] = rx_power_status_id
                sfp_media_dct['rx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(rx_power_status_id)
            else:
                sfp_media_dct['rx-power-status-id'] = None
                sfp_media_dct['rx-power-status'] = None
                                                                             
            if sfp_media_dct.get('tx-power') is not None:
                tx_power_status_id = 2
                if sfp_distance == 'sw':
                    tx_power_status_id = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_tx'])
                elif sfp_distance == 'lw':
                    sfp_media_dct['tx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['lw_tx'])
                sfp_media_dct['tx-power-status-id'] = tx_power_status_id
                sfp_media_dct['tx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(tx_power_status_id)
            else:
                sfp_media_dct['tx-power-status-id'] = None
                sfp_media_dct['tx-power-status'] = None

            if sfp_media_dct.get('remote-media-rx-power') is not None:
                remote_rx_power_status_id = 2
                remote_rx_power_status_id = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['remote-media-rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_rx'])
                sfp_media_dct['remote-media-rx-power-status-id'] = remote_rx_power_status_id
                sfp_media_dct['remote-media-rx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(remote_rx_power_status_id)
            else:
                sfp_media_dct['remote-media-rx-power-status-id'] = None
                sfp_media_dct['remote-media-rx-power-status'] = None

            if sfp_media_dct.get('remote-media-tx-power'):
                remote_tx_power_status_id = 2
                remote_tx_power_status_id = BrocadeSFPMediaParser.get_alert_status_id(
                        sfp_media_dct['remote-media-tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_tx'])
                sfp_media_dct['remote-media-tx-power-status-id'] = remote_tx_power_status_id
                sfp_media_dct['remote-media-tx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(remote_tx_power_status_id)
            else:
                sfp_media_dct['remote-media-tx-power-status-id'] = None
                sfp_media_dct['remote-media-tx-power-status'] = None

        # power status and power status id for ports which are not Online
        else:
            empty_stutus_dct = {key: None for key in BrocadeSFPMediaParser.MEDIA_POWER_STATUS_CHANGED}
            empty_stutus_id_dct = {key + '-id': None for key in BrocadeSFPMediaParser.MEDIA_POWER_STATUS_CHANGED}
            sfp_media_dct.update(empty_stutus_dct)
            sfp_media_dct.update(empty_stutus_id_dct)
                

    # def _add_power_status(self, sfp_media_dct) -> None:
    #     """
    #     Method adds power status ('ok', 'warning', 'critical') to the sfp media dictionary for the 
    #     'rx-power', 'tx-power', 'remote-media-rx-power', 'remote-media-tx-power'
    #     depending on power value for Online ports.
                
    #     Args: 
    #         sfp_media_dct (dict): sfp parameters dictionary for a single port
        
    #     Returns:
    #         None
    #     """
        
    #     # check longwave or shortwave transceiver installed
    #     sfp_distance = None
    #     if sfp_media_dct.get('media-distance'):
    #         if 'short' in sfp_media_dct['media-distance']:
    #             sfp_distance = 'sw'
    #         elif 'long' in sfp_media_dct['media-distance']:
    #             sfp_distance = 'lw'

    #     # check power value for Online ports only
    #     if sfp_media_dct.get('physical-state') == 'Online':
    #         if sfp_media_dct.get('rx-power'):
    #             if sfp_distance == 'sw':
    #                 sfp_media_dct['rx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_rx'])
    #                 sfp_media_dct['rx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(sfp_media_dct['rx-power-status-id'])
    #             elif sfp_distance == 'lw':
    #                 sfp_media_dct['rx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['lw_rx'])
    #                 sfp_media_dct['rx-power-status'] = BrocadeSFPMediaParser.STATUS_ID.get(sfp_media_dct['rx-power-status-id'])                                                             
    #         if sfp_media_dct.get('tx-power'):
    #             if sfp_distance == 'sw':
    #                 sfp_media_dct['tx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_tx'])
    #             elif sfp_distance == 'lw':
    #                 sfp_media_dct['tx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['lw_tx'])
    #         if sfp_media_dct.get('remote-media-rx-power'):
    #             sfp_media_dct['remote-rx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['remote-media-rx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_rx'])
    #         if sfp_media_dct.get('remote-media-tx-power'):
    #             sfp_media_dct['remote-tx-power-status-id'] = BrocadeSFPMediaParser.get_alert_status_id(
    #                     sfp_media_dct['remote-media-tx-power'], BrocadeSFPMediaParser.SFP_POWER_ALERT['sw_tx'])


    # @staticmethod
    # def get_alert_status(value: float, status_intervals_dct: dict) -> str:
    #     """
    #     Method checks to which interval value belongs to and returns corresponding status.
    #     '--------low-alarm--------low-warning--------high-warning--------high-alarm--------'
    #     'critical----------warning---------------ok---------------warning----------critical'
        
    #     Args:
    #         value {float}: value checked to which interval it belongs to.
    #         status_intervals_dct {dict}: dictionary with intervals 
    #         {'high-alarm': x, 'low-alarm': y, 'high-warning': z, 'low-warning': w}
        
    #     Returns:
    #         str: 'ok', 'warning', 'critical'
    #     """

    #     status = 'unknown'
    #     if value >= status_intervals_dct['low-warning'] and value < status_intervals_dct['high-warning']:
    #         status = 'ok'
    #     elif value >= status_intervals_dct['high-alarm'] or value < status_intervals_dct['low-alarm']:
    #         status = 'critical'
    #     else:
    #         status = 'warning'
    #     return status




    @staticmethod
    def get_alert_status_id(value: float, status_intervals_dct: dict) -> int:
        """
        Method checks to which interval value belongs to and returns corresponding status.
        '--------low-alarm--------low-warning--------high-warning--------high-alarm--------'
        'critical----------warning---------------ok---------------warning----------critical'
        STATUS_ID = {1: 'OK', 2: 'Unknown', 2: 'Warning', 2: 'Critical'}
        
        Args:
            value {float}: value checked to which interval it belongs to.
            status_intervals_dct {dict}: dictionary with intervals 
            {'high-alarm': x, 'low-alarm': y, 'high-warning': z, 'low-warning': w}
        
        Returns:
            int: (1,2,3,4)
        """
        
        status_id = 2 # unknown
        if value >= status_intervals_dct['low-warning'] and value < status_intervals_dct['high-warning']:
            status_id = 1 # ok
        elif value >= status_intervals_dct['high-alarm'] or value < status_intervals_dct['low-alarm']:
            status_id = 4 # critical
        else:
            status_id = 3 # warning
        return status_id



    def _add_sfp_dbm_power(self, sfp_media_dct):
        """Method converts uW power parameters to dBm and adds it to the sfp parameters dictionary.
        Power paramters 'rx-power', 'tx-power',  'remote-media-rx-power', 'remote-media-tx-power'.
                
        Args:
            sfp_media_dct (dict): single sfp parameters dictionary
        """
        
        sfp_dbm_power_dct = {}

        for sfp_param in sfp_media_dct:
            if 'x-power' in sfp_param: 
                if sfp_media_dct[sfp_param] is not None:
                    sfp_dbm_power_dct[sfp_param + '-dbm'] = BrocadeSFPMediaParser.uW_to_dBm(sfp_media_dct[sfp_param])
                else:
                    sfp_dbm_power_dct[sfp_param + '-dbm'] = None

        if sfp_dbm_power_dct:
            sfp_media_dct.update(sfp_dbm_power_dct)


    @staticmethod
    def uW_to_dBm(uW: float) -> float:
        """
        Method converts uwatt value to the dBm value.
        
        Args:
            uwatt {int}: uwatt value to convert
        
        Returns:
            dBm value
        """
                
        mW = uW/1000
        return round(10 * math.log10(mW / 1), 1)


    def _get_changed_sfpmedia(self, other) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method detects if sfp paramters from the MEDIA_RDP_CHANGED and MEDIA_POWER_CHANGED lists have been changed for each switch port.
        It compares sfp parameters of two instances of BrocadeSFPMediaParser class.
        All changed sfp parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeSFPMediaParser}: sfp media parameters class instance retrieved from the previous sw_telemetry.
        
        Returns:
            dict: SFP ports changed parameters dictionary. Any port with changed parameters are in this dictionary.
        """

        # switch ports with changed parameters
        sfp_media_changed_dct = {}

        # other is not exist (for examle 1st iteration)
        # other is not BrocadeSFPMediaParser type
        # other's sfp_media atrribute is empty
        if other is None or str(type(self)) != str(type(other)) or not other.sfp_media:
            return None
        
        # check if other is for the same switch
        elif self.same_chassis(other):
            for vf_id, sfp_media_vfid_now_dct in self.sfp_media.items():

                sfp_media_changed_dct[vf_id] = {}

                # if there is no vf_id in other check next vf_id 
                if vf_id not in other.sfp_media:
                    continue

                # sfp_media of the vf_id switch for the previous telemetry    
                sfp_media_vfid_prev_dct = other.sfp_media[vf_id]
                # timestamps
                time_now = self.telemetry_date + ' ' + self.telemetry_time
                time_prev = other.telemetry_date + ' ' + other.telemetry_time
                # add changed sfp_media ports for the current vf_id
                sfp_media_changed_dct[vf_id] = BrocadeSFPMediaParser.get_changed_vfid_ports(
                    sfp_media_vfid_now_dct, sfp_media_vfid_prev_dct, 
                    changed_keys=BrocadeSFPMediaParser.MEDIA_RDP_CHANGED + BrocadeSFPMediaParser.MEDIA_POWER_CHANGED + BrocadeSFPMediaParser.MEDIA_POWER_STATUS_CHANGED, 
                    const_keys=BrocadeSFPMediaParser.FC_PORT_PATH, 
                    time_now=time_now, time_prev=time_prev)
        return sfp_media_changed_dct


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser
    

    @property
    def sfp_media(self):
        return self._sfp_media
    
    @property
    def sfp_media_changed(self):
        return self._sfp_media_changed