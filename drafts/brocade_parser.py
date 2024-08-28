from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry

from brocade_telemetry_request_status import BrocadeRequestStatus
from brocade_chassis_parser import BrocadeChassisParser
from brocade_fru_parser import BrocadeFRUParser
from brocade_maps_parser import BrocadeMAPSParser
from brocade_switch_parser import BrocadeSwitchParser
from brocade_fcport_params_parser import BrocadeFCPortParametersParser
from brocade_sfp_media_parser import BrocadeSFPMediaParser
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser

from typing import Dict, List, Union


class BrocadeParser:
    """
    Class to create a parser. Parser is a set of dedicated parsers  
    for group if switch parameters.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        chname_ip_dct (Dict[str, str]): dictionary key as ip address and chassis name as value. 
        brocade_parser_prev (BrocadeParser): previous parser.
    """


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry, chname_ip_dct: Dict[str, str], 
                 brocade_parser_prev: 'BrocadeParser' = None) -> None:
        """  
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
            chname_ip_dct (Dict[str, str]): dictionary key as ip address and chassis name as value. 
            brocade_parser_prev (BrocadeParser): previous parser.
        """

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        self._chname_ip_dct: Dict[str, str] = chname_ip_dct
        self._brocade_parser_prev: 'BrocadeParser' = brocade_parser_prev

        # http request status parser
        self._request_status_parser = BrocadeRequestStatus(self.sw_telemetry, self.chname_ip_dct)
        # chassis parameters parser
        self._ch_parser = BrocadeChassisParser(self.sw_telemetry)
        # switch parameters parser
        self._sw_parser = BrocadeSwitchParser(self.sw_telemetry)
        
        if self._brocade_parser_prev is None:
            # fan, ps, sensor parser
            self._fru_parser = BrocadeFRUParser(self.sw_telemetry)
            # maps parser
            self._maps_parser = BrocadeMAPSParser(self.sw_telemetry, self.sw_parser)
            # fc port parameters parser
            self._fcport_params_parser = BrocadeFCPortParametersParser(self.sw_telemetry, self.sw_parser)
            # sfp media parser
            self._sfp_media_parser = BrocadeSFPMediaParser(self.sw_telemetry, self.fcport_params_parser)
            # fc port statistics parser
            self._fcport_stats_parser = BrocadeFCPortStatisticsParser(self.sw_telemetry, self.fcport_params_parser)
        else:
            # fan, ps, sensor parser
            self._fru_parser = BrocadeFRUParser(self.sw_telemetry, self.brocade_parser_prev.fru_parser)
            # maps parser
            self._maps_parser = BrocadeMAPSParser(self.sw_telemetry, self.sw_parser, 
                                                  self.brocade_parser_prev.maps_parser)
            # fc port parameters parser
            self._fcport_params_parser = BrocadeFCPortParametersParser(self.sw_telemetry, self.sw_parser, 
                                                                       self.brocade_parser_prev.fcport_params_parser)
            # sfp media parser
            self._sfp_media_parser = BrocadeSFPMediaParser(self.sw_telemetry, self.fcport_params_parser, 
                                                           self.brocade_parser_prev.sfp_media_parser)
            # fc port statistics parser
            self._fcport_stats_parser = BrocadeFCPortStatisticsParser(self.sw_telemetry, self.fcport_params_parser, 
                                                                      self.brocade_parser_prev.fcport_stats_parser)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def chname_ip_dct(self):
        return self._chname_ip_dct
    

    @property
    def brocade_parser_prev(self):
        return self._brocade_parser_prev
    
     
    @property
    def request_status_parser(self):
        return self._request_status_parser
    
    
    @property
    def ch_parser(self):
        return self._ch_parser
    
    
    @property
    def sw_parser(self):
        return self._sw_parser
    
    
    @property
    def fru_parser(self):
        return self._fru_parser
    
    
    @property
    def maps_parser(self):
        return self._maps_parser
    
    
    @property
    def fcport_params_parser(self):
        return self._fcport_params_parser
    
    
    @property
    def sfp_media_parser(self):
        return self._sfp_media_parser
    
    
    @property
    def fcport_stats_parser(self):
        return self._fcport_stats_parser