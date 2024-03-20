# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:17:39 2024

@author: kavlasenko
"""


from typing import Dict, List, Optional, Tuple, Union

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser


class BrocadeSFPMediaParser:
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
    
    FC_PORT_PARAMS = ['swicth-name', 'port-name', 'physical-state', 
                      'port-enable-status', 'link-speed', 'port-type']

    REMOTE_OPTICAL_PRODUCT_LEAFS = ['part-number', 'serial-number', 'vendor-name']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fcport_params_parser: BrocadeSwitchParser):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._fcport_params_parser: BrocadeSwitchParser = fcport_params_parser
        self._sfp_media = self._get_sfp_media_values()

    
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
            fcport_params = {param: fc_port_params_current.get(param) for param in BrocadeSFPMediaParser.FC_PORT_PARAMS}
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


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser
    

    @property
    def sfp_media(self):
        return self._sfp_media