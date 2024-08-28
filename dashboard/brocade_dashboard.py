from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_request_status_toolbar import BrocadeRequestStatusToolbar
from brocade_chassis_toolbar import BrocadeChassisToolbar
from brocade_fru_toolbar import BrocadeFRUToolbar
from brocade_maps_system_toolbar import BrocadeMAPSSystemToolbar
from brocade_maps_dashboard_toolbar import BrocadeMAPSDashboardToolbar
from brocade_switch_toolbar import BrocadeSwitchToolbar
from brocade_fabricshow_toolbar import BrocadeFabricShowToolbar
from brocade_fcport_params_toolbar import BrocadeFCPortParamsToolbar
from brocade_sfp_media_toolbar import BrocadeSFPMediaToolbar
from brocade_fcport_stats_toolbar import BrocadeFCPortStatsToolbar
from brocade_log_toolbar import BrocadeLogToolbar

from brocade_telemetry_request_status import BrocadeRequestStatus
from brocade_chassis_parser import BrocadeChassisParser
from brocade_fru_parser import BrocadeFRUParser
from brocade_maps_parser import BrocadeMAPSParser
from brocade_switch_parser import BrocadeSwitchParser
from brocade_fcport_params_parser import BrocadeFCPortParametersParser
from brocade_sfp_media_parser import BrocadeSFPMediaParser
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser


class BrocadeDashboard:
    """
    Class to create a dashboard. Dashboard is a set of toolbars 
    which in turn are a set of prometheus gauges groups for Brocade switch.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry) -> None:
        """  
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

        self._request_status_tb = BrocadeRequestStatusToolbar(self.sw_telemetry)
        # self._chassis_tb = BrocadeChassisToolbar(self.sw_telemetry)
        # self._fru_tb = BrocadeFRUToolbar(self.sw_telemetry)
        # self._maps_system_tb = BrocadeMAPSSystemToolbar(self.sw_telemetry)
        # self._maps_dashboard_tb = BrocadeMAPSDashboardToolbar(self.sw_telemetry)
        # self._switch_tb = BrocadeSwitchToolbar(self.sw_telemetry)
        # self._fabricshow_tb = BrocadeFabricShowToolbar(self.sw_telemetry)
        # self._fcport_params_tb = BrocadeFCPortParamsToolbar(self.sw_telemetry)
        # self._sfp_media_tb = BrocadeSFPMediaToolbar(self.sw_telemetry)
        # self._fcport_stats_tb = BrocadeFCPortStatsToolbar(self.sw_telemetry)
        # self._log_tb = BrocadeLogToolbar(self.sw_telemetry)


    def fill_dashboard_gauge_metrics(self, 
                                    request_status_parser: BrocadeRequestStatus,
                                    ch_parser: BrocadeChassisParser,
                                    fru_parser: BrocadeFRUParser,
                                    maps_parser: BrocadeMAPSParser,
                                    sw_parser: BrocadeSwitchParser,
                                    fcport_params_parser: BrocadeFCPortParametersParser,
                                    sfp_media_parser: BrocadeSwitchParser,
                                    fcport_stats_parser: BrocadeFCPortStatisticsParser) -> None:
        

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