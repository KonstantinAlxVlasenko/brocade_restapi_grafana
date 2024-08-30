from parser import (ChassisParser, FCPortParametersParser,
                    FCPortStatisticsParser, FRUParser, MAPSParser,
                    RequestStatusParser, SFPMediaParser, SwitchParser)
from typing import Dict, List, Self, Union

from switch_telemetry_request import SwitchTelemetryRequest


class BrocadeParser:
    """
    Class to create a parser. Parser is a set of dedicated parsers  
    for group if switch parameters.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
        nameserver_dct (Dict[str, str]): dictionary key as ip address and chassis name as value. 
        brocade_parser_prev (BrocadeParser): previous parser.
    """


    def __init__(self, sw_telemetry: SwitchTelemetryRequest, nameserver_dct: Dict[str, str], 
                 brocade_parser_prev: Self = None) -> None:
        """  
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
            nameserver_dct (Dict[str, str]): dictionary key as ip address and chassis name as value. 
            brocade_parser_prev (BrocadeParser): previous parser.
        """

        self._sw_telemetry: SwitchTelemetryRequest = sw_telemetry
        self._nameserver: Dict[str, str] = nameserver_dct
        self._brocade_parser_prev: 'BrocadeParser' = brocade_parser_prev

        # http request status parser
        self._request_status_parser = RequestStatusParser(self.sw_telemetry, self.nameserver)
        # chassis parameters parser
        self._ch_parser = ChassisParser(self.sw_telemetry)
        # switch parameters parser
        self._sw_parser = SwitchParser(self.sw_telemetry)
        
        if self._brocade_parser_prev is None:
            # fan, ps, sensor parser
            self._fru_parser = FRUParser(self.sw_telemetry)
            # maps parser
            self._maps_parser = MAPSParser(self.sw_telemetry, self.sw_parser)
            # fc port parameters parser
            self._fcport_params_parser = FCPortParametersParser(self.sw_telemetry, self.sw_parser)
            # sfp media parser
            self._sfp_media_parser = SFPMediaParser(self.sw_telemetry, self.fcport_params_parser)
            # fc port statistics parser
            self._fcport_stats_parser = FCPortStatisticsParser(self.sw_telemetry, self.fcport_params_parser)
        else:
            # fan, ps, sensor parser
            self._fru_parser = FRUParser(self.sw_telemetry, self.brocade_parser_prev.fru_parser)
            # maps parser
            self._maps_parser = MAPSParser(self.sw_telemetry, self.sw_parser, 
                                                  self.brocade_parser_prev.maps_parser)
            # fc port parameters parser
            self._fcport_params_parser = FCPortParametersParser(self.sw_telemetry, self.sw_parser, 
                                                                       self.brocade_parser_prev.fcport_params_parser)
            # sfp media parser
            self._sfp_media_parser = SFPMediaParser(self.sw_telemetry, self.fcport_params_parser, 
                                                           self.brocade_parser_prev.sfp_media_parser)
            # fc port statistics parser
            self._fcport_stats_parser = FCPortStatisticsParser(self.sw_telemetry, self.fcport_params_parser, 
                                                                      self.brocade_parser_prev.fcport_stats_parser)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property
    def nameserver(self):
        return self._nameserver
    

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