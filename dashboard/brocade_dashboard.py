from parser import (ChassisParser, FCPortParametersParser,
                    FCPortStatisticsParser, FRUParser, MAPSParser,
                    RequestStatusParser, SFPMediaParser, SwitchParser)

from dashboard import (ChassisToolbar, FabricShowToolbar, FCPortParamsToolbar,
                       FCPortStatsToolbar, FRUToolbar, LogToolbar,
                       MAPSDashboardToolbar, MAPSSystemToolbar,
                       RequestStatusToolbar, SFPMediaToolbar, SwitchToolbar)
from switch_telemetry_request import SwitchTelemetryRequest


class BrocadeDashboard:
    """
    Class to create a dashboard. Dashboard is a set of toolbars 
    which in turn are a set of prometheus gauges groups for Brocade switch.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """


    def __init__(self, sw_telemetry: SwitchTelemetryRequest) -> None:
        """  
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        self._sw_telemetry: SwitchTelemetryRequest = sw_telemetry

        self._request_status_tb = RequestStatusToolbar(self.sw_telemetry)
        self._chassis_tb = ChassisToolbar(self.sw_telemetry)
        self._fru_tb = FRUToolbar(self.sw_telemetry)
        self._maps_system_tb = MAPSSystemToolbar(self.sw_telemetry)
        self._maps_dashboard_tb = MAPSDashboardToolbar(self.sw_telemetry)
        self._switch_tb = SwitchToolbar(self.sw_telemetry)
        self._fabricshow_tb = FabricShowToolbar(self.sw_telemetry)
        self._fcport_params_tb = FCPortParamsToolbar(self.sw_telemetry)
        self._sfp_media_tb = SFPMediaToolbar(self.sw_telemetry)
        self._fcport_stats_tb = FCPortStatsToolbar(self.sw_telemetry)
        self._log_tb = LogToolbar(self.sw_telemetry)


    def fill_dashboard_gauge_metrics(self, 
                                    request_status_parser: RequestStatusParser,
                                    ch_parser: ChassisParser,
                                    fru_parser: FRUParser,
                                    maps_parser: MAPSParser,
                                    sw_parser: SwitchParser,
                                    fcport_params_parser: FCPortParametersParser,
                                    sfp_media_parser: SFPMediaParser,
                                    fcport_stats_parser: FCPortStatisticsParser) -> None:
        

        print('request_status')
        self.request_status_tb.fill_toolbar_gauge_metrics(request_status_parser)
        
        # print('chassis')
        # self.chassis_tb.fill_toolbar_gauge_metrics(ch_parser, sw_parser)

        # print('fru')
        # self.fru_tb.fill_toolbar_gauge_metrics(fru_parser, sw_parser)

        # print('maps system resources', 'maps system health')
        # self.maps_system_tb.fill_toolbar_gauge_metrics(maps_parser, sw_parser)

        # print('maps policy, actions','maps dashboard')
        # self.maps_dashboard_tb.fill_toolbar_gauge_metrics(maps_parser)

        # print('switch')
        # self.switch_tb.fill_toolbar_gauge_metrics(sw_parser)
        
        # print('fabrichsow')
        # self.fabricshow_tb.fill_toolbar_gauge_metrics(sw_parser)

        # print('fcport parameters')
        # self.fcport_params_tb.fill_toolbar_gauge_metrics(fcport_params_parser)

        # print('sfp media')
        # self.sfp_media_tb.fill_toolbar_gauge_metrics(sfp_media_parser)

        # print('fcport_stats')
        # self.fcport_stats_tb.fill_toolbar_gauge_metrics(fcport_stats_parser)

        # print('log')
        # self.log_tb.fill_toolbar_gauge_metrics(sw_parser, fcport_params_parser, sfp_media_parser, 
        #                                   fcport_stats_parser, fru_parser, maps_parser)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry
    
    
    @property    
    def request_status_tb(self):
        return self._request_status_tb


    @property    
    def chassis_tb(self):
        return self._chassis_tb


    @property
    def fru_tb(self):
        return self._fru_tb


    @property
    def maps_system_tb(self):
        return self._maps_system_tb


    @property
    def maps_dashboard_tb(self):
        return self._maps_dashboard_tb


    @property
    def switch_tb(self):
        return self._switch_tb


    @property
    def fabricshow_tb(self):
        return self._fabricshow_tb


    @property
    def fcport_params_tb(self):
        return self._fcport_params_tb


    @property
    def sfp_media_tb(self):
        return self._sfp_media_tb


    @property
    def fcport_stats_tb(self):
        return self._fcport_stats_tb


    @property
    def log_tb(self):
        return self._log_tb