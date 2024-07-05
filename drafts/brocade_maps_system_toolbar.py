from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar


class BrocadeMAPSSystemToolbar(BrocadeToolbar):
    """
    Class to create Monitoring and Alerting Policy Suite (MAPS) system resource and system health toolbar.
    MAPS System Toolbar is a set of prometheus gauges:
    cpu usage, flash usage, memory usage, system health.
    Each unique chassis identified by chassis wwn.
    Each unique chassis component identified by chassis wwn and component name.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    # The Switch Status Policy report keys
    ssp_report_keys = BrocadeToolbar.chassis_wwn_key + ['name']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # system resource chassis name gauge
        self._gauge_sys_resource_chname = BrocadeGauge(name='system_resource_chname', description='System resource chassis name',
                                                       label_keys=BrocadeMAPSSystemToolbar.chassis_name_keys)
        # cpu usage gauge
        self._gauge_cpu_usage = BrocadeGauge(name='cpu', description='CPU usage', 
                                       label_keys=BrocadeMAPSSystemToolbar.chassis_wwn_key, metric_key='cpu-usage')
        # flash flash gauge
        self._gauge_flash_usage = BrocadeGauge(name='flash', description='Flash usage', 
                                         label_keys=BrocadeMAPSSystemToolbar.chassis_wwn_key, metric_key='flash-usage')
        # memory memory gauge
        self._gauge_memory_usage = BrocadeGauge(name='memory', description='Memory usage', 
                                          label_keys=BrocadeMAPSSystemToolbar.chassis_wwn_key, metric_key='memory-usage')
        
        # ssp report chname gauge
        self._gauge_ssp_report_chname = BrocadeGauge(name='ssp_report_chname', description='SSP report chassis name',
                                                     label_keys=BrocadeMAPSSystemToolbar.chassis_name_keys)
        # ssp report gauge
        # 1 - 'healthy', 2 - 'unknown', 3 - 'marginal', 4 - 'down'
        self._gauge_ssp_report  = BrocadeGauge(name='ssp_report', description='The switch status policy report state', 
                                               label_keys=BrocadeMAPSSystemToolbar.ssp_report_keys, metric_key='operational-state-id')


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_sys_resource_chname(self):
        return self._gauge_sys_resource_chname


    @property
    def gauge_cpu_usage(self):
        return self._gauge_cpu_usage
    

    @property
    def gauge_flash_usage(self):
        return self._gauge_flash_usage
    

    @property
    def gauge_memory_usage(self):
        return self._gauge_memory_usage


    @property
    def gauge_ssp_report_chname(self):
        return self._gauge_ssp_report_chname


    @property
    def gauge_ssp_report(self):
        return self._gauge_ssp_report


