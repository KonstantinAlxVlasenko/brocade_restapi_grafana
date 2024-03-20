# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 17:08:32 2024

@author: kavlasenko
"""

import re
from typing import Dict, List, Tuple, Union, Optional
from quantiphy import Quantity
import numbers
import math


from datetime import datetime


from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from switch_telemetry_switch_parser_cls import BrocadeSwitchParser

class BrocadeFCPortStatisticsParser:
    """
    Class to create fc port parameters dictionaries.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        sw_parser: switch parameters retrieved from the sw_telemetry.
        port_owner: dictonary with port name as key and switchname to which port belongs to as value.
        fcport_params: fc port parameters dictionary ({vf_id:{slot_port_id:{param1: value1, param2: valuue2}}}).
    """

    FC_STATISTICS_PARAMS_LEAFS = ['name', 'sampling-interval', 'time-generated',
                                  'in-peak-rate', 'in-rate', 'out-peak-rate', 'out-rate']

    FC_STATISTICS_STATS_LEAFS = ['in-frames', 'out-frames', 'bb-credit-zero', 
                                 'frames-processing-required', 'in-lcs', 'class-3-frames']
    
    HIGH_SEVERITY_ERROR_LEAFS = ['class3-in-discards', 'class3-out-discards', 'class-3-discards', 
                                 'crc-errors', 'in-crc-errors', 'remote-crc-errors', 'remote-fec-uncorrected', 
                                 'pcs-block-errors',  'truncated-frames', 'bad-eofs-received', 
                                 'frames-too-long', 'frames-timed-out', 
                                 'invalid-transmission-words', 'remote-invalid-transmission-words']
    
    MEDIUM_SEVERITY_ERROR_LEAFS = ['address-errors', 'delimiter-errors', 'encoding-disparity-errors', 
                                   'frames-transmitter-unavailable-errors', 
                                   'multicast-timeouts', 'too-many-rdys', 
                                   'f-busy-frames', 'f-rjt-frames', 'p-busy-frames', 'p-rjt-frames', 
                                   'primitive-sequence-protocol-error',
                                   'remote-primitive-sequence-protocol-error']
    
    LOW_SEVERITY_ERROR_LEAFS = ['encoding-errors-outside-frame',  'invalid-ordered-sets']
    
    LINK_ERROR_LEAFS = ['loss-of-signal', 'loss-of-sync', 'link-failures', 
                        'in-link-resets', 'out-link-resets', 
                        'in-offline-sequences', 'out-offline-sequences',
                        'link-level-interrpts',
                        'remote-link-failures', 'remote-loss-of-signal', 'remote-loss-of-sync']
    
    FC_STATISTICS_COUNTER_LEAFS = (FC_STATISTICS_STATS_LEAFS + 
                                   HIGH_SEVERITY_ERROR_LEAFS + 
                                   MEDIUM_SEVERITY_ERROR_LEAFS + 
                                   LOW_SEVERITY_ERROR_LEAFS +
                                   LINK_ERROR_LEAFS)
    
    FC_STATISTICS_LEAFS = FC_STATISTICS_PARAMS_LEAFS + FC_STATISTICS_COUNTER_LEAFS
    
    
    # LR_OLS_DIFFERENCE = ['lrout-olsin-difference', 'lrin-olsout-difference']
    
    FC_PORT_PARAMS = ['swicth-name', 'port-name', 'physical-state', 
                      'port-enable-status', 'link-speed', 'port-type', 'speed']
    
    DELTA_TAG = '-delta'
    HRF_TAG = '-hrf'
    
    LROUT_SUBTRACT_OLSIN_LEAF = 'lrout' + DELTA_TAG + '_subtract_olsin' + DELTA_TAG
    LRIN_SUBTRACT_OLSOUT_LEAF = 'lrin' + DELTA_TAG + '_subtract_olsout' + DELTA_TAG
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, fcport_params_parser: BrocadeSwitchParser, fcport_stats_parser=None):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._ch_wwn = self._get_chassis_wwn()
        self._fcport_params_parser: BrocadeSwitchParser = fcport_params_parser
        self._fcport_stats = self._get_port_stats_values()
        if self.fcport_stats:
            self._calculate_counters_growth(fcport_stats_parser)
    


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



    def _get_port_stats_values(self) -> Dict[int, Dict[str, Dict[str, Optional[Union[str, int]]]]]:
        """
        Method retrieves each fc port parameters and status.
        
        Returns:
            dict: FC port parameters. Dictionary of dictionaries of dictionaries.
                External dictionary keys are vf_ids (if vf mode is disabled then vf-id is -1).
                First level nested dictionary keys are slot_port_numbers.
                Second level nested dictionary keys are fc port parameters names.
        """
        
        fcport_stats_dct = {}

        for vf_id, fc_statistics_telemetry in self.sw_telemetry.fc_statistics.items():
            if fc_statistics_telemetry.get('Response'):
                # list with fc_interface containers for the each port in the vf_id switch
                fc_statistics_container_lst = fc_statistics_telemetry['Response']['fibrechannel-statistics']
                fcport_stats_dct[vf_id] = {}
                
                for fc_statistics_container in fc_statistics_container_lst:

                    # get port statistics from the container
                    fcport_stats_current_dct = {leaf: fc_statistics_container.get(leaf) for leaf in BrocadeFCPortStatisticsParser.FC_STATISTICS_LEAFS}
                    # 
                    fcport_stats_current_hrf_dct = {leaf + BrocadeFCPortStatisticsParser.HRF_TAG: BrocadeFCPortStatisticsParser.int_to_hrf(fc_statistics_container.get(leaf)) for leaf in 
                                                    BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS}
                    

                    
                    fcport_stats_current_dct.update(fcport_stats_current_hrf_dct)


                    # slot_port_number in the format 'slot_number/port_number' (e.g. '0/1')
                    slot_port_number = fc_statistics_container['name']
                    # split slot and port number
                    slot_number, port_number = slot_port_number.split('/')
                    fcport_stats_current_dct['slot-number'] = int(slot_number)
                    fcport_stats_current_dct['port-number'] = int(port_number)

                    fcport_stats_current_dct['time-generated-hrf'] = BrocadeFCPortStatisticsParser.epoch_to_datetime(fc_statistics_container['time-generated'])

                    # fcport_stats_current_dct['lrout-olsin-difference'] = BrocadeFCPortStatisticsParser._subtract_counters(fcport_stats_current_dct['out-link-resets' + BrocadeFCPortStatisticsParser.DELTA_TAG], 
                    #                                                                                                                 fcport_stats_current_dct['in-offline-sequences' + BrocadeFCPortStatisticsParser.DELTA_TAG])
                    # fcport_stats_current_dct['lrin-olsout-difference'] = BrocadeFCPortStatisticsParser._subtract_counters(fcport_stats_current_dct['in-link-resets' + BrocadeFCPortStatisticsParser.DELTA_TAG], 
                    #                                                                                                         fcport_stats_current_dct['out-offline-sequences' + BrocadeFCPortStatisticsParser.DELTA_TAG])

                    # add port parameters to the sfp media dictionary
                    fcport_params_dct = self._get_port_params(vf_id, slot_port_number)
                    fcport_stats_current_dct.update(fcport_params_dct)


                    # add current port status dictionary to the summary port status dictionary with vf_id and slot_port as consecutive keys
                    fcport_stats_dct[vf_id][fc_statistics_container['name']] = fcport_stats_current_dct
        return fcport_stats_dct
    

    def _get_chassis_wwn(self) -> str:
        """
        Method extracts chassis parameters from the chassis module.
        
        Returns:
            Chassis parameters dictionary.
            Dictionary keys are CHASSIS_LEAFS. 
        """
        
        if self.sw_telemetry.chassis.get('Response'):
            return self.sw_telemetry.chassis['Response']['chassis']['chassis-wwn']



    @staticmethod
    def _subtract_counters(counter1: int, counter2: int) -> int:
        """
        Method calculates difference between LR and OLS states.
        
        Returns:
            Difference between LR and OLS ports.
        """
        
        if counter1 is not None and  counter2 is not None:
            return abs(counter1 - counter2)
                

    @staticmethod
    def int_to_hrf(counter: int, precision: int = 1) -> str:
        if isinstance(counter, numbers.Number):
            if counter:
                exponent = int(math.floor(math.log10(abs(counter))/3.0)*3)
                if counter / 10**exponent >= 10:
                    precision += 1
            return Quantity(counter).render(prec=precision).lower()



    def _calculate_counters_growth(self, other):

        if other is None or str(type(self)) != str(type(other)) or not other.fcport_stats:
            # print('other is None')

            for fcport_stats_vfid_now_dct in self.fcport_stats.values():

                for fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.values():
                    BrocadeFCPortStatisticsParser._add_empty_fields(fc_statistics_port_now_dct)
        
        elif self.ch_wwn == other.ch_wwn:
            # print(self.ch_wwn,  other.ch_wwn)
            # print('CHASSIS WWN is the same')
            for vf_id, fcport_stats_vfid_now_dct in self.fcport_stats.items():
                if vf_id not in other.fcport_stats:
                    for fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.values():
                        BrocadeFCPortStatisticsParser._add_empty_fields(fc_statistics_port_now_dct)
                    continue
                    
                
                fcport_stats_vfid_prev_dct = other.fcport_stats[vf_id]
                for slot_port, fc_statistics_port_now_dct in fcport_stats_vfid_now_dct.items():
                    if slot_port not in fcport_stats_vfid_prev_dct:
                        BrocadeFCPortStatisticsParser._add_empty_fields(fc_statistics_port_now_dct)
                        continue
                    
                    fc_statistics_port_prev_dct = fcport_stats_vfid_prev_dct[slot_port]
                    for counter in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS:
                        counter_delta = counter + BrocadeFCPortStatisticsParser.DELTA_TAG
                        if fc_statistics_port_prev_dct[counter] is None or fc_statistics_port_now_dct[counter] is None:
                            fc_statistics_port_now_dct[counter_delta] = None
                        else:
                            fc_statistics_port_now_dct[counter_delta] = fc_statistics_port_now_dct[counter] - fc_statistics_port_prev_dct[counter]
                    
                    fc_statistics_port_now_dct['time-generated-prev-hrf'] = fc_statistics_port_prev_dct['time-generated-hrf']
                            
                
                    
                    fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LROUT_SUBTRACT_OLSIN_LEAF] = \
                        BrocadeFCPortStatisticsParser._subtract_counters(fc_statistics_port_now_dct['out-link-resets' + BrocadeFCPortStatisticsParser.DELTA_TAG], 
                                                                         fc_statistics_port_now_dct['in-offline-sequences' + BrocadeFCPortStatisticsParser.DELTA_TAG])
                    
                    
                    fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LRIN_SUBTRACT_OLSOUT_LEAF] = \
                        BrocadeFCPortStatisticsParser._subtract_counters(fc_statistics_port_now_dct['in-link-resets' + BrocadeFCPortStatisticsParser.DELTA_TAG], 
                                                                         fc_statistics_port_now_dct['out-offline-sequences' + BrocadeFCPortStatisticsParser.DELTA_TAG])
                        
                        
    
    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"



    @staticmethod
    def _add_empty_fields(fc_statistics_port_now_dct) -> None:

        empty_delta_dct = {counter + BrocadeFCPortStatisticsParser.DELTA_TAG: None for counter in BrocadeFCPortStatisticsParser.FC_STATISTICS_COUNTER_LEAFS}
        fc_statistics_port_now_dct.update(empty_delta_dct)
        fc_statistics_port_now_dct['time-generated-prev-hrf'] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LROUT_SUBTRACT_OLSIN_LEAF] = None
        fc_statistics_port_now_dct[BrocadeFCPortStatisticsParser.LRIN_SUBTRACT_OLSOUT_LEAF] = None
        


    @staticmethod
    def epoch_to_datetime(seconds: int) -> datetime:
        return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser
    

    @property
    def fcport_stats(self):
        return self._fcport_stats


    @property
    def ch_wwn(self):
        return self._ch_wwn