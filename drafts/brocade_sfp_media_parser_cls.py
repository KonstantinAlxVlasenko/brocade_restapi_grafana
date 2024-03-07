# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:17:39 2024

@author: kavlasenko
"""

import re
from typing import Dict, List, Tuple, Union, Optional

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser

class BrocadeSFPMediaParser:
    """
    Class to create fc port parameters dictionaries to imitate port status from switchshow output.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        sw_parser: switch parameters retrieved from the sw_telemetry.
        port_owner: dictonary with port name as key and switchname to which port belongs to as value.
        port_status: fc port parameters dictionary.
    """

    MEDIA_RDP_LEAFS = ['connector', 'current', 'identifier', 'media-distance', 
                       'media-speed-capability', 'name', 'part-number', 'power-on-time',
                       'rx-power', 'serial-number', 'temperature', 
                       'tx-power', 'vendor-name', 'vendor-oui', 'vendor-revision', 
                       'voltage', 'wavelength', 
                       'remote-identifier', 'remote-laser-type', 'remote-media-current', 
                       'remote-media-rx-power', 'remote-media-speed-capability', 
                       'remote-media-temperature', 'remote-media-tx-power', 
                       'remote-media-voltage', 'remote-optical-product-data'
                       ]
    
    FC_PORT_PARAMS = ['swicth-name', 'port-name', 'physical-state', 
                      'port-enable-status', 'link-speed', 'port-type']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fcport_params_parser: BrocadeSwitchParser):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._fcport_params_parser: BrocadeSwitchParser = fcport_params_parser
        self._sfp_media = self._get_sfp_media_values()

    
    def _get_sfp_media_values(self) -> Dict[str, Union[str, int]]:
        """_summary_

        Returns:
            Dict[str, Union[str, int]]: _description_
        """

        sfp_media_dct = {}

        for vf_id, sfp_media_telemetry in self.sw_telemetry.media_rdp.items():
            if sfp_media_telemetry.get('Response'):
                # list with fc_interface containers for the each port in the vf_id switch
                sfp_media_container_lst = sfp_media_telemetry['Response']['media-rdp']
                sfp_media_dct[vf_id] = {}
                
                for sfp_media_container in sfp_media_container_lst:
                    # slot_port_number in the format 'slot_number/port_number' (e.g. '0/1')
                    slot_port_number = sfp_media_container['name']
                    # split slot and port number
                    protocol, slot_number, port_number = slot_port_number.split('/')
                    slot_port_number = slot_number + '/' + port_number
                    # print(protocol, slot_number, port_number, slot_port_number)
                    sfp_media_current_dct = {leaf: sfp_media_container.get(leaf) for leaf in BrocadeSFPMediaParser.MEDIA_RDP_LEAFS}
                    sfp_media_current_dct['slot-number'] = int(slot_number)
                    sfp_media_current_dct['port-number'] = int(port_number)
                    # sfp_media_current_dct['media-speed-capability'] = BrocadeSFPMediaParser._get_speed_capabilities(sfp_media_current_dct['media-speed-capability'])
                    # sfp_media_current_dct['remote-media-speed-capability'] = BrocadeSFPMediaParser._get_speed_capabilities(sfp_media_current_dct['remote-media-speed-capability'])

                    sfp_media_current_dct['media-distance'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['media-distance'], 'distance')
                    sfp_media_current_dct['media-speed-capability'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['media-speed-capability'], 'speed')
                    sfp_media_current_dct['remote-media-speed-capability'] = BrocadeSFPMediaParser._convert_list_to_string(sfp_media_current_dct['remote-media-speed-capability'], 'speed')


                    remote_optical_product_keys = ['part-number', 'serial-number', 'vendor-name']
                    if sfp_media_container.get('remote-optical-product-data'):
                        for key in remote_optical_product_keys:
                            sfp_media_current_dct['remote-' + key] = sfp_media_container['remote-optical-product-data'].get(key)
                    else:
                        for key in remote_optical_product_keys:
                            sfp_media_current_dct['remote-' + key] = None

                    if sfp_media_current_dct['power-on-time']:
                        sfp_media_current_dct['power-on-time-hrf'] = BrocadeSFPMediaParser.hours_to_hrf(sfp_media_current_dct['power-on-time'])

                    
                    fc_port_params_current = self.fcport_params_parser.fcport_params[vf_id][slot_port_number]
                    sfp_media_current_dct.update({param: fc_port_params_current.get(param) for param in BrocadeSFPMediaParser.FC_PORT_PARAMS})
                    # add current port status dictionary to the summary port status dictionary with vf_id and slot_port as consecutive keys
                    sfp_media_dct[vf_id][sfp_media_container['name']] = sfp_media_current_dct
        return sfp_media_dct
    

    @staticmethod
    def _get_speed_capabilities(speed_dct) -> str:
        if speed_dct and speed_dct.get('speed'):
            print(speed_dct['speed'])
            speed_capabilities_str = [str(value) for value in speed_dct['speed']]
            return ', '.join(speed_capabilities_str)
                                

    @staticmethod
    def _convert_list_to_string(value_dct, key) -> str:
        if value_dct and value_dct.get(key):
            if isinstance(value_dct[key], list):
                str_list = [str(value) for value in value_dct[key]]
                return ', '.join(str_list)
            else:
                return value_dct[key]


    @staticmethod
    def hours_to_hrf(hours_input: int) -> str:
        """
        Method converts hours to the string human readable format.
        
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


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser
    

    @property
    def sfp_media(self):
        return self._sfp_media