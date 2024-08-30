from parser import SwitchParser

from base_gauge import BaseGauge
from base_toolbar import BaseToolbar

from switch_telemetry_request import SwitchTelemetryRequest


class FabricShowToolbar(BaseToolbar):
    """
    Class to create Fabricshow output toolbar.
    Fabricshow Toolbar is a set of prometheus gauges:
    swictch name, ip address, fabric name, did, fid, principal label, fos and paths number to the remote domain.
    Each unique switch in the fabricshow output identified by switch wwn.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    # local and fabric switch wwn keys
    switch_wwn_pair_keys = ['switch-wwn', 'fabric-switch-wwn']

    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # fabricshow remote switch name gauge
        self._gauge_fabric_swname = BaseGauge(name='fabricshow_remote_switchname', description='Switch name in the fabricshow output', 
                                          unit_keys=FabricShowToolbar.switch_wwn_pair_keys, parameter_key='fabric-switch-name')
        # fabricshow local switch name gauge
        self._gauge_local_swname = BaseGauge(name='fabricshow_local_switchname', description='Local switch name', 
                                          unit_keys=FabricShowToolbar.switch_wwn_pair_keys, parameter_key='switch-name')        
        # fabricshow fabric name gauge
        self._gauge_fabricname = BaseGauge(name='fabricshow_fabricname', description='Fabric name in the fabricshow output', 
                                              unit_keys=FabricShowToolbar.switch_wwn_pair_keys, parameter_key='fabric-user-friendly-name')
        # fabricshow ip-address gauge
        self._gauge_switch_ip = BaseGauge(name='fabricshow_ip', description='Switch ip-address in the fabricshow output', 
                                             unit_keys=FabricShowToolbar.switch_wwn_pair_keys, parameter_key='ip-address')
        # fabricshow fos gauge
        self._gauge_switch_fos = BaseGauge(name='fabricshow_fos', description='Firmware version in the fabricshow output', 
                                              unit_keys=FabricShowToolbar.switch_wwn_pair_keys, parameter_key='firmware-version')        
        # fabricshow principal label gauge
        # 1 - ">", 0 - "_"  
        self._gauge_principal_label = BaseGauge(name='fabricshow_principal_label', description='Fabricshow principal switch label. {0: "_",  1: ">"}', 
                                                   unit_keys=FabricShowToolbar.switch_wwn_pair_keys, metric_key='principal')
        # fabricshow switch did gauge
        self._gauge_switch_did = BaseGauge(name='fabricshow_switch_did', description='The switch Domain_ID and embedded port D_ID.', 
                                              unit_keys=FabricShowToolbar.switch_wwn_pair_keys, metric_key='domain-id')
        # fabricshow switch fid gauge
        self._gauge_switch_fid = BaseGauge(name='fabricshow_switch_fid', description='Fabricshow fabric ID', 
                                              unit_keys=FabricShowToolbar.switch_wwn_pair_keys, metric_key='fabric-id')
        # fabricshow path-count gauge
        self._gauge_path_count = BaseGauge(name='fabricshow_path_count', description='The number of currently available paths to the remote domain.', 
                                              unit_keys=FabricShowToolbar.switch_wwn_pair_keys, metric_key='path-count')


    def fill_toolbar_gauge_metrics(self, sw_parser: SwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
        """

        fabricshow_gauges_lst = [self.gauge_fabric_swname, self.gauge_local_swname, self.gauge_fabricname, 
                                 self.gauge_switch_ip, self.gauge_switch_fos, self.gauge_principal_label, 
                                 self.gauge_switch_did, self.gauge_switch_fid, self.gauge_path_count]
        
        for gauge in fabricshow_gauges_lst:
            gauge.fill_switch_gauge_metrics(sw_parser.fabric)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"
    

    @property
    def gauge_fabric_swname(self):
        return self._gauge_fabric_swname


    @property
    def gauge_local_swname(self):
        return self._gauge_local_swname


    @property
    def gauge_fabricname(self):
         return self._gauge_fabricname


    @property
    def gauge_switch_ip(self):
        return self._gauge_switch_ip


    @property
    def gauge_switch_fos(self):
        return self._gauge_switch_fos


    @property
    def gauge_principal_label(self):
        return self._gauge_principal_label


    @property
    def gauge_switch_did(self):
        return self._gauge_switch_did


    @property
    def gauge_switch_fid(self):
        return self._gauge_switch_fid


    @property
    def gauge_path_count(self):
        return self._gauge_path_count


    