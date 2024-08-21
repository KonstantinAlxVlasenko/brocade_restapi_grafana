from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_maps_parser import BrocadeMAPSParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser

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
    ssp_report_keys = BrocadeToolbar.chassis_switch_wwn_keys + ['name']

    SSP_REPORT_STATUS_ID = {1: 'healthy', 2: 'unknown', 3: 'marginal', 4: 'down'}


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # system resource chassis name gauge
        self._gauge_sys_resource_chname = BrocadeGauge(name='system_resource_chname', description='System resource chassis name',
                                                       unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, parameter_key='chassis-name')
        # switch name
        self._gauge_sys_resource_swname = BrocadeGauge(name='system_resource_swname', description='System resource switch name', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.switch_wwn_key, parameter_key='switch-name')
        # fabric name
        self._gauge_sys_resource_fabricname = BrocadeGauge(name='system_resource_fabric_name', description='System resource fabric name', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_sys_resource_vfid = BrocadeGauge(name='ssystem_resource_vfid', description='System resource VF id', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.switch_wwn_key, parameter_key='vf-id')

        # cpu usage gauge
        self._gauge_cpu_usage = BrocadeGauge(name='cpu_usage', description='CPU usage', 
                                            unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='cpu-usage')
        self._gauge_cpu_usage_status = BrocadeGauge(name='cpu_usage_status', description=f'CPU usage status {BrocadeMAPSSystemToolbar.STATUS_ID}',
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='cpu-usage-status-id')
        # flash usage gauge
        self._gauge_flash_usage = BrocadeGauge(name='flash_usage', description='Flash usage', 
                                            unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='flash-usage')
        self._gauge_flash_usage_status = BrocadeGauge(name='flash_usage_status', description=f'Flash usage status {BrocadeMAPSSystemToolbar.STATUS_ID}',
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='flash-usage-status-id')
        # memory usage gauge
        self._gauge_memory_usage = BrocadeGauge(name='memory_usage', description='Memory usage', 
                                                unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='memory-usage')
        self._gauge_memory_usage_status = BrocadeGauge(name='memory_usage_status', description=f'Memory usage status {BrocadeMAPSSystemToolbar.STATUS_ID}',
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, metric_key='memory-usage-status-id')
        
        # ssp report chname gauge
        self._gauge_ssp_report_chname = BrocadeGauge(name='ssp_report_chname', description='SSP report chassis name',
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_wwn_key, parameter_key='chassis-name')
        # switch name
        self._gauge_ssp_report_swname = BrocadeGauge(name='ssp_report_swname', description='SSP report switch name', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, parameter_key='switch-name')
        # fabric name
        self._gauge_ssp_report_fabricname = BrocadeGauge(name='ssp_report_fabric_name', description='SSP report fabric name', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_ssp_report_vfid = BrocadeGauge(name='ssp_report_vfid', description='SSP report VF id', 
                                                    unit_keys=BrocadeMAPSSystemToolbar.chassis_switch_wwn_keys, parameter_key='vf-id')
        # ssp report gauge
        # 1 - 'healthy', 2 - 'unknown', 3 - 'marginal', 4 - 'down'
        ssp_report_description = f'The switch status policy report state {BrocadeMAPSSystemToolbar.SSP_REPORT_STATUS_ID}'
        self._gauge_ssp_report_state  = BrocadeGauge(name='ssp_report_state', description=ssp_report_description, 
                                                unit_keys=BrocadeMAPSSystemToolbar.ssp_report_keys, metric_key='status-id')


    def fill_toolbar_gauge_metrics(self, maps_parser: BrocadeMAPSParser, sw_parser: BrocadeSwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            maps_parser (BrocadeMAPSParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.
        """

        
        # self.gauge_sys_resource_chname.fill_chassis_gauge_metrics(maps_parser.system_resources)
        # self.gauge_cpu_usage.fill_chassis_gauge_metrics(maps_parser.system_resources)
        # self.gauge_flash_usage.fill_chassis_gauge_metrics(maps_parser.system_resources)
        # self.gauge_memory_usage.fill_chassis_gauge_metrics(maps_parser.system_resources)
        
        # 'maps system resources'
        system_resources = BrocadeToolbar.clone_chassis_to_vf(maps_parser.system_resources, sw_parser, component_level=False)
        sys_resource_gauge_lst = [self.gauge_sys_resource_chname, self.gauge_sys_resource_swname, 
                                  self.gauge_sys_resource_fabricname, self.gauge_sys_resource_vfid, 
                                  self.gauge_cpu_usage, self.gauge_cpu_usage_status,
                                  self.gauge_flash_usage, self.gauge_flash_usage_status,
                                  self.gauge_memory_usage, self.gauge_memory_usage_status]
        for gauge in sys_resource_gauge_lst:
            gauge.fill_switch_gauge_metrics(system_resources)

        # 'maps system health'
        ssp_report = BrocadeToolbar.clone_chassis_to_vf(maps_parser.ssp_report, sw_parser, component_level=False)
        ssp_report_gauge_lst = [self.gauge_ssp_report_chname, self.gauge_ssp_report_swname, self.gauge_ssp_report_fabricname,
                                self.gauge_ssp_report_vfid]

        for gauge in ssp_report_gauge_lst:
            gauge.fill_switch_gauge_metrics(ssp_report)

        if not maps_parser.ssp_report_parameters:
            return
        
        # parameter name and it's status id
        for ssp_report_parameter in maps_parser.ssp_report_parameters:
            self.gauge_ssp_report_state.fill_switch_gauge_metrics(ssp_report,
                                                                renamed_keys={ssp_report_parameter + BrocadeMAPSParser.STATUS_ID_TAG: 'status-id'}, 
                                                                add_dict={'name': ssp_report_parameter})
                

    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_sys_resource_chname(self):
        return self._gauge_sys_resource_chname
    

    @property
    def gauge_sys_resource_swname(self):
        return self._gauge_sys_resource_swname
    

    @property
    def gauge_sys_resource_fabricname(self):
        return self._gauge_sys_resource_fabricname
    

    @property
    def gauge_sys_resource_vfid(self):
        return self._gauge_sys_resource_vfid


    @property
    def gauge_cpu_usage(self):
        return self._gauge_cpu_usage
    

    @property
    def gauge_cpu_usage_status(self):
        return self._gauge_cpu_usage_status


    @property
    def gauge_flash_usage(self):
        return self._gauge_flash_usage
    

    @property
    def gauge_flash_usage_status(self):
        return self._gauge_flash_usage_status
    

    @property
    def gauge_memory_usage(self):
        return self._gauge_memory_usage
    

    @property
    def gauge_memory_usage_status(self):
        return self._gauge_memory_usage_status    


    @property
    def gauge_ssp_report_chname(self):
        return self._gauge_ssp_report_chname
    

    @property
    def gauge_ssp_report_swname(self):
        return self._gauge_ssp_report_swname


    @property
    def gauge_ssp_report_fabricname(self):
        return self._gauge_ssp_report_fabricname
    

    @property
    def gauge_ssp_report_vfid(self):
        return self._gauge_ssp_report_vfid
    

    @property
    def gauge_ssp_report_state(self):
        return self._gauge_ssp_report_state


