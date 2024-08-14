# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 01:19:28 2024

@author: kavlasenko
"""


from typing import Dict, List, Union

from prometheus_client import Gauge, start_http_server, CollectorRegistry



class BrocadeGauge:


    chassis_wwn_key = ['chassis-wwn']
    switch_wwn_key  = ['switch-wwn']
    


    # def __init__(self, name: str, description: str, label_keys: List[str], metric_key: str = None, reverse_filling: bool = False):

    #     self._registry = CollectorRegistry()
    #     self._name = name
    #     self._description  = description
    #     self._label_keys = label_keys
    #     self._metric_key = metric_key
    #     self._reverse_filling = reverse_filling
    #     # self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys), registry=self.registry)
    #     self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys))



    def __init__(self, name: str, description: str, unit_keys: List[str], parameter_key: str = None, metric_key: str = None, reverse_filling: bool = False):

        # self._registry = CollectorRegistry()
        self._name = name
        self._description  = description
        self._unit_keys = unit_keys
        self._parameter_key = parameter_key
        self._metric_key = metric_key
        self.validate_gauge_parameters()
        self._reverse_filling = reverse_filling
        self._label_keys = self._unit_keys + [self._parameter_key] if self._parameter_key else self._unit_keys

        # self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys), registry=self.registry)
        self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys))


    def validate_gauge_parameters(self):
        """Method checks if gauge instance is initialized with parameter or metric key.
        Gauge istance must have either parameter_key or metric_key passed as class parameter but not both.
        If parameter_key is passed then metric_key has to be None and vice versa"""

        if all(v is not None for v in [self.parameter_key, self.metric_key]):
            raise ValueError(f"{self.name} gauge of the {self.__class__.__name__} class has both parameter_key and metric_key. "
                             "Gauge is initialized with either parameter_key or metric_key.")
        elif all(v is None for v in [self.parameter_key, self.metric_key]):
            raise ValueError(f"{self.name} gauge of the {self.__class__.__name__} class has no parameter_key or metric_key. " 
                             "Gauge is initialized with either parameter_key or metric_key.")


    def fill_chassis_gauge_metrics(self, gauge_data: Union[List[dict], Dict]):

        if not gauge_data:
            return
        
        if isinstance(gauge_data, list):
            
            for gauge_data_current in gauge_data:
                self.add_gauge_metric(gauge_data_current)
        elif isinstance(gauge_data, dict):
            self.add_gauge_metric(gauge_data)

            
    def fill_chassis_components_gauge_metrics(self, gauge_data: Dict[int, Dict[str, Union[str, int]]]):

        if not gauge_data:
            return
        

        for gauge_data_component in gauge_data.values():
        
            if not gauge_data_component:
                continue

            if isinstance(gauge_data_component, dict):
                self.add_gauge_metric(gauge_data_component)
        
        



    def fill_switch_gauge_metrics(self, gauge_data: Dict[int, Dict],
                                  prerequisite_keys_all: List[str] = None, prerequisite_keys_any: List[str] = None,  
                                  renamed_keys: dict = None, update_dict:dict = None) -> None:
        
        if not gauge_data:
            return
        
        for gauge_data_switch in gauge_data.values():
        
            if not gauge_data_switch:
                continue
        
            if isinstance(gauge_data_switch, list):
                gauge_data_switch_ordered = gauge_data_switch[::-1] if self.reverse_filling else gauge_data_switch

                for gauge_data_current in gauge_data_switch_ordered:
                    self.add_gauge_metric(gauge_data_current)
            elif isinstance(gauge_data_switch, dict):

                if not BrocadeGauge.check_prerequisite_keys(gauge_data_switch, prerequisite_keys_all, prerequisite_keys_any):
                    continue

                gauge_data_switch_modified = BrocadeGauge.modify_dict(gauge_data_switch, renamed_keys, update_dict)

                self.add_gauge_metric(gauge_data_switch_modified)


                # self.add_gauge_metric(gauge_data_switch)



    def fill_port_gauge_metrics(self, gauge_data: Dict[int, Dict], 
                                prerequisite_keys_all: List[str] = None, prerequisite_keys_any: List[str] = None,  
                                renamed_keys: dict = None, add_dict:dict = None) -> None:
        
        if not gauge_data:
            return
        
        for gauge_data_switch in gauge_data.values():
        
            if not gauge_data_switch:
                continue

            for gauge_data_port in gauge_data_switch.values():

                # print(gauge_data_port)
                
                if not gauge_data_port:
                    continue
        

                if isinstance(gauge_data_port, dict):

                    # if prerequisite_keys_any and not any(key in gauge_data_port for key in prerequisite_keys_any):
                    #     continue

                    # if prerequisite_keys_all and not all(key in gauge_data_port for key in prerequisite_keys_all):
                    #     continue

                    if not BrocadeGauge.check_prerequisite_keys(gauge_data_port, prerequisite_keys_all, prerequisite_keys_any):
                        continue


                    gauge_data_port_modified = BrocadeGauge.modify_dict(gauge_data_port, renamed_keys, add_dict)
                    self.add_gauge_metric(gauge_data_port_modified)

                    # gauge_data_port_modified = gauge_data_port.copy()
                    
                    # if renamed_keys:
                    #     for key_old, key_new in renamed_keys.items():
                    #         gauge_data_port_modified[key_new] = gauge_data_port_modified.pop(key_old)

                    # if update_dict:
                    #     gauge_data_port_modified.update(update_dict)

                    # if renamed_keys or update_dict:
                    #     self.add_gauge_metric(gauge_data_port_modified)
                    # else:
                    #     self.add_gauge_metric(gauge_data_port)
                else:
                    print('NOT DICT')


    @staticmethod
    def check_prerequisite_keys(checked_dict: dict, 
                                prerequisite_keys_all: List[str] = None, 
                                prerequisite_keys_any: List[str] = None) -> bool:
        """Method checks if prerequisite keys are in the dictionary.

        Args:
            checked_dict (dict): dictionary which need to be checked.
            prerequisite_keys_all (List[str], optional): True if all keys from the list are in the checked_dict. Defaults to None.
            prerequisite_keys_any (List[str], optional): True if any key from the list are in the checked_dict. Defaults to None.

        Returns:
            bool: True if all conditions from the parameters are met.
        """

        prerequisites_met = True

        if prerequisite_keys_any and not any(key in checked_dict for key in prerequisite_keys_any):
            prerequisites_met = False

        if prerequisite_keys_all and not all(key in checked_dict for key in prerequisite_keys_all):
            prerequisites_met = False

        return prerequisites_met


    @staticmethod
    def modify_dict(original_dict: dict, renamed_keys: dict = None, add_dict:dict = None):
        """Method to change original disctionary.

        Args:
            original_dict (dict): dictionary which need to be changed.
            renamed_keys (dict, optional): Key is old key name, value is a new key name.
            modified_dict (dict, optional): Key is a key name, value is a new value for the key.

        Returns:
            dict: modified dictionary.
        """

        modified_dict = original_dict.copy()
        
        if renamed_keys:
            for key_old, key_new in renamed_keys.items():
                modified_dict[key_new] = modified_dict.pop(key_old)

        if add_dict:
            modified_dict.update(add_dict)
        
        return modified_dict
        

    def add_gauge_metric(self, gauge_data):
        label_values = BrocadeGauge.get_ordered_values(gauge_data, self.label_keys)
        # metric_value = gauge_data[self.metric_key] if self.metric_key is not None else 1

        if self.metric_key:
            metric_value = gauge_data[self.metric_key]
        elif self.parameter_key:
            if gauge_data[self.parameter_key] is None:
                metric_value = 0
            else:
                metric_value = 1

        if metric_value is not None:
            self.gauge.labels(*label_values).set(metric_value)


    @staticmethod
    def get_ordered_values(values_dct, keys, fillna='no data'):

        values_lst = [values_dct.get(key) for key in keys]
        if fillna is not None:
            values_lst = [value if value is not None else fillna for value in values_lst]
        return values_lst
    

    @staticmethod
    def replace_underscore(keys: List[str], char='_'):
        return [key.replace('-', char) for key in keys]
    

    @property
    def registry(self):
        return self._registry
    

    @property
    def name(self):
        return self._name
    

    @property
    def description(self):
        return self._description
    
    
    @property
    def unit_keys(self):
        return self._unit_keys


    @property
    def parameter_key(self):
        return self._parameter_key


    @property
    def label_keys(self):
        return self._label_keys
    

    @property
    def metric_key(self):
        return self._metric_key
    

    @property
    def reverse_filling(self):
        return self._reverse_filling


    @property
    def gauge(self):
        return self._gauge
