from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar

class BrocadeMAPSToolbar(BrocadeToolbar):
    """
    Class to create Monitoring and Alerting Policy Suite (MAPS) toolbar.
    MAPS Toolbar is a set of prometheus gauges:
    chassis_name, fos version, date, time, timezone, ntp_active, ntp_configured, vf_mode, ls_number, licenses installed.
    Each unique chassis identified by chassis wwn, serial number, model and product name.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    # chassis_wwn_key = ['chassis-wwn']
    # switch_wwn_key = ['switch-wwn']
    # chassis_name_keys = chassis_wwn_key +   ['chassis-name']
    # switch_name_keys = switch_wwn_key +  ['switch-name']
    
    ssp_report_keys = BrocadeToolbar.chassis_wwn_key + ['name']
    maps_policy_keys  = BrocadeToolbar.switch_wwn_key  + ['maps-policy']
    maps_actions_keys  = BrocadeToolbar.switch_wwn_key   +  ['maps-actions']

    db_rule_keys = BrocadeToolbar.switch_wwn_key + ['category', 'name', 'time-stamp', 'object-element', 'object-value']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):

        # self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

        super().__init__(sw_telemetry)

        # system resource chassis name gauge
        self._gauge_sys_resource_chname = BrocadeGauge(name='system_resource_chname', description='System resource chassis name',
                                                       label_keys=BrocadeMAPSToolbar.chassis_name_keys)
        # cpu usage gauge
        self._gauge_cpu = BrocadeGauge(name='cpu', description='CPU usage', 
                                       label_keys=BrocadeMAPSToolbar.chassis_wwn_key, metric_key='cpu-usage')
        # flash flash gauge
        self._gauge_flash = BrocadeGauge(name='flash', description='Flash usage', 
                                         label_keys=BrocadeMAPSToolbar.chassis_wwn_key, metric_key='flash-usage')
        # memory memory gauge
        self._gauge_memory = BrocadeGauge(name='memory', description='Memory usage', 
                                          label_keys=BrocadeMAPSToolbar.chassis_wwn_key, metric_key='memory-usage')
        
        # ssp report chname gauge
        self._gauge_ssp_report_chname = BrocadeGauge(name='ssp_report_chname', description='SSP report chassis name',
                                                       label_keys=BrocadeMAPSToolbar.chassis_name_keys)
        # ssp report gauge
        # 1 - 'healthy', 2 - 'unknown', 3 - 'marginal', 4 - 'down'
        self._gauge_ssp_report  = BrocadeGauge(name='ssp_report', description='The switch status policy report state', 
                                         label_keys=BrocadeMAPSToolbar.ssp_report_keys, metric_key='operational-state-id')


        # maps config switch name gauge
        self._gauge_mapsconfig_swname  = BrocadeGauge(name='mapsconfig_swname', description='MAPS config switchanme', 
                                         label_keys=BrocadeMAPSToolbar.switch_name_keys)
        # mapsconfig switch vf-id gauge
        self._gauge_mapsconfig_vfid  = BrocadeGauge(name='mapsconfig_vfid', description='MAPS config switch VF ID', 
                                         label_keys=BrocadeMAPSToolbar.switch_name_keys, metric_key='vf-id')
        # maps config switch name gauge
        self._gauge_maps_policy  = BrocadeGauge(name='maps_policy', description='MAPS policy name', 
                                         label_keys=BrocadeMAPSToolbar.maps_policy_keys)
        # maps config switch name gauge
        self._gauge_maps_actions  = BrocadeGauge(name='maps_swname', description='MAPS actions list', 
                                         label_keys=BrocadeMAPSToolbar.maps_actions_keys)
        

        # dashboard rules switch name gauge
        self._gauge_db_swname = BrocadeGauge(name='dashboard_rule_swname', description='Dashboard rules affecting health switchname.',
                                             label_keys=BrocadeMAPSToolbar.switch_name_keys)
        # dashboard rules vfid gauge
        self._gauge_db_vfid = BrocadeGauge(name='dashboard_rule_vfid', description='Dashboard rules affecting health switch VF ID.',
                                             label_keys=BrocadeMAPSToolbar.switch_wwn_key, metric_key='repetition-count')
        # dashboard rules repetition count gauge
        self._gauge_db_repetition_count = BrocadeGauge(name='dashboard_rule_repetition_count', description='The number of times a rule was triggered.',
                                             label_keys=BrocadeMAPSToolbar.switch_wwn_key, metric_key='repetition-count')
        # dashboard rules triggered count gauge
        self._gauge_db_triggered_count = BrocadeGauge(name='dashboard_rule_repetition_count', description='The number of times the rule was triggered for the category.',
                                             label_keys=BrocadeMAPSToolbar.switch_wwn_key, metric_key='triggered-count')
        # dashboard rules severity gauge
        # 0 - no event triggired or retrieved
        # 1 - information that event condition is cleared 
        # 2 - warning that event condition detected
        self._gauge_db_triggered_count = BrocadeGauge(name='dashboard_rule_severiry', description='Dashboard rules affecting health severity.',
                                             label_keys=BrocadeMAPSToolbar.switch_wwn_key, metric_key='severity')
        



    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def gauge_sys_resource_chname(self):
        return self._gauge_sys_resource_chname


    @property
    def gauge_cpu(self):
        return self._gauge_cpu
    

    @property
    def gauge_flash(self):
        return self._gauge_flash
    

    @property
    def gauge_memory(self):
        return self._gauge_memory


    @property
    def gauge_ssp_report(self):
        return self._gauge_ssp_report


    @property
    def gauge_mapsconfig_vfid(self):
        return self._gauge_mapsconfig_vfid


    @property
    def gauge_mapsconfig_swname(self):
        return self._gauge_mapsconfig_swname
    

    @property
    def gauge_maps_policy(self):
        return self._gauge_maps_policy


    @property
    def gauge_maps_actions(self):
        return self._gauge_maps_actions
    

    @property
    def gauge_db_swname(self):
        return self._gauge_db_swname


    @property
    def gauge_db_vfid(self):
        return self._gauge_db_vfid


    @property
    def gauge_db_repetition_count(self):
        return self._gauge_db_repetition_count


    @property
    def gauge_db_triggered_count(self):
        return self._gauge_db_triggered_count


    @property
    def gauge_db_triggered_count(self):
        return self._gauge_db_triggered_count


