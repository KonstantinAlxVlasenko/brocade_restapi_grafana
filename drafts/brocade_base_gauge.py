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


    def __init__(self, name: str, description: str, label_keys: List[str], metric_key: str = None):

        self._registry = CollectorRegistry()
        self._name = name
        self._description  = description
        self._label_keys = label_keys
        self._metric_key = metric_key
        # self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys), registry=self.registry)
        self._gauge = Gauge(self.name, self.description, BrocadeGauge.replace_underscore(self._label_keys))

    # def gauge_init(self, name: str, description: str, label_names: List[str]):

    #     return Gauge(name, description, BrocadeGauge.replace_underscore(label_names))


    # def fill_chassis_gauge_metrics_(self, gauge_instance: Gauge, gauge_data: Union[List[dict], Dict], label_names: List[str], metric_name: str=None):
        
        
    #     if not gauge_data:
    #         return
        
    #     if isinstance(gauge_data, list):
            
    #         for gauge_data_current in gauge_data:
    #             self.add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
    #     elif isinstance(gauge_data, dict):
    #         self.add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name)



    def fill_chassis_gauge_metrics(self, gauge_data: Union[List[dict], Dict]):

        if not gauge_data:
            return
        
        if isinstance(gauge_data, list):
            
            for gauge_data_current in gauge_data:
                self.add_gauge_metric(gauge_data_current)
        elif isinstance(gauge_data, dict):
            self.add_gauge_metric(gauge_data)

            
    # def fill_switch_gauge_metrics(self, gauge_instance: Gauge, gauge_data: Dict[int, Dict], 
    #                                     label_names: List[str], metric_name: str=None, reverse=False):
        
    #     if not gauge_data:
    #         return
        
    #     for gauge_data_switch in gauge_data.values():
        
    #         if not gauge_data_switch:
    #             continue
        
    #         if isinstance(gauge_data_switch, list):
    #             gauge_data_switch_ordered = gauge_data_switch[::-1] if reverse else gauge_data_switch
                    
    #             for gauge_data_current in gauge_data_switch_ordered:
    #                 self.add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
    #         elif isinstance(gauge_data_switch, dict):
    #             self.add_gauge_metric(gauge_instance, gauge_data_switch, label_names, metric_name)
        

    def add_gauge_metric(self, gauge_data):
        label_values = BrocadeGauge.get_ordered_values(gauge_data, self.label_keys)
        metric_value = gauge_data[self.metric_key] if self.metric_key is not None else 1
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
    

    # @property
    # def labelkeys(self):
    #     return self._labelkeys
    

    @property
    def label_keys(self):
        return self._label_keys
    

    @property
    def metric_key(self):
        return self._metric_key


    @property
    def gauge(self):
        return self._gauge
