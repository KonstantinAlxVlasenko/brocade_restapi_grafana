from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar
from brocade_maps_parser import BrocadeMAPSParser


class MAPSDashboardToolbar(BrocadeToolbar):
    """
    Class to create Monitoring and Alerting Policy Suite (MAPS) policy Dashboard toolbar.
    MAPS Dashboard Toolbar is a set of prometheus gauges:
    maps policy, maps actions, triggered and repetition rule count, rule severity.
    Each unique switch identified by switch wwn.
    Each unique rule identified by switch wwn, rule catefory, rule name, timetamp rule occured and rule object.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    # maps_policy_keys  = BrocadeToolbar.switch_wwn_key  + ['maps-policy']
    # maps_actions_keys  = BrocadeToolbar.switch_wwn_key   +  ['maps-actions']
    db_rule_keys = BrocadeToolbar.switch_wwn_key + ['category', 'name', 'time-stamp', 'object-element', 'object-value']

    DB_SEVERITY_RULE_ID = {0: 'no event triggired or retrieved',
                                 1: 'information that event condition is cleared',
                                 2: 'warning that event condition detected'}


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)
        
        # maps config switch name gauge
        self._gauge_mapsconfig_swname  = BrocadeGauge(name='mapsconfig_swname', description='MAPS config switchanme', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='switch-name')
        # maps config fabric name gauge
        self._gauge_mapsconfig_fabricname  = BrocadeGauge(name='mapsconfig_fabric_name', description='MAPS config fabric name', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # mapsconfig switch vf-id gauge
        self._gauge_mapsconfig_vfid  = BrocadeGauge(name='mapsconfig_vfid', description='MAPS config switch VF ID', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, metric_key='vf-id')
        # maps config switch name gauge
        self._gauge_maps_policy  = BrocadeGauge(name='maps_policy', description='MAPS policy name', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='maps-policy')
        # maps config switch name gauge
        self._gauge_maps_actions  = BrocadeGauge(name='maps_actions', description='MAPS actions list', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='maps-actions')

        # dashboard rules switch name gauge
        self._gauge_db_swname = BrocadeGauge(name='dashboard_rule_swname', description='Dashboard rules affecting health switchname.',
                                             unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='switch-name')
        # dashboard rules fabric name gauge
        self._gauge_db_fabricname  = BrocadeGauge(name='dashboard_rule_fabric_name', description='Dashboard rules affecting health fabric name', 
                                         unit_keys=MAPSDashboardToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # dashboard rules vfid gauge
        self._gauge_db_vfid = BrocadeGauge(name='dashboard_rule_vfid', description='Dashboard rules affecting health switch VF ID.',
                                             unit_keys=MAPSDashboardToolbar.switch_wwn_key, metric_key='vf-id')
        # dashboard rules repetition count gauge
        self._gauge_db_repetition_count = BrocadeGauge(name='dashboard_rule_repetition_count', description='The number of times a rule was triggered.',
                                             unit_keys=MAPSDashboardToolbar.db_rule_keys, metric_key='repetition-count')
        # dashboard rules triggered count gauge
        self._gauge_db_triggered_count = BrocadeGauge(name='dashboard_rule_triggered_count', description='The number of times the rule was triggered for the category.',
                                                        unit_keys=MAPSDashboardToolbar.db_rule_keys, metric_key='triggered-count')
        # dashboard rules severity gauge
        # 0 - no event triggired or retrieved
        # 1 - information that event condition is cleared 
        # 2 - warning that event condition detected
        db_severity_description = f'Dashboard rules affecting health severity {MAPSDashboardToolbar.DB_SEVERITY_RULE_ID}.'
        self._gauge_db_severity = BrocadeGauge(name='dashboard_rule_severiry', description=db_severity_description,
                                                unit_keys=MAPSDashboardToolbar.db_rule_keys, metric_key='severity')
        
     
    def fill_toolbar_gauge_metrics(self, maps_parser: BrocadeMAPSParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            maps_parser (BrocadeMAPSParser): object contains required data to fill the gauge metrics.
        """
        
        # 'maps policy, actions'
        maps_config_gauges_lst = [self.gauge_mapsconfig_swname, self.gauge_mapsconfig_fabricname, self.gauge_mapsconfig_vfid, 
                                  self.gauge_maps_policy, self.gauge_maps_actions]
        for gauge in maps_config_gauges_lst:
            gauge.fill_switch_gauge_metrics(maps_parser.maps_config)
 
        # 'maps dashboard'
        dashboard_rules_gauges_lst = [self.gauge_db_swname, self.gauge_db_fabricname, self.gauge_db_vfid, 
                                     self.gauge_db_repetition_count, self.gauge_db_triggered_count, self.gauge_db_severity]
        for gauge in dashboard_rules_gauges_lst:
            gauge.fill_switch_gauge_metrics(maps_parser.dashboard_rule)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_mapsconfig_swname(self):
        return self._gauge_mapsconfig_swname
    

    @property
    def gauge_mapsconfig_fabricname(self):
        return self._gauge_mapsconfig_fabricname
    

    @property
    def gauge_mapsconfig_vfid(self):
        return self._gauge_mapsconfig_vfid    
    

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
    def gauge_db_fabricname(self):
        return self._gauge_db_fabricname


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
    def gauge_db_severity(self):
        return self._gauge_db_severity


