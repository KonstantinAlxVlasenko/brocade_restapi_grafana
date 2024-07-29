from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar


class BrocadeFabricShowToolbar(BrocadeToolbar):
    """
    Class to create Fabricshow output toolbar.
    Fabricshow Toolbar is a set of prometheus gauges:
    swictch name, ip address, fabric name, did, fid, principal label, fos and paths number to the remote domain.
    Each unique switch in the fabricshow output identified by switch wwn.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    # fabricshow_fos_keys = ['switch-wwn', 'firmware-version']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # # fabricshow switch name gauge
        # self._gauge_swname = BrocadeGauge(name='fabricshow_switchname', description='Switch name in the fabricshow output', 
        #                                   label_keys=BrocadeFabricShowToolbar.switch_name_keys)
        # # fabricshow fabric name gauge
        # self._gauge_fabricname = BrocadeGauge(name='fabricshow_fabricname', description='Fabric name in the fabricshow output', 
        #                                       label_keys=BrocadeFabricShowToolbar.switch_fabric_name_keys)
        # # fabricshow ip-address gauge
        # self._gauge_switch_ip = BrocadeGauge(name='fabricshow_ip', description='Switch ip-address in the fabricshow output', 
        #                                      label_keys=BrocadeFabricShowToolbar.switch_ip_keys)
        # # fabricshow fos gauge
        # self._gauge_switch_fos = BrocadeGauge(name='fabricshow_fos', description='Firmware version in the fabricshow output', 
        #                                       label_keys=BrocadeFabricShowToolbar.fabricshow_fos_keys)        
        # # fabricshow principal label gauge
        # # 1 - ">", 0 - "_"  
        # self._gauge_principal_label = BrocadeGauge(name='fabricshow_principal_label', description='Fabricshow principal switch label. {0: "_",  1: ">"}', 
        #                                            label_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='principal')
        # # fabricshow switch did gauge
        # self._gauge_switch_did = BrocadeGauge(name='fabricshow_switch_did', description='The switch Domain_ID and embedded port D_ID.', 
        #                                       label_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='domain-id')
        # # fabricshow switch fid gauge
        # self._gauge_switch_fid = BrocadeGauge(name='fabricshow_switch_fid', description='Fabricshow fabric ID', 
        #                                       label_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='fabric-id')
        # # fabricshow path-count gauge
        # self._gauge_path_count = BrocadeGauge(name='fabricshow_path_count', description='The number of currently available paths to the remote domain.', 
        #                                       label_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='path-count')


        # fabricshow switch name gauge
        self._gauge_swname = BrocadeGauge(name='fabricshow_switchname', description='Switch name in the fabricshow output', 
                                          unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, parameter_key='switch-name')
        # fabricshow fabric name gauge
        self._gauge_fabricname = BrocadeGauge(name='fabricshow_fabricname', description='Fabric name in the fabricshow output', 
                                              unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # fabricshow ip-address gauge
        self._gauge_switch_ip = BrocadeGauge(name='fabricshow_ip', description='Switch ip-address in the fabricshow output', 
                                             unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, parameter_key='ip-address')
        # fabricshow fos gauge
        self._gauge_switch_fos = BrocadeGauge(name='fabricshow_fos', description='Firmware version in the fabricshow output', 
                                              unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, parameter_key='firmware-version')        
        # fabricshow principal label gauge
        # 1 - ">", 0 - "_"  
        self._gauge_principal_label = BrocadeGauge(name='fabricshow_principal_label', description='Fabricshow principal switch label. {0: "_",  1: ">"}', 
                                                   unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='principal')
        # fabricshow switch did gauge
        self._gauge_switch_did = BrocadeGauge(name='fabricshow_switch_did', description='The switch Domain_ID and embedded port D_ID.', 
                                              unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='domain-id')
        # fabricshow switch fid gauge
        self._gauge_switch_fid = BrocadeGauge(name='fabricshow_switch_fid', description='Fabricshow fabric ID', 
                                              unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='fabric-id')
        # fabricshow path-count gauge
        self._gauge_path_count = BrocadeGauge(name='fabricshow_path_count', description='The number of currently available paths to the remote domain.', 
                                              unit_keys=BrocadeFabricShowToolbar.switch_wwn_key, metric_key='path-count')


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_swname(self):
        return self._gauge_swname


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


    