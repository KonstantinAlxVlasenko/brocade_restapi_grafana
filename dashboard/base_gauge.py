from typing import Dict, List, Union

from prometheus_client import Gauge


class BaseGauge:
    """
    Class to create a prometheus gauge for Brocade switch.
    Each gauge must have either parameter_key or metric_key passed as class parameter but not both.

    Attributes:
        name (str): Gauge unique name.
        description (str): Gauge help.
        unit_keys (List[str]): Gauge labels.
        parameter_key (str, optional): Gauge parameter key contains string type value or value converted to string (added to gauge labels). 
        metric_key (str, optional): Gauge metric key contains numeric type value (used as metric value in set method).
        reverse_filling (bool, optional): Gauge reverse filling flag. Applied if switch parsed data presented as list.
    """

    chassis_wwn_key = ['chassis-wwn']
    switch_wwn_key  = ['switch-wwn']
    

    def __init__(self, 
                 name: str, description: str, unit_keys: List[str], 
                 parameter_key: str = None, metric_key: str = None, 
                 reverse_filling: bool = False):
        """
        Class constructor.

        Args:
            name (str): Gauge unique name.
            description (str): Gauge help.
            unit_keys (List[str]): Gauge labels.
            parameter_key (str, optional): Gauge parameter key contains string type value or value converted to string (added to gauge labels). 
            metric_key (str, optional): Gauge metric key contains numeric type value (used as metric value in set method).
            reverse_filling (bool, optional): Gauge reverse filling flag. Applied if switch parsed data presented as list.
        """

        # self._registry = CollectorRegistry()
        self._name = name
        self._description  = description
        self._unit_keys = unit_keys
        self._parameter_key = parameter_key
        self._metric_key = metric_key
        self.validate_gauge_parameters()
        self._reverse_filling = reverse_filling
        self._label_keys = self._unit_keys + [self._parameter_key] if self._parameter_key else self._unit_keys
        self._gauge = Gauge(self.name, self.description, BaseGauge.replace_underscore(self._label_keys))


    def validate_gauge_parameters(self) -> None:
        """
        Method checks if gauge instance is initialized with parameter or metric key.
        Gauge istance must have either parameter_key or metric_key passed as class constructor parameter but not both.
        If parameter_key is passed then metric_key has to be None and vice versa.
        """

        # check if both parameter_key and metric_key are passed
        if all(v is not None for v in [self.parameter_key, self.metric_key]):
            raise ValueError(f"{self.name} gauge of the {self.__class__.__name__} class has both parameter_key and metric_key. "
                             "Gauge is initialized with either parameter_key or metric_key.")
        # chaeck if neiither parameter_key nor metric_key are passed
        elif all(v is None for v in [self.parameter_key, self.metric_key]):
            raise ValueError(f"{self.name} gauge of the {self.__class__.__name__} class has no parameter_key or metric_key. " 
                             "Gauge is initialized with either parameter_key or metric_key.")


    def fill_chassis_gauge_metrics(self, gauge_data: List[Dict]):
        """
        Method to unpack gauge_data to get chassis level dictionaries.
        Each unpacked dictionary contains key, value pairs to fill gauge labels and set gauge metric.
        
        Args:
            gauge_data (List[Dict]): List of dictionaries. Each dictionary contains chassis level element parameters.     
        """

        if not gauge_data:
            return
        
        if isinstance(gauge_data, list):
            for gauge_data_current in gauge_data:
                self.add_gauge_metric(gauge_data_current)
        # elif isinstance(gauge_data, dict):
        #     self.add_gauge_metric(gauge_data)


    def fill_switch_gauge_metrics(self, 
                                  gauge_data: Dict[int, Union[Dict, List[Dict]]],
                                  prerequisite_keys_all: List[str] = None, prerequisite_keys_any: List[str] = None,  
                                  renamed_keys: dict = None, add_dict:dict = None,
                                  storage_lst: list = None) -> None:
        """Method to unpack gauge_data to get switch level dictionaries.
        Each unpacked dictionary contains key, value pairs to fill gauge labels and set gauge metric.
        
        Args:
            gauge_data (Dict[int, Union[Dict, List[Dict]]]): Nested dictionaries. Each dictionary contains switch level element parameters.
            storage_lst (list): list to store dictionaries which are added to the gauge.     
        """
        
        if not gauge_data:
            return
        
        # gauge_data_switch for the current vfid 
        for gauge_data_switch in gauge_data.values():
        
            if not gauge_data_switch:
                continue
            # gauge_data_switch is a list of switch level dictionaries
            if isinstance(gauge_data_switch, list):
                gauge_data_switch_ordered = gauge_data_switch[::-1] if self.reverse_filling else gauge_data_switch
                
                for gauge_data_current in gauge_data_switch_ordered:
                    self.add_gauge_metric(gauge_data_current)
            # gauge_data_switch is a switch level dictionary
            elif isinstance(gauge_data_switch, dict):
                # check if dictionary contains required keys
                if not BaseGauge.check_prerequisite_keys(gauge_data_switch, prerequisite_keys_all, prerequisite_keys_any):
                    continue
                # rename existing keys or add new key, value pairs
                gauge_data_switch_modified = BaseGauge.modify_dict(gauge_data_switch, renamed_keys, add_dict)
                if storage_lst is not None:
                    storage_lst.append(gauge_data_switch_modified)
                self.add_gauge_metric(gauge_data_switch_modified)


    def fill_port_gauge_metrics(self, 
                                gauge_data: Dict[int, Dict[str, Dict]], 
                                prerequisite_keys_all: List[str] = None, prerequisite_keys_any: List[str] = None,  
                                renamed_keys: dict = None, add_dict:dict = None,
                                storage_lst: list = None) -> None:
        """Method to unpack gauge_data to get port level dictionaries.
        Each unpacked dictionary contains key, value pairs to fill gauge labels and set gauge metric.
        
        Args:
            gauge_data (Dict[int, Dict[str, Dict]]): Nested dictionaries. Each dictionary contains port level element parameters.
            storage_lst (list): list to store dictionaries which are added to the gauge.
        """
        
        if not gauge_data:
            return
        
        # gauge_data_switch for the current vfid
        for gauge_data_switch in gauge_data.values():
        
            if not gauge_data_switch:
                continue

            # gauge_data_port for the current port
            for gauge_data_port in gauge_data_switch.values():
                
                if not gauge_data_port:
                    continue
                # gauge_data_port is a port level dictionary
                if isinstance(gauge_data_port, dict):
                    # check if dictionary contains required keys
                    if not BaseGauge.check_prerequisite_keys(gauge_data_port, prerequisite_keys_all, prerequisite_keys_any):
                        continue
                    # rename existing keys or add new key, value pairs
                    gauge_data_port_modified = BaseGauge.modify_dict(gauge_data_port, renamed_keys, add_dict)
                    if storage_lst is not None:
                        storage_lst.append(gauge_data_port_modified)
                    self.add_gauge_metric(gauge_data_port_modified)
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
            bool: True if all conditions from the parameters are met otherwise False.
        """

        prerequisites_met = True

        # if none of the prerequisite_keys_any are in the checked_dict
        if prerequisite_keys_any and not any(key in checked_dict for key in prerequisite_keys_any):
            prerequisites_met = False
        # if not all the keys from the prerequisite_keys_all are in the checked_dict
        if prerequisite_keys_all and not all(key in checked_dict for key in prerequisite_keys_all):
            prerequisites_met = False
        return prerequisites_met


    @staticmethod
    def modify_dict(original_dict: dict, renamed_keys: dict = None, add_dict:dict = None) -> None:
        """Method to change original disctionary. 
        Rename keys or add new key, value pairs to the dictionary.

        Args:
            original_dict (dict): dictionary which need to be changed.
            renamed_keys (dict, optional): Key is old key name, value is a new key name.
            add_dict (dict, optional): Key is a key name, value is a new value for the key.

        Returns:
            dict: modified dictionary.
        """

        modified_dict = original_dict.copy()
        # rename keys
        if renamed_keys:
            for key_old, key_new in renamed_keys.items():
                modified_dict[key_new] = modified_dict.pop(key_old)
        # add new key, value pairs
        if add_dict:
            modified_dict.update(add_dict)
        return modified_dict
        

    def add_gauge_metric(self, gauge_data: Dict[str, Union[str, int]]) -> None:
        """Method to set metric to prometheus gauge.

        Args:
            gauge_data (dict): dictionary contains values to set metric for the corresponding gauge labels.
        """

        # get values for gauge labels from gauge_data
        label_values = BaseGauge.get_ordered_values(gauge_data, self.label_keys)

        # get gauge metric numeric value from gauge_data
        if self.metric_key:
            metric_value = gauge_data[self.metric_key]
        # if gauge parameter_key is defined it's added to the labels
        # and metric value is 0 or 1 depending on the parameter_key value
        elif self.parameter_key:
            # parameter_key value is None -> metric value is 0
            if gauge_data[self.parameter_key] is None:
                metric_value = 0
            # parameter_key value is not None -> metric value is 1
            else:
                metric_value = 1
        # add non empty metric to the gauge
        if metric_value is not None:
            self.gauge.labels(*label_values).set(metric_value)


    @staticmethod
    def get_ordered_values(values_dct: Dict[str, Union[str, int]], 
                           keys: List[str], fillna: str = 'no data') -> list:
        """Method to get ordered values from the dictionary.

        Args:
            values_dct (dict): dictionary contains values.
            keys (list): keys to get values.
            fillna (str, optional): value to replace None. Defaults to 'no data'.

        Returns:
            list: ordered values.
        """

        values_lst = [values_dct.get(key) for key in keys]
        if fillna is not None:
            values_lst = [value if value is not None else fillna for value in values_lst]
        return values_lst
    

    @staticmethod
    def replace_underscore(keys: List[str], char='_') -> List[str]:
        """Method to replace underscore in keys.

        Args:
            keys (List[str]): keys to check underscore.
            char (str): Replace underscore with the char. Defaults to '_'.

        Returns:
            List[str]: keys with replaced underscores.
        """

        return [key.replace('-', char) for key in keys]
    

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
