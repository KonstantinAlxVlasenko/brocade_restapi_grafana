# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 17:45:30 2024

@author: kavlasenko
"""
from typing import Dict, List, Tuple, Union

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeFRUParser:
    """
    Class to create sensor (ps and fan) readings lists.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        fru_ps: power supply readings list.
        fru_fan: fan readings list.
        fru_sensor: temperature readings list.
    """
    
    
    PS_STATE = {'absent': 0,
                'ok': 1,
                'predicting failure': 2, 
                'unknown': 3,
                'try reseating unit': 4,
                'faulty': 5}
    
    
    FAN_STATE = {'absent': 0, 
                 'ok': 1, 
                 'below minimum': 2, 
                 'above maximum': 3, 
                 'unknown': 4, 
                 'not ok': 5,
                 'faulty': 6}
    
    
    SENSOR_STATE = {'absent': 0, 
                    'ok': 1}
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._fru_ps: list = self._get_ps_value()
        self._fru_fan: list = self._get_fan_value()
        self._fru_sensor: list = self._get_sensor_value()
        
        
    def _get_ps_value(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method extracts leaf values from the FRU Power Supply container.
        
        Returns:
            List of power supplies as nested dictionaries.
            Nested dictionary contains ps id, ps operational state, ps state id.
            PS state id is a numerical status value to identify warning thresholds.
        """
        
        ps_lst = []

        if self.sw_telemetry.fru_ps.get('Response'):
            container = self.sw_telemetry.fru_ps['Response']['power-supply']
            for ps in container:
                ps_id = 'Power Supply #' + str(ps['unit-number'])
                ps_state = ps['operational-state']
                ps_lst.append({'unit-number': ps_id, 
                               'operational-state': ps_state.upper(), 
                               'operational-state-id': BrocadeFRUParser.PS_STATE.get(ps_state)})
        return ps_lst
        

    def _get_fan_value(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method extracts leaf values from the FRU FAN container.
        
        Returns:
            List of fans as nested dictionaries.
            Nested dictionary contains fan id, fan airflow, fan operational state, fan state id, fan speed.
            FAN state id is a numerical status value to identify warning thresholds.
        """
        
        fan_lst = []
        if self.sw_telemetry.fru_fan.get('Response'):
            container = self.sw_telemetry.fru_fan['Response']['fan']
            for fan in container:
                fan_id = 'Fan #' + str(fan['unit-number'])
                fan_airflow = fan['airflow-direction']
                fan_state = fan['operational-state']
                fan_speed = fan['speed']
                fan_lst.append({'unit-number': fan_id, 
                                'airflow-direction': fan_airflow, 
                                'operational-state': fan_state.upper(), 
                                'operational-state-id': BrocadeFRUParser.FAN_STATE.get(fan_state), 
                                'speed': fan_speed})
        return fan_lst
    
    
    def _get_sensor_value(self) -> List[Dict[str, Union[str, int]]]:
    
        """
        Method extracts leaf values from the FRU SENSOR container.
        
        Returns:
            List of temperature sensors as nested dictionaries.
            Nested dictionary contains sensor id, sensor temperature, sensor operational state, sensor state id.
            SENSOR state id is a numerical status value to identify warning thresholds.
        """
        
        sensor_lst = []
        if self.sw_telemetry.fru_sensor.get('Response'):
            container = self.sw_telemetry.fru_sensor['Response']['sensor']
            for sensor in container:
                sensor_id = sensor['category'].capitalize() + ' #' + str(sensor['id'])
                sensor_state = sensor['state']
                sensor_lst.append({'unit-number': sensor_id,
                                   'temperature': sensor['temperature'],
                                    'operational-state': sensor_state.upper(), 
                                    'operational-state-id': BrocadeFRUParser.SENSOR_STATE.get(sensor_state, 3), 
                                    'slot-number': sensor.get('slot-number'), 
                                    'index': sensor.get('index')})
        return sensor_lst    
    


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry    


    @property
    def fru_ps(self):
        return self._fru_ps


    @property
    def fru_fan(self):
        return self._fru_fan
    
    @property
    def fru_sensor(self):
        return self._fru_sensor