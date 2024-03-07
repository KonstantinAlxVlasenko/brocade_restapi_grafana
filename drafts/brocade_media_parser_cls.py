# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:17:39 2024

@author: kavlasenko
"""

import re
from typing import Dict, List, Tuple, Union, Optional

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser

class BrocadeMedaiParser:
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
    

    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, sw_parser: BrocadeSwitchParser):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._sw_parser: BrocadeSwitchParser = sw_parser
        self._port_owner = self._get_ports_owner()
        self._port_status = self. _get_portstatus_value()
