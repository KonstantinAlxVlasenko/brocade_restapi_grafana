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

from brocade_base_parser import BrocadeTelemetryParser
from quantiphy import Quantity
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser


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
                                  'frames-too-long', 'frames-timed-out']
    
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
    
    # FC_PORT_PARAMS = ['swicth-name', 'port-name', 'physical-state', 
    #                   'port-enable-status', 'port-speed-hrf', 'port-type', 'speed']
    
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
    
    PORT_ERROR_STATUS_TAG = '-severity-errors_port-status'

    ERROR_SEVERITY_TYPES = ['high','medium', 'low']

    PORT_ERROR_STATUS_KEYS = [severity + '-severity-errors_port-status' for severity in ERROR_SEVERITY_TYPES]

    COUNTER_CATEGORY_KEYS = [severity + '-severity_' + counter_status + '-status_errors' 
                             for severity in ERROR_SEVERITY_TYPES for counter_status in ['critical', 'warning', 'ok']]
    
    COUNTER_CATEGORY_DELTA_KEYS = [category + '-delta' for category in COUNTER_CATEGORY_KEYS]
    
    # STATUS_IDS = {'ok': 1, 'unknown': 2, 'warning': 3, 'critical': 4}

    # IO_RATE_KEYS = [rate_key + tag for rate_key in ['in-rate', 'out-rate'] for tag in ['-bits', '-percentage', '-status']]
    # IO_RATE_KEYS = [rate_key + tag for rate_key in ['in-rate', 'out-rate'] for tag in ['-status']]
    
    IO_RATE_KEYS = [rate_key + tag for rate_key in ['in-rate', 'out-rate'] for tag in ['-bits', '-percentage']]
    IO_RATE_STATUS_KEYS = [rate_key + tag for rate_key in ['in-rate', 'out-rate'] for tag in ['-status']]

    FC_PORT_STATS_CHANGED = PORT_ERROR_STATUS_KEYS + COUNTER_CATEGORY_KEYS + COUNTER_CATEGORY_DELTA_KEYS + IO_RATE_KEYS + IO_RATE_STATUS_KEYS

    # FC_PORT_PATH = ['fabric-user-friendly-name', 'vf-id', 'switch-name', 'switch-wwn', 'port-name', 'name', 'slot-number', 'port-number']


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
            self._fcport_stats_changed = self._get_changed_fcport_stats(fcport_stats_prev)
        else:
            self._fcport_stats_growth = {}
            self._fcport_stats_changed = {}
    

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
                    # convert io rates to bits and check if throuput threshold is exceeded
                    self._add_io_troughput_status(fcport_stats_current_dct)
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
        fcport_params = {param: fc_port_params_current.get(param) for param in BrocadeFCPortStatisticsParser.FC_PORT_ADD_PARAMS}
        return fcport_params


    def _add_io_troughput_status(self, fcport_stats_current_dct) -> None:
        """
        Method to add io troughput status to the fc port statistics dictionary.
        
        Args:
            fcport_stats_current_dct {dict}: fc statistics dictionary for the current slot_port.
        
        Returns:
            None.
        """

        for rate_key in ['in-peak-rate', 'in-rate', 'out-peak-rate', 'out-rate']:
            # rate_bits_key = rate_key + '-bits'
            rate_mbytes_key = rate_key + '-Mbytes'
            rate_percantage_key = rate_key + '-percentage'
            # # convert rate bytes to bits
            # fcport_stats_current_dct[rate_bits_key] = BrocadeFCPortStatisticsParser.bytes_to_bits(fcport_stats_current_dct[rate_key])
            # convert rate bytes to mbytes
            fcport_stats_current_dct[rate_mbytes_key] = BrocadeFCPortStatisticsParser.bytes_to_mbytes(fcport_stats_current_dct[rate_key])
            # find throughput percentage from the port throughput
            fcport_stats_current_dct[rate_percantage_key] = BrocadeFCPortStatisticsParser.get_percentage(
                fcport_stats_current_dct[rate_mbytes_key], fcport_stats_current_dct['port-throughput-Mbytes'])
            if not 'peak' in rate_key:
                rate_status_key = rate_key + '-status'
                rate_status_id_key = rate_status_key + '-id'
                # find if throuput threshold is exceeded and get corresponding status id
                fcport_stats_current_dct[rate_status_id_key] = BrocadeFCPortStatisticsParser.get_rate_status(
                    fcport_stats_current_dct[rate_percantage_key])
                # corresponding status
                fcport_stats_current_dct[rate_status_key] = BrocadeFCPortStatisticsParser.STATUS_ID[fcport_stats_current_dct[rate_status_id_key]]
            
            # if not 'peak' in  rate_key:
            #     print(fcport_stats_current_dct['port-number'], fcport_stats_current_dct['physical-state'], rate_key + '-%', fcport_stats_current_dct[rate_bits_key], fcport_stats_current_dct['speed'], fcport_stats_current_dct[rate_key + '-%'])


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
                    force_ok_status = True if other is None else False
                    self._add_empty_fields(fc_statistics_port_now_dct, force_ok_status=force_ok_status)
        
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
                    # add 'unknown' port error status for high, medium and low severity counters if it doesn't exist 
                    self._add_unknown_port_error_status_fields(fc_statistics_port_now_dct)
                    # add None for list of errors for all severities and critical, warning and ok statuses if doesn't exist 
                    self._add_empty_error_category_fields(fc_statistics_port_now_dct)
                    # if stat counters (transmitted and received frames etc, see FC_STATISTICS_STAT_LEAFS) 
                    # increased only then drop stats dictionary coz error counters are not increasing
                    # otherwise add increased port counters stats to the fcport_stats_growth_dct
                    self._update_fcport_stats_growth(fcport_stats_growth_dct, fcport_stats_growth_port_dct, fc_statistics_port_now_dct, vf_id, slot_port)
        return fcport_stats_growth_dct    


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
                # add counter name to the corresponding category list depending from counter severity and counter status and assign port error status
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
        Method assingns port error status and categorizes error (adds counter title to the corresponding list).
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            counter_name {str}: name of the counter.
            counter_status {str}: status of the counter.
            severity {str}: severity of the error.
        """
                
        counter_status_id = BrocadeFCPortStatisticsParser.get_error_status(counter_delta, BrocadeFCPortStatisticsParser.COUNTER_THRESHOLDS[counter_thresholds_key])
        # update port error status if counter_status is greater than the port error status
        self._update_port_error_status(fc_statistics_port_now_dct, counter_status_id, severity)
        # add counter title to the corresponding list depending from counter severity and counter status.
        self._categorize_error(fc_statistics_port_now_dct, counter_name, counter_status_id, severity)
                

    def _update_port_error_status(self, fc_statistics_port_now_dct: dict,  counter_status_id, severity: str) -> None:
        """
        Method updates port error status ('critical', 'warning', 'ok') for the current severity level ('high','medium', 'low').
        If existing port error status has greater port error status id than the current port error status is not updated.
        So worse error status is assigned to the port error status.

        Port error status types:
            'high-severity-errors_port-status',
            'medium-severity-errors_port-status',
            'low-severity-errors_port-status']
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            counter_status {str}: status of the counter threshold ('critical', 'warning', 'ok').
            severity {str}: error severity ('high','medium', 'low').
        
        Returns:
            None
        """

        # port error status type title
        counter_status_key = severity + BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_TAG
        # port error status type id title
        counter_status_id_key = severity + BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_TAG + '-id'
        # get id of the current error status
        # counter_status_id = BrocadeFCPortStatisticsParser.STATUS_VALUE[counter_status]
        counter_status = BrocadeFCPortStatisticsParser.STATUS_ID[counter_status_id]
        # if port error status is assigned
        if fc_statistics_port_now_dct.get(counter_status_id_key):
            # check if current error status id is greater than the port error status id
            if counter_status_id > fc_statistics_port_now_dct[counter_status_id_key]:
                fc_statistics_port_now_dct[counter_status_key] = counter_status
                fc_statistics_port_now_dct[counter_status_id_key] = counter_status_id
        # if port error status is not exist assign it as current error status
        else:
            fc_statistics_port_now_dct[counter_status_key] = counter_status
            fc_statistics_port_now_dct[counter_status_id_key] = counter_status_id


    def _categorize_error(self, fc_statistics_port_now_dct, counter_name, counter_status_id: int, severity: str) -> None:
        """
        Method adds counter title to the corresponding list depending on the error status ('critical', 'warning', 'ok')
        and severity ('high','medium', 'low').

        Counter categories:
            'high-severity_critical-status_error',
            'high-severity_warning-status_error',
            'high-severity_ok-status_error',
            'medium-severity_critical-status_error',
            'medium-severity_warning-status_error',
            'medium-severity_ok-status_error',
            'low-severity_critical-status_error',
            'low-severity_warning-status_error',
            'low-severity_ok-status_error'
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            counter_name {str}: name of the counter (error title).
            counter_status {str}: status of the counter threshold ('critical', 'warning', 'ok').
            severity {str}: error severity ('high','medium', 'low').
        
        Returns:
            None
        """
                
        # if counter_status == 'ok':
        #     return

        if counter_status_id == 2: # 'unknown'
            return
        
        # category name for the current counter
        counter_category = severity + '-severity_' + BrocadeFCPortStatisticsParser.STATUS_ID[counter_status_id].lower() + '-status_errors'

        counter_delta_name = counter_name if BrocadeFCPortStatisticsParser.DELTA_TAG in counter_name else counter_name + BrocadeFCPortStatisticsParser.DELTA_TAG
        if counter_category in fc_statistics_port_now_dct:
            fc_statistics_port_now_dct[counter_category].append(counter_name)
            fc_statistics_port_now_dct[counter_category + BrocadeFCPortStatisticsParser.DELTA_TAG].update(
                {counter_name: fc_statistics_port_now_dct[counter_delta_name]})
        else:
            fc_statistics_port_now_dct[counter_category] = [counter_name]
            fc_statistics_port_now_dct[counter_category + BrocadeFCPortStatisticsParser.DELTA_TAG] ={
                counter_name: fc_statistics_port_now_dct[counter_delta_name]}

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
        # save diffrerence to fc port statistics dictionaries
        fcport_stats_dct[lr_substract_ols_leaf] = lr_substract_ols_delta 
        # add counter name to the corresponding category list depending from counter severity and counter status and assign port error status
        self._add_error_status_and_categorize_error(fcport_stats_dct, lr_substract_ols_delta, counter_thresholds_key='lr_substract_ols', 
                                                    counter_name=lr_substract_ols_leaf, severity='medium')
        BrocadeFCPortStatisticsParser.save_positive_value(fcport_stats_growth_dct, lr_substract_ols_leaf, lr_substract_ols_delta) 


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
                                   

    def _add_empty_fields(self, fc_statistics_port_now_dct: dict, force_ok_status: bool = False) -> None:
        """
        Method adds empty fields from the BrocadeFCPortStatisticsParser list,
        empty port error status fields and empty error category fields to the fcport statistics dictionary.

        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            force_ok_status {bool}: forces to fill empty error status with 'ok' instead 'unknown'.
        
        Returns:
            None.
        """

        empty_delta_dct = {counter + BrocadeFCPortStatisticsParser.DELTA_TAG: None for counter in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS}
        fc_statistics_port_now_dct.update(empty_delta_dct)
        self._add_unknown_port_error_status_fields(fc_statistics_port_now_dct, force_ok_status)
        self._add_empty_error_category_fields(fc_statistics_port_now_dct)
        fc_statistics_port_now_dct['time-generated-prev-hrf'] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LROUT_SUBTRACT_OLSIN_LEAF] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LRIN_SUBTRACT_OLSOUT_LEAF] = None
        

    def _add_unknown_port_error_status_fields(self, fc_statistics_port_now_dct: dict, force_ok_status: bool = False) -> None:
        """
        Method adds port error status fields to the fcport statistics dictionary 
        with 'unknown' value if this port error status doesn't exist or 'ok' value if it's forced.

        Port error status types:
            'high-severity-errors_port-status',
            'medium-severity-errors_port-status',
            'low-severity-errors_port-status'
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
            force_ok_status {bool}: forces to fill empty error status with 'ok' instead 'unknown'. 
        
        Returns:
            None.
        """
        
        status_id = 1 if force_ok_status else 2

        # non-exisnet port error status id                                 
        unknown_port_error_status_id_dct = {port_error_severity + '-id': status_id 
                                            for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS
                                            if not port_error_severity in fc_statistics_port_now_dct}
        # non-exisnet port error status
        unknown_port_error_status_dct = {port_error_severity: BrocadeFCPortStatisticsParser.STATUS_ID[status_id] 
                                         for  port_error_severity in BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS 
                                         if not port_error_severity in fc_statistics_port_now_dct}        
        
        
        fc_statistics_port_now_dct.update(unknown_port_error_status_dct)
        fc_statistics_port_now_dct.update(unknown_port_error_status_id_dct)
        

    def _add_empty_error_category_fields(self, fc_statistics_port_now_dct: dict) -> None:
        """
        Method adds error categories with None value if it doesn't exist in fc_statistics_port_now_dct.

        Counter categories:
            'high-severity_critical-status_error',
            'high-severity_warning-status_error',
            'high-severity_ok-status_error',
            'medium-severity_critical-status_error',
            'medium-severity_warning-status_error',
            'medium-severity_ok-status_error',
            'low-severity_critical-status_error',
            'low-severity_warning-status_error',
            'low-severity_ok-status_error'
        
        Args:
            fc_statistics_port_now_dct {dict}: current fc port statistics dictionary.
        
        Returns:
            None
        """

        # create empty categories fields
        empty_error_categories_dct = {error_category: None 
                                       for error_category in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS 
                                       if not error_category in fc_statistics_port_now_dct}
        empty_error_categories_w_values_dct = {error_category + BrocadeFCPortStatisticsParser.DELTA_TAG: None 
                                       for error_category in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS 
                                       if not error_category + BrocadeFCPortStatisticsParser.DELTA_TAG in fc_statistics_port_now_dct}
        # add empty fields to the fc port statistics dictionary
        fc_statistics_port_now_dct.update(empty_error_categories_dct)
        fc_statistics_port_now_dct.update(empty_error_categories_w_values_dct)
        

    def _get_changed_fcport_stats(self, other) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method detects if error port status, error categories members, io thresholds from the FC_PORT_STATS_CHANGED list have been changed for each switch port.
        It compares port parameters of two instances of BrocadeFCPortStatisticsParser class.
        All changed parameters are added to to the dictionatry including current and previous values.
        
        Args:
            other {BrocadeFCPortStatisticsParser}: fc port statistics class instance retrieved from the previous sw_telemetry.
        
        Returns:
            dict: FC ports statistics change dictionary. Any port with changed parameters are in this dictionary.
        """

        # switch ports with changed parameters
        fcport_stats_changed_dct = {}

        # other is not exist (for examle 1st iteration)
        # other is not BrocadeFCPortParametersParser type
        # other's fcport_params atrribute is empty
        if other is None or str(type(self)) != str(type(other)) or not other.fcport_stats:
            return None
        
        # check if other is for the same switch
        elif self.same_chassis(other):
            for vf_id, fcport_stats_vfid_now_dct in self.fcport_stats.items():

                fcport_stats_changed_dct[vf_id] = {}

                # if there is no vf_id in other check next vf_id 
                if vf_id not in other.fcport_stats:
                    continue

                # fc port statistics of the vf_id switch of the previous telemetry    
                fcport_params_vfid_prev_dct = other.fcport_stats[vf_id]
                # timestamps
                time_now = self.telemetry_date + ' ' + self.telemetry_time
                time_prev = other.telemetry_date + ' ' + other.telemetry_time
                # add changed fcport stats ports for the current vf_id
                fcport_stats_changed_dct[vf_id] = BrocadeFCPortStatisticsParser.get_changed_vfid_ports(fcport_stats_vfid_now_dct, fcport_params_vfid_prev_dct, 
                                                                                        changed_keys=BrocadeFCPortStatisticsParser.FC_PORT_STATS_CHANGED, 
                                                                                        const_keys=BrocadeFCPortStatisticsParser.FC_PORT_PATH, 
                                                                                        time_now=time_now, time_prev=time_prev)
        return fcport_stats_changed_dct


    @staticmethod
    def get_error_status(value: float, status_intervals_dct: dict) -> str:
        """
        Method checks to which interval value belongs to and returns corresponding status.
        'unknown--------0--------warning--------critical--------'
        
        Args:
            value {float}: value checked to which interval it belongs to.
            status_intervals_dct {dict}: dictionary with intervals {'warning': x, 'critical': y}
        
        Returns:
            int: 1: 'ok', 2: 'unknown', 3: 'warning', 4: 'critical'
        """

        # status = 'unknown'

        status = 2 # 'unknown'
        if value < 0:
            return status

        if value >= 0 and value < status_intervals_dct['warning']:
            status = 1 # 'ok'
        elif value >= status_intervals_dct['warning'] and value < status_intervals_dct['critical']:
            status = 3 # 'warning'                  
        elif value >= status_intervals_dct['critical']:
            status = 4 # 'critical'
        return status


    @staticmethod
    def get_rate_status(rate_percantage: float) -> str:
        """
        Method to get port in and out rate status. Port throughput status.
        
        Args:
            rate_percantage {float}: in and out throughput percentage from the port speed.
        
        Returns:
            int: Port in and out throughput status (1: 'ok', 2: 'unknown', 3: 'warning', 4: 'critical',).
            
        """

        if rate_percantage is None:
            return 2 #'unknown'
        
        if rate_percantage >= 90:
            return 4 #'critical'
        elif rate_percantage >= 75:
            return 3 #'warning'
        else:
            return 1 #'ok'


    @staticmethod
    def get_percentage(part: int, whole: int) -> float:
        """
        Method to get percantage from the whole value.
        
        Args:
            part {int}: part value to calculate percentage.
            whole {int}: whole value to calculate percentage from.
        
        Returns:
            float: percenatage of part from the whole.
        """
        if part is not None and whole is not None:
            return round(100 * part/whole, 2)


    @staticmethod
    def bytes_to_bits(bytes: int) -> int:
        """
        Method converts bytes to bits. 1 byte = = 8 bits.
        
        Args:
            bytes {int}: nember of bytes.
        
        Returns:
            int: bits.
        """
        
        if bytes is not None:
            return 8 * bytes


    @staticmethod
    def bytes_to_mbytes(bytes: int) -> int:
        """
        Method converts bytes to Mega bytes. 1 Mbyte = 1024*1024*bytes.
        
        Args:
            bytes {int}: nember of bytes.
        
        Returns:
            int: Mbytes.
        """
        
        if bytes is not None:
            return round(bytes/1024/1024, 2)


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
    

    @property
    def fcport_stats_changed(self):
        return self._fcport_stats_changed


    # @staticmethod
    # def _save_positive_counter_delta(delta_dct, slot_port, counter_name, delta_value):
    #     if delta_value and delta_value > 0:
    #         if not slot_port in delta_dct:
    #             delta_dct[slot_port] = {counter_name: delta_value}
    #         else:
    #             delta_dct[slot_port].update({counter_name: delta_value})    