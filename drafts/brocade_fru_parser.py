# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 17:45:30 2024

@author: kavlasenko
"""
from typing import Dict, List, Tuple, Union, Optional

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_parser import BrocadeTelemetryParser


class BrocadeFRUParser(BrocadeTelemetryParser):
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
    
    PS_CHANGED = ['operational-state']
    FAN_CHANGED = ['operational-state','speed']
    SENSOR_CHANGED = ['operational-state', 'temperature']
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fru_prev=None):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        super().__init__(sw_telemetry)
        self._fru_ps: dict = self._get_ps_value()
        self._fru_fan: dict = self._get_fan_value()
        self._fru_sensor: dict = self._get_sensor_value()
        self._fru_ps_changed: dict = self._get_changed_fru_params(fru_prev, fru_type='ps')
        self._fru_fan_changed: dict = self._get_changed_fru_params(fru_prev, fru_type='fan')
        self._fru_sensor_changed: dict = self._get_changed_fru_params(fru_prev, fru_type='sensor')

        
        
    def _get_ps_value(self) -> Dict[int, Dict[str, Union[str, int]]]:
        """
        Method extracts leaf values from the FRU Power Supply container.
        
        Returns:
            List of power supplies as nested dictionaries.
            Nested dictionary contains ps id, ps operational state, ps state id.
            PS state id is a numerical status value to identify warning thresholds.
        """
        
        # ps_lst = []

        ps_dct = {}

        if self.sw_telemetry.fru_ps.get('Response'):
            container = self.sw_telemetry.fru_ps['Response']['power-supply']
            for ps in container:
                ps_id = 'Power Supply #' + str(ps['unit-number'])
                ps_state = ps['operational-state']
                # ps_lst.append({'chassis-name': self.ch_name,
                #                'chassis-wwn': self.ch_wwn,
                #                'unit-number': ps_id, 
                #                'operational-state': ps_state.upper(), 
                #                'operational-state-id': BrocadeFRUParser.PS_STATE.get(ps_state)})
                ps_dct[ps['unit-number']] = {'chassis-name': self.ch_name,
                                            'chassis-wwn': self.ch_wwn,
                                            'unit-number': ps_id, 
                                            'operational-state': ps_state.upper(), 
                                            'operational-state-id': BrocadeFRUParser.PS_STATE.get(ps_state)}
            return ps_dct
        

    def _get_fan_value(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method extracts leaf values from the FRU FAN container.
        
        Returns:
            List of fans as nested dictionaries.
            Nested dictionary contains fan id, fan airflow, fan operational state, fan state id, fan speed.
            FAN state id is a numerical status value to identify warning thresholds.
        """
        
        # fan_lst = []
        fan_dct = {}
        if self.sw_telemetry.fru_fan.get('Response'):
            container = self.sw_telemetry.fru_fan['Response']['fan']
            for fan in container:
                fan_id = 'Fan #' + str(fan['unit-number'])
                fan_airflow = fan['airflow-direction']
                fan_state = fan['operational-state']
                fan_speed = fan['speed']
                # fan_lst.append({'chassis-name': self.ch_name,
                #                 'chassis-wwn': self.ch_wwn,
                #                 'unit-number': fan_id, 
                #                 'airflow-direction': fan_airflow, 
                #                 'operational-state': fan_state.upper(), 
                #                 'operational-state-id': BrocadeFRUParser.FAN_STATE.get(fan_state), 
                #                 'speed': fan_speed})
                fan_dct[fan['unit-number']] = {'chassis-name': self.ch_name,
                                                'chassis-wwn': self.ch_wwn,
                                                'unit-number': fan_id, 
                                                'airflow-direction': fan_airflow, 
                                                'operational-state': fan_state.upper(), 
                                                'operational-state-id': BrocadeFRUParser.FAN_STATE.get(fan_state), 
                                                'speed': fan_speed}
        return fan_dct
    
    
    def _get_sensor_value(self) -> List[Dict[str, Union[str, int]]]:
    
        """
        Method extracts leaf values from the FRU SENSOR container.
        
        Returns:
            List of temperature sensors as nested dictionaries.
            Nested dictionary contains sensor id, sensor temperature, sensor operational state, sensor state id.
            SENSOR state id is a numerical status value to identify warning thresholds.
        """
        
        # sensor_lst = []
        sensor_dct = {}
        if self.sw_telemetry.fru_sensor.get('Response'):
            container = self.sw_telemetry.fru_sensor['Response']['sensor']
            for sensor in container:
                sensor_id = sensor['category'].capitalize() + ' #' + str(sensor['id'])
                sensor_state = sensor['state']
                # sensor_lst.append({'chassis-name': self.ch_name,
                #                    'chassis-wwn': self.ch_wwn,
                #                    'unit-number': sensor_id,
                #                    'temperature': sensor['temperature'],
                #                    'operational-state': sensor_state.upper(), 
                #                    'operational-state-id': BrocadeFRUParser.SENSOR_STATE.get(sensor_state, 3), 
                #                    'slot-number': sensor.get('slot-number'), 
                #                    'index': sensor.get('index')})
                sensor_dct[sensor['id']] = {'chassis-name': self.ch_name,
                                            'chassis-wwn': self.ch_wwn,
                                            'unit-number': sensor_id,
                                            'temperature': sensor['temperature'],
                                            'operational-state': sensor_state.upper(), 
                                            'operational-state-id': BrocadeFRUParser.SENSOR_STATE.get(sensor_state, 3), 
                                            'slot-number': sensor.get('slot-number'), 
                                            'index': sensor.get('index')}
        return sensor_dct    
    


    def _get_changed_fru_params(self, other, fru_type: str) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method detects if fru parameters have been changed for each fru.
        It compares fru parameters of two instances of BrocadeFRUParser class.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeFRUParser}: fru parameters class instance retrieved from the previous sw_telemetry.
            fru_type {str}: ps, fan, sensor.
        
        Returns:
            dict: FRU parameters change dictionary. Any fru with changed parameters are in this dictionary.
        """


        # fru with changed parameters
        fru_params_changed_dct = {}

        # other is not exist (for exaple 1st iteration)
        # other is not same class instance
        if other is None or str(type(self)) != str(type(other)):
            return

        if fru_type == 'ps':
            fru_params_dct_now = self.fru_ps
            fru_params_dct_prev = other.fru_ps
            changed_keys = BrocadeFRUParser.PS_CHANGED
        elif fru_type == 'fan':
            fru_params_dct_now = self.fru_fan
            fru_params_dct_prev = other.fru_fan
            changed_keys = BrocadeFRUParser.FAN_CHANGED
        elif fru_type =='sensor':
            fru_params_dct_now = self.fru_sensor
            fru_params_dct_prev = other.fru_sensor
            changed_keys = BrocadeFRUParser.SENSOR_CHANGED


        # other's params dict is empty
        if not fru_params_dct_prev:            
            return

        if not fru_params_dct_now:
            return fru_params_changed_dct
                
        # check if other is for the same switch
        if self.same_chassis(other):
            for id, current_fru in fru_params_dct_now.items():
                # if there is fru id in previous check next id 
                if id not in fru_params_dct_prev:
                    continue

                # fru params for the currrent fru id in the previous telemetry    
                prev_fru = fru_params_dct_prev[id]
                # timestamps
                time_now = self.telemetry_date + ' ' + self.telemetry_time
                time_prev = other.telemetry_date + ' ' + other.telemetry_time
                # get changed params
                
                current_changed_dct = BrocadeFRUParser.get_changed_chassis_params(current_fru, prev_fru, 
                                                                                   changed_keys=changed_keys, 
                                                                                   const_keys=['chassis-name', 'chassis-wwn', 'unit-number'], 
                                                                                   time_now=time_now, time_prev=time_prev)
                if current_changed_dct:
                    fru_params_changed_dct[id] = current_changed_dct
        return fru_params_changed_dct


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
    

    @property
    def fru_ps_changed(self):
        return self._fru_ps_changed


    @property
    def fru_fan_changed(self):
        return self._fru_fan_changed
        

    @property
    def fru_sensor_changed(self):
        return self._fru_sensor_changed