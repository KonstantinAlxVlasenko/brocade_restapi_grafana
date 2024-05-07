# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 17:08:32 2024

@author: kavlasenko
"""

import math
import numbers
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from brocade_telemetry_parser_cls import BrocadeTelemetryParser
from quantiphy import Quantity
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser


class BrocadeFCPortStatisticsParser(BrocadeTelemetryParser):
    """
    Class to create fc port statistics dictionaries.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        fcport_params_parser: fc port parameters class instance retrieved from the sw_telemetry.
        fcport_stats_parser: fc port stats class instance retrieved from the sw_telemetry (current class instance to find delta).
        fcport_stats: fc port statistics dictionary ({vf_id:{slot_port_id:{counter1: value1, counter2: value2}}}).
        fcport_stats_growth: fc port statistics dictionary for ports with increased counters except FC_STATISTICS_STAT_LEAFS
    """
    

    FC_STATISTICS_PARAMS_LEAFS = ['name', 'sampling-interval', 'time-generated',
                                  'in-peak-rate', 'in-rate', 'out-peak-rate', 'out-rate']

    FC_STATISTICS_STAT_LEAFS = ['in-frames', 'out-frames', 'class-3-frames', 'in-lcs'] 
    
    HIGH_SEVERITY_ERROR_LEAFS = ['class3-in-discards', 'class3-out-discards', 'class-3-discards', 
                                  'crc-errors', 'in-crc-errors', 'remote-crc-errors', 'remote-fec-uncorrected', 
                                  'pcs-block-errors',  'truncated-frames', 'bad-eofs-received', 
                                  'frames-too-long', 'frames-timed-out'
                                  ]
    
    MEDIUM_SEVERITY_ERROR_LEAFS = ['address-errors', 'delimiter-errors', 'encoding-disparity-errors', 
                                    'frames-transmitter-unavailable-errors', 
                                    'multicast-timeouts', 'too-many-rdys', 
                                    'f-busy-frames', 'f-rjt-frames', 'p-busy-frames', 'p-rjt-frames', 
                                    'primitive-sequence-protocol-error',
                                    'remote-primitive-sequence-protocol-error', 'frames-processing-required',
                                    'invalid-transmission-words', 'remote-invalid-transmission-words']
    
    LOW_SEVERITY_ERROR_LEAFS = ['encoding-errors-outside-frame',  'invalid-ordered-sets']

    OTHER_COUNTER_LEAFS = ['bb-credit-zero']
    
    LINK_ERROR_LEAFS = ['loss-of-signal', 'loss-of-sync', 'link-failures', 
                        'in-link-resets', 'out-link-resets', 
                        'in-offline-sequences', 'out-offline-sequences',
                        'link-level-interrpts',
                        'remote-link-failures', 'remote-loss-of-signal', 'remote-loss-of-sync']
    
    FC_STATISTICS_COUNTER_LEAFS = (FC_STATISTICS_STAT_LEAFS + 
                                    HIGH_SEVERITY_ERROR_LEAFS + 
                                    MEDIUM_SEVERITY_ERROR_LEAFS + 
                                    LOW_SEVERITY_ERROR_LEAFS +
                                    LINK_ERROR_LEAFS +
                                    OTHER_COUNTER_LEAFS)
    
    FC_STATISTICS_LEAFS = FC_STATISTICS_PARAMS_LEAFS + FC_STATISTICS_COUNTER_LEAFS
    
    FC_PORT_PARAMS = ['swicth-name', 'port-name', 'physical-state', 
                      'port-enable-status', 'link-speed', 'port-type', 'speed']
    
    DELTA_TAG = '-delta'
    HRF_TAG = '-hrf'
    
    LROUT_SUBTRACT_OLSIN_LEAF = 'lrout' + DELTA_TAG + '_subtract_olsin' + DELTA_TAG
    LRIN_SUBTRACT_OLSOUT_LEAF = 'lrin' + DELTA_TAG + '_subtract_olsout' + DELTA_TAG

    LR_SUBTRACT_OLS_LEAFS = [LROUT_SUBTRACT_OLSIN_LEAF, LRIN_SUBTRACT_OLSOUT_LEAF]

    COUNTER_THRESHOLDS = {'high_severity': {'warning': 10, 'critical': 30},
                          'medium_severity': {'warning': 30, 'critical': 100},
                          'low_severity': {'warning': 30, 'critical': 100},
                          'link_error': {'warning': 10, 'critical': 20},
                          'lr_substract_ols': {'warning': 30, 'critical': 100}}
    
    PORT_ERROR_STATUS_TAG = '-severity-error_port-status'

    ERROR_SEVERITY_TYPES = ['high','medium', 'low']

    PORT_ERROR_STATUS_KEYS = [severity + '-severity-error_port-status' for severity in ERROR_SEVERITY_TYPES]

    COUNTER_CATEGORY_KEYS = [severity + '-severity_' + counter_status + '-status_errors' 
                             for severity in ERROR_SEVERITY_TYPES for counter_status in ['critical', 'warning']]
    
    PORT_ERROR_STATUS_ID = {'ok': 1, 'unknown': 2, 'warning': 3, 'critical': 4}

    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fcport_params_parser: BrocadeSwitchParser, fcport_stats_prev=None):
        """
        Args:
            sw_telemetry {BrocadeSwitchTelemetry}: set of switch telemetry retrieved from the switch.
        """
        
        super().__init__(sw_telemetry)
        self._fcport_params_parser: BrocadeSwitchParser = fcport_params_parser
        self._fcport_stats = self._get_port_stats_values()
        if self.fcport_stats:
            self._fcport_stats_growth = self._calculate_counters_growth(fcport_stats_prev)
        else:
            self._fcport_stats_growth = {}
    

    def _get_port_stats_values(self) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method retrieves each fc port statistics from the switch telemetry.
        
        Returns:
            dict: FC port statistics. Dictionary of dictionaries of dictionaries.
                External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
                First level nested dictionary keys are slot_port_numbers.
                Second level nested dictionary keys are fc port counters names.
        """
        
        fcport_stats_dct = {}

        for vf_id, fc_statistics_telemetry in self.sw_telemetry.fc_statistics.items():
            if fc_statistics_telemetry.get('Response'):
                # list with fc_interface statistics containers for the each port in the vf_id switch
                fc_statistics_container_lst = fc_statistics_telemetry['Response']['fibrechannel-statistics']
                # create fc statistics empty dictionary for the current vf_id
                fcport_stats_dct[vf_id] = {}
                
                for fc_statistics_container in fc_statistics_container_lst:
                    # get port statistics from the container
                    fcport_stats_current_dct = {leaf: fc_statistics_container.get(leaf) for leaf in BrocadeFCPortStatisticsParser.FC_STATISTICS_LEAFS}
                    # convert counters to the human readable format
                    fcport_stats_current_hrf_dct = {leaf + BrocadeFCPortStatisticsParser.HRF_TAG: BrocadeFCPortStatisticsParser.int_to_hrf(fc_statistics_container.get(leaf)) 
                                                    for leaf in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS}
                    # add hrf counters to the fc port statistics dictionary
                    fcport_stats_current_dct.update(fcport_stats_current_hrf_dct)




                    # slot_port_number in the format 'slot_number/port_number' (e.g. '0/1')
                    slot_port_number = fc_statistics_container['name']
                    # split slot and port number
                    slot_number, port_number = slot_port_number.split('/')
                    fcport_stats_current_dct['slot-number'] = int(slot_number)
                    fcport_stats_current_dct['port-number'] = int(port_number)
                    # convert seconds to the human readable format datetime
                    fcport_stats_current_dct['time-generated-hrf'] = BrocadeFCPortStatisticsParser.epoch_to_datetime(fc_statistics_container['time-generated'])
                    # add port parameters to the fc port statistics dictionary
                    fcport_params_dct = self._get_port_params(vf_id, slot_port_number)
                    fcport_stats_current_dct.update(fcport_params_dct)

                    # convert speeds bytes to bits
                    for rate_key in ['in-peak-rate', 'in-rate', 'out-peak-rate', 'out-rate']:
                        rate_bits_key = rate_key + '-bits'
                        fcport_stats_current_dct[rate_bits_key] = BrocadeFCPortStatisticsParser.bytes_to_bits(fcport_stats_current_dct[rate_key])
                        fcport_stats_current_dct[rate_key + '-%'] = BrocadeFCPortStatisticsParser.get_percentage(fcport_stats_current_dct[rate_bits_key], fcport_stats_current_dct['speed'])
                        if not 'peak' in  rate_key:
                            print(fcport_stats_current_dct['port-number'], fcport_stats_current_dct['physical-state'], rate_key + '-%', fcport_stats_current_dct[rate_bits_key], fcport_stats_current_dct['speed'], fcport_stats_current_dct[rate_key + '-%'])


                    # add current fc port statistics dictionary to the summary port statistics dictionary with vf_id and slot_port as consecutive keys
                    fcport_stats_dct[vf_id][fc_statistics_container['name']] = fcport_stats_current_dct
        return fcport_stats_dct
    

    def _get_port_params(self, vf_id: int, slot_port_number: str) -> Dict[str, Optional[str]]:
        """
        Method to get port parameters.
        
        Args:
            vf_id {int}: switch vf_id.
            slot_port_number {str}: slot and port number in the format'slot/port' (e.g. '0/1').
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with FC_PORT_PARAMS values.
        """
        
        fc_port_params_current = self.fcport_params_parser.fcport_params[vf_id][slot_port_number]
        fcport_params = {param: fc_port_params_current.get(param) for param in BrocadeFCPortStatisticsParser.FC_PORT_PARAMS}
        return fcport_params


    @staticmethod
    def get_percentage(part: int, whole: int) -> float:
        if part is not None and whole is not None:
            return round(100 * part/whole, 2)


    @staticmethod
    def bytes_to_bits(bytes: int) -> int:
        if bytes is not None:
            return 8 * bytes


    @staticmethod
    def int_to_hrf(counter: int, precision: int = 1) -> str:
        """
        Method converts integer counters to the hrf format with k (10^3), m (10^6) and g (10^9 )endings.
        
        Returns:
            str: Integer counter in hrf format (3_600_000 -> 3,6m).
        """

        if isinstance(counter, numbers.Number):
            if counter:
                # maximum degree of ten which is a multiple of three to have base counter value in the interval betweeb 1 and 999
                exponent = int(math.floor(math.log10(abs(counter))/3.0)*3)
                # raise precision if base counter value is >=10 to have 1 digit after ','
                if counter / 10**exponent >= 10:
                    precision += 1
            return Quantity(counter).render(prec=precision).lower()


    def _calculate_counters_growth(self, other) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method calculates counters delta between two instances of BrocadeFCPortStatisticsParser class
        and adds delta to the current (self) instance of class.
        
        Args:
            other {BrocadeFCPortStatisticsParser}: fc port stats class instance retrieved from the sw_telemetry.
        
        Returns:
            dict: FC ports statistics growth dictionary. Any port with increased counters except FC_STATISTICS_STAT_LEAFS are in this dictionary.
        """

        fcport_stats_growth_dct = {}

        # other is not exist (for examle 1st iteration)
        # other is not BrocadeFCPortStatisticsParser type
        # other's fcport_stats atrribute is empty
        # add empty delta keys to the each port stats dictionary
        if other is None or str(type(self)) != str(type(other)) or not other.fcport_stats:
            for fcport_stats_vfid_now_dct in self.fcport_stats.values():
                for fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.values():
                    # BrocadeFCPortStatisticsParser._add_empty_fields(fc_statistics_port_now_dct)
                    self._add_empty_fields(fc_statistics_port_now_dct)
        
        # check if other is for the same switch
        elif self.same_chassis(other):
            for vf_id, fcport_stats_vfid_now_dct in self.fcport_stats.items():

                fcport_stats_growth_dct[vf_id] = {}

                # if there is no vf_id in other add empty delta keys to the each port stats dictionary 
                if vf_id not in other.fcport_stats:
                    for fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.values():
                        self._add_empty_fields(fc_statistics_port_now_dct)
                    continue
                    
                fcport_stats_vfid_prev_dct = other.fcport_stats[vf_id]
                for slot_port, fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.items():
                    # if there is no port number in other add empty delta keys to this port stats dictionary
                    if slot_port not in fcport_stats_vfid_prev_dct:
                        self._add_empty_fields(fc_statistics_port_now_dct)
                        continue
                    
                    # current fc port statistics from the other
                    fc_statistics_port_prev_dct = fcport_stats_vfid_prev_dct[slot_port]
                    # find delta for each fc port counter
                    fcport_stats_growth_port_dct = self._get_port_counters_delta(fc_statistics_port_now_dct, fc_statistics_port_prev_dct)
                    # if switch operates normally LR_OUT and OLS_IN values must be equal
                    self._detect_lr_ols_inconsistency(fc_statistics_port_now_dct, fcport_stats_growth_port_dct, lr_type='lr_out')
                    # if switch operates normally LR_IN and OLS_OUT values must be equal
                    self._detect_lr_ols_inconsistency(fc_statistics_port_now_dct, fcport_stats_growth_port_dct, lr_type='lr_in')
                    # add timestamp from the other to the current port statistics to see time period for which delta in counted for
                    fc_statistics_port_now_dct['time-generated-prev-hrf'] = fc_statistics_port_prev_dct['time-generated-hrf']
                    # add 'unknown' porterr summary status for high, medium and low severity counters if it doesn't exist 
                    self._add_unknown_port_error_status_fields(fc_statistics_port_now_dct)
                    # add None for list of errors for critical and warning categories if doesn't exist 
                    self._add_empty_error_category_fields(fc_statistics_port_now_dct)
                    # if stat counters (transmitted and received frames etc, see FC_STATISTICS_STAT_LEAFS) 
                    # increased only then drop stats dictionary coz error counters are not increasing
                    # otherwise add increased port counters stats to the fcport_stats_growth_dct
                    self._update_fcport_stats_growth(fcport_stats_growth_dct, fcport_stats_growth_port_dct, fc_statistics_port_now_dct, vf_id, slot_port)
        return fcport_stats_growth_dct    


    # @staticmethod
    # def _save_positive_counter_delta(delta_dct, slot_port, counter_name, delta_value):
    #     if delta_value and delta_value > 0:
    #         if not slot_port in delta_dct:
    #             delta_dct[slot_port] = {counter_name: delta_value}
    #         else:
    #             delta_dct[slot_port].update({counter_name: delta_value})    


    def _update_fcport_stats_growth(self, fcport_stats_growth_dct: dict, fcport_stats_growth_port_dct: dict, 
                                    fc_statistics_port_now_dct: dict, vf_id: int, slot_port: str) -> None:
        """
        Method adds slot_port statistics to the switch fcports statistics growth dictionary if error counters is greater than 0.
        fcport_stats_growth_port_dct contains switch ports with increased counters only.
        
        Args:
            fcport_stats_growth_dct {dict}: dictionary with ports for which error counters have increased.
            fcport_stats_growth_port_dct {dict}: dictionary with increased counters for current slot_port (not error counters only). 
            fc_statistics_port_now_dct {dict}: fc statistics dictionary for the current slot_port.
            vf_id {int}: switch vf_id.
            slot_port {str}: slot and port number in the format'slot/port' (e.g. '0/1').
        
        Returns:
            None.
        """

        # if increased counters are stats counters only (FC_STATISTICS_STAT_LEAFS), 
        # i.e total received and transmitted frames and any other counter hasn't incresed
        # then this port growth stats is not added to the switch port growth stats dictionary
        if fcport_stats_growth_port_dct and not set(fcport_stats_growth_port_dct.keys()).issubset(
            set([leaf + BrocadeFCPortStatisticsParser.DELTA_TAG for leaf in BrocadeFCPortStatisticsParser.FC_STATISTICS_STAT_LEAFS])):
            # add time stamps of the both stats for which delta is counted for
            fcport_stats_growth_port_dct['time-generated-hrf'] = fc_statistics_port_now_dct['time-generated-hrf']
            fcport_stats_growth_port_dct['time-generated-prev-hrf'] = fc_statistics_port_now_dct['time-generated-prev-hrf']
            # add port parameters to the fc port statistics dictionary
            fcport_params_dct = self._get_port_params(vf_id, slot_port)
            fcport_stats_growth_port_dct.update(fcport_params_dct)
            # add slot port information
            fcport_stats_growth_port_dct['slot-number'] = fc_statistics_port_now_dct['slot-number']
            fcport_stats_growth_port_dct['port-number'] = fc_statistics_port_now_dct['port-number']
            # add increased port counters stats to the fcport_stats_growth_dct
            fcport_stats_growth_dct[vf_id][slot_port] = fcport_stats_growth_port_dct
                                   

    def _get_port_counters_delta(self, fc_statistics_port_now_dct: dict, fc_statistics_port_prev_dct: dict) -> dict:
        """
        Method calculates delta between same counters of the curren port statistics and previous port statistics.
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            fc_statistics_port_prev_dct {dict}: previous fc port statistics dictionary to calculate delate with. 
        
        Returns:
            dict: dictionary with increased counters.
        """

        # dictionary with increased counters for slot_port
        fcport_stats_growth_port_dct = {}
        
        # find delta for each fc port counter
        for counter in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS:
            counter_delta = counter + BrocadeFCPortStatisticsParser.DELTA_TAG
            # find delta if both counters are not None
            if fc_statistics_port_prev_dct[counter] is None or fc_statistics_port_now_dct[counter] is None:
                fc_statistics_port_now_dct[counter_delta] = None
            else:
                delta = fc_statistics_port_now_dct[counter] - fc_statistics_port_prev_dct[counter]
                
                fc_statistics_port_now_dct[counter_delta] = delta
                if counter in BrocadeFCPortStatisticsParser.HIGH_SEVERITY_ERROR_LEAFS:
                    self._add_error_status_and_categorize_error(fc_statistics_port_now_dct, delta, 
                                                                counter_thresholds_key='high_severity', counter_name=counter, severity='high')
                elif counter in BrocadeFCPortStatisticsParser.MEDIUM_SEVERITY_ERROR_LEAFS:
                    self._add_error_status_and_categorize_error(fc_statistics_port_now_dct, delta, 
                                                                counter_thresholds_key='medium_severity', counter_name=counter, severity='medium')
                elif counter in BrocadeFCPortStatisticsParser.LOW_SEVERITY_ERROR_LEAFS:
                    self._add_error_status_and_categorize_error(fc_statistics_port_now_dct, delta, 
                                                                counter_thresholds_key='low_severity', counter_name=counter, severity='low')
                elif counter in BrocadeFCPortStatisticsParser.LINK_ERROR_LEAFS:
                    self._add_error_status_and_categorize_error(fc_statistics_port_now_dct, delta, 
                                                                counter_thresholds_key='link_error', counter_name=counter, severity='high')

                # save the delta to the fc port statistics dictionary
                BrocadeFCPortStatisticsParser.save_positive_value(fcport_stats_growth_port_dct, counter_delta, delta)
        return fcport_stats_growth_port_dct



    def _add_error_status_and_categorize_error(self, fc_statistics_port_now_dct: dict, counter_delta, 
                                               counter_thresholds_key: str, counter_name: str, severity: str) -> None:
        """
        Method adds error status to the fc port statistics dictionary and categorizes error.
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            counter_name {str}: name of the counter.
            counter_status {str}: status of the counter.
            severity {str}: severity of the error.
        """
                
        counter_status = BrocadeFCPortStatisticsParser.get_error_status(counter_delta, BrocadeFCPortStatisticsParser.COUNTER_THRESHOLDS[counter_thresholds_key])
        self._update_port_error_status(fc_statistics_port_now_dct, counter_status, severity)
        self._categorize_error(fc_statistics_port_now_dct, counter_name, counter_status, severity)
                


    def _categorize_error(self, fc_statistics_port_now_dct, counter_name, counter_status, severity: str) -> None:

        """
        Method categorizes error statuses of the fc port statistics.
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            severity {str}: severity of the error status.
        
        Returns:
            None
        """
                
        if counter_status == 'ok':
            return
        
        counter_category = severity + '-severity_' + counter_status + '-status_errors'
        if counter_category in fc_statistics_port_now_dct:
            fc_statistics_port_now_dct[counter_category].append(counter_name)
        else:
            fc_statistics_port_now_dct[counter_category] = [counter_name]
        


    def _update_port_error_status(self, fc_statistics_port_now_dct: dict,  counter_status, severity: str) -> None:

        counter_status_key = severity + BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_TAG
        counter_status_id_key = severity + BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_TAG + '-id'
        counter_status_id = BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_ID[counter_status]
        if fc_statistics_port_now_dct.get(counter_status_id_key):
            if counter_status_id > fc_statistics_port_now_dct[counter_status_id_key]:
                fc_statistics_port_now_dct[counter_status_key] = counter_status
                fc_statistics_port_now_dct[counter_status_id_key] = counter_status_id
        else:
            fc_statistics_port_now_dct[counter_status_key] = counter_status
            fc_statistics_port_now_dct[counter_status_id_key] = counter_status_id


    @staticmethod
    def get_error_status(value: float, status_intervals_dct: dict) -> str:
        """
        Method checks to which interval value belongs to and returns corresponding status.
        '0--------warning--------critical--------'
        
        Args:
            value {float}: value checked to which interval it belongs to.
            status_intervals_dct {dict}: dictionary with intervals 
            {'high-alarm': x, 'low-alarm': y, 'high-warning': z, 'low-warning': w}
        
        Returns:
            str: 'ok', 'warning', 'critical'
        """

        status = 'unknown'
        if value < 0:
            return status

        if value >= 0 and value < status_intervals_dct['warning']:
            status = 'ok'
        elif value >= status_intervals_dct['warning'] and value < status_intervals_dct['critical']:
            status = 'warning'                  
        elif value >= status_intervals_dct['critical']:
            status = 'critical'
        return status


    def _detect_lr_ols_inconsistency(self, fcport_stats_dct: dict, fcport_stats_growth_dct: dict, lr_type: str) -> None:
        """
        Method detects inconsistency between Link reset and Offline state counters deltas.
        Lr_in and Ols_out values must be equal.
        Lr_out and Ols_in values must be equal.
        Inconsistency indicates link errors.
        
        Args:
            fc_statistics_port_now_dct {dict}: fc port statistics dictionary for the current sw telemetry.
            fcport_stats_growth_port_dct {dict}: fc port statistics dictionary for ports with increased counters.
        
        Returns:
            None.
        """

        if lr_type == 'lr_in':
            lr_delta_leaf = 'in-link-resets'
            ols_delta_leaf = 'out-offline-sequences'
            lr_substract_ols_leaf = BrocadeFCPortStatisticsParser.LRIN_SUBTRACT_OLSOUT_LEAF
            
        elif lr_type == 'lr_out':
            lr_delta_leaf = 'out-link-resets'
            ols_delta_leaf = 'in-offline-sequences'
            lr_substract_ols_leaf = BrocadeFCPortStatisticsParser.LROUT_SUBTRACT_OLSIN_LEAF

        lr_delta_leaf += BrocadeFCPortStatisticsParser.DELTA_TAG
        ols_delta_leaf += BrocadeFCPortStatisticsParser.DELTA_TAG
 
        # find diffrerence between link reset and offline sequence delta counters
        lr_substract_ols_delta = \
            BrocadeFCPortStatisticsParser.subtract_counters(fcport_stats_dct[lr_delta_leaf], fcport_stats_dct[ols_delta_leaf])
        
        self._add_error_status_and_categorize_error(fcport_stats_dct, lr_substract_ols_delta, counter_thresholds_key='lr_substract_ols', counter_name=lr_substract_ols_leaf, severity='medium')
        
        # save diffrerence to fc port statistics dictionaries
        fcport_stats_dct[lr_substract_ols_leaf] = lr_substract_ols_delta
        BrocadeFCPortStatisticsParser.save_positive_value(fcport_stats_growth_dct, lr_substract_ols_leaf, lr_substract_ols_delta) 



    @staticmethod
    def save_positive_value(delta_dct: dict, counter_name: str, delta_value: int) -> None:
        """
        Method adds delta value to the dictionary if delta is greater then 0.
        
        Args:
            delta_dct {dict}: dictionary with positive deltas.
            counter_name {str}: counter name.
            delta_value {int}: delta value to add.
        
        Returns:
            None.        
        """
        if delta_value and delta_value > 0:
            delta_dct[counter_name] = delta_value


    @staticmethod
    def subtract_counters(counter1: int, counter2: int) -> int:
        """
        Method calculates absolute difference between two counters.

        Args:
            counter1 {int}: port statistics counter.
            counter2 {int}: port statistics counter.
        
        Returns:
            int: module of two counters substraction.
        """
        
        if counter1 is not None and  counter2 is not None:
            return abs(counter1 - counter2)
                        

    def _add_empty_fields(self, fc_statistics_port_now_dct: dict) -> None:
        """
        Method adds empty fields from the BrocadeFCPortStatisticsParser list to the fcport statistics dictionary.

        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
        
        Returns:
            None.
        """

        empty_delta_dct = {counter + BrocadeFCPortStatisticsParser.DELTA_TAG: None for counter in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS}
        fc_statistics_port_now_dct.update(empty_delta_dct)
        # self._add_empty_port_error_status_fields(fc_statistics_port_now_dct)
        self._add_unknown_port_error_status_fields(fc_statistics_port_now_dct)
        self._add_empty_error_category_fields(fc_statistics_port_now_dct)
        fc_statistics_port_now_dct['time-generated-prev-hrf'] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LROUT_SUBTRACT_OLSIN_LEAF] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LRIN_SUBTRACT_OLSOUT_LEAF] = None
        

    # def _add_empty_port_error_status_fields(self, fc_statistics_port_now_dct: dict) -> None:

    #     unknown_port_error_status_dct = {port_error_severity: 'unknown' 
    #                                      for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS}
    #     unknown_port_error_status_id_dct = {port_error_severity + '-id': BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_ID['unknown'] 
    #                                         for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS}
        
    #     empty_error_categories_dct = {key: None for key in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS}
    #     fc_statistics_port_now_dct.update(unknown_port_error_status_dct)
    #     fc_statistics_port_now_dct.update(unknown_port_error_status_id_dct)
    #     fc_statistics_port_now_dct.update(empty_error_categories_dct)



    def _add_unknown_port_error_status_fields(self, fc_statistics_port_now_dct: dict) -> None:

        unknown_port_error_status_dct = {port_error_severity: 'unknown' 
                                         for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS 
                                         if not port_error_severity in fc_statistics_port_now_dct}
                                         
        unknown_port_error_status_id_dct = {port_error_severity + '-id': BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_ID['unknown'] 
                                            for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS
                                            if not port_error_severity in fc_statistics_port_now_dct}
        fc_statistics_port_now_dct.update(unknown_port_error_status_dct)
        fc_statistics_port_now_dct.update(unknown_port_error_status_id_dct)
        

    def _add_empty_error_category_fields(self, fc_statistics_port_now_dct: dict) -> None:


         empty_error_categories_dct = {error_category: None 
                                       for error_category in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS 
                                       if not error_category in fc_statistics_port_now_dct}
         fc_statistics_port_now_dct.update(empty_error_categories_dct)
        
        
    

    @staticmethod
    def epoch_to_datetime(seconds: int) -> datetime:
        """
        Method converts epoch to human-readable datetime.

        Args:
            seconds {int}: number of seconds that have elapsed since January 1, 1970 (midnight UTC/GMT).
        
        Returns:
            str: datetime in hrf format.
        """

        return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
    

    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser


    @property
    def fcport_stats(self):
        return self._fcport_stats
    

    @property
    def fcport_stats_growth(self):
        return self._fcport_stats_growth