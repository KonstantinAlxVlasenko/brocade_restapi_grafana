from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar


class BrocadeMAPSDashboardToolbar(BrocadeToolbar):
    """
    Class to create Monitoring and Alerting Policy Suite (MAPS) policy Dashboard toolbar.
    MAPS Dashboard Toolbar is a set of prometheus gauges:
    maps policy, maps actions, triggered and repetition rule count, rule severity.
    Each unique switch identified by switch wwn.
    Each unique rule identified by switch wwn, rule catefory, rule name, timetamp rule occured and rule object.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    maps_policy_keys  = BrocadeToolbar.switch_wwn_key  + ['maps-policy']
    maps_actions_keys  = BrocadeToolbar.switch_wwn_key   +  ['maps-actions']
    db_rule_keys = BrocadeToolbar.switch_wwn_key + ['category', 'name', 'time-stamp', 'object-element', 'object-value']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # maps config switch name gauge
        self._gauge_mapsconfig_swname  = BrocadeGauge(name='mapsconfig_swname', description='MAPS config switchanme', 
                                         label_keys=BrocadeMAPSDashboardToolbar.switch_name_keys)
        # mapsconfig switch vf-id gauge
        self._gauge_mapsconfig_vfid  = BrocadeGauge(name='mapsconfig_vfid', description='MAPS config switch VF ID', 
                                         label_keys=BrocadeMAPSDashboardToolbar.switch_wwn_key, metric_key='vf-id')
        # maps config switch name gauge
        self._gauge_maps_policy  = BrocadeGauge(name='maps_policy', description='MAPS policy name', 
                                         label_keys=BrocadeMAPSDashboardToolbar.maps_policy_keys)
        # maps config switch name gauge
        self._gauge_maps_actions  = BrocadeGauge(name='maps_actions', description='MAPS actions list', 
                                         label_keys=BrocadeMAPSDashboardToolbar.maps_actions_keys)

        # dashboard rules switch name gauge
        self._gauge_db_swname = BrocadeGauge(name='dashboard_rule_swname', description='Dashboard rules affecting health switchname.',
                                             label_keys=BrocadeMAPSDashboardToolbar.switch_name_keys)
        # dashboard rules vfid gauge
        self._gauge_db_vfid = BrocadeGauge(name='dashboard_rule_vfid', description='Dashboard rules affecting health switch VF ID.',
                                             label_keys=BrocadeMAPSDashboardToolbar.switch_wwn_key, metric_key='vf-id')
        # dashboard rules repetition count gauge
        self._gauge_db_repetition_count = BrocadeGauge(name='dashboard_rule_repetition_count', description='The number of times a rule was triggered.',
                                             label_keys=BrocadeMAPSDashboardToolbar.db_rule_keys, metric_key='repetition-count')
        # dashboard rules triggered count gauge
        self._gauge_db_triggered_count = BrocadeGauge(name='dashboard_rule_triggered_count', description='The number of times the rule was triggered for the category.',
                                             label_keys=BrocadeMAPSDashboardToolbar.db_rule_keys, metric_key='triggered-count')
        # dashboard rules severity gauge
        # 0 - no event triggired or retrieved
        # 1 - information that event condition is cleared 
        # 2 - warning that event condition detected
        self._gauge_db_severity = BrocadeGauge(name='dashboard_rule_severiry', description='Dashboard rules affecting health severity.',
                                             label_keys=BrocadeMAPSDashboardToolbar.db_rule_keys, metric_key='severity')
        

    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


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
    def gauge_db_severity(self):
        return self._gauge_db_severity


