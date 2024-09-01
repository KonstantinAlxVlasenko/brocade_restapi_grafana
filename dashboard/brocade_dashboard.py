from parser.brocade_parser import BrocadeParser

from .chassis_toolbar import ChassisToolbar
from .fabricshow_toolbar import FabricShowToolbar
from .fcport_params_toolbar import FCPortParamsToolbar
from .fcport_stats_toolbar import FCPortStatsToolbar
from .fru_toolbar import FRUToolbar
from .log_toolbar import LogToolbar
from .maps_dashboard_toolbar import MAPSDashboardToolbar
from .maps_system_toolbar import MAPSSystemToolbar
from .request_status_toolbar import RequestStatusToolbar
from .sfp_media_toolbar import SFPMediaToolbar
from .switch_toolbar import SwitchToolbar


from collection.switch_telemetry_request import SwitchTelemetryRequest


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


    def fill_dashboard_gauge_metrics(self, brocade_parser: BrocadeParser) -> None:
        """Method to fill the gauge metrics for the dashboard.

        Args:
            brocade_parser (BrocadeParser): object contains required data to fill the gauge metrics.
        """
        

        # print('request_status')
        # self.request_status_tb.fill_toolbar_gauge_metrics(brocade_parser.request_status_parser)
        
        # print('chassis')
        # self.chassis_tb.fill_toolbar_gauge_metrics(brocade_parser.ch_parser, brocade_parser.sw_parser)

        # print('fru')
        # self.fru_tb.fill_toolbar_gauge_metrics(brocade_parser.fru_parser, brocade_parser.sw_parser)

        # print('maps system resources', 'maps system health')
        # self.maps_system_tb.fill_toolbar_gauge_metrics(brocade_parser.maps_parser, brocade_parser.sw_parser)

        # print('maps policy, actions','maps dashboard')
        # self.maps_dashboard_tb.fill_toolbar_gauge_metrics(brocade_parser.maps_parser)

        # print('switch')
        # self.switch_tb.fill_toolbar_gauge_metrics(brocade_parser.sw_parser)
        
        # print('fabrichsow')
        # self.fabricshow_tb.fill_toolbar_gauge_metrics(brocade_parser.sw_parser)

        # print('fcport parameters')
        # self.fcport_params_tb.fill_toolbar_gauge_metrics(brocade_parser.fcport_params_parser)

        # print('sfp media')
        # self.sfp_media_tb.fill_toolbar_gauge_metrics(brocade_parser.sfp_media_parser)

        print('fcport_stats')
        self.fcport_stats_tb.fill_toolbar_gauge_metrics(brocade_parser.fcport_stats_parser)

        # print('log')
        # self.log_tb.fill_toolbar_gauge_metrics(brocade_parser.sw_parser, brocade_parser.fcport_params_parser, brocade_parser.sfp_media_parser, 
        #                                   brocade_parser.fcport_stats_parser, brocade_parser.fru_parser, brocade_parser.maps_parser)


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