from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar


class BrocadeSwitchToolbar(BrocadeToolbar):
    """
    Class to create Switch toolbar.
    Switch Toolbar is a set of prometheus gauges:
    swictch name, ip address, fabric name, uptime, switch state, switch mode, switch role, 
    did, fid, port quantity, vf id, base and default switches status, logical isl status.
    Each unique switch identified by switch wwn.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    # switch_ip_keys = ['switch-wwn', 'ip-address']
    # switch_fabric_name_keys = ['switch-wwn', 'fabric-user-friendly-name']
    switch_uptime_keys = ['switch-wwn', 'up-time-hrf']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # switch name gauge
        self._gauge_swname = BrocadeGauge(name='switch_name', description='Switch name', 
                                           label_keys=BrocadeSwitchToolbar.switch_name_keys)
        # switch ip address gauge
        self._gauge_switch_ip = BrocadeGauge(name='switch_ip_address', description='Switch IP address', 
                                           label_keys=BrocadeSwitchToolbar.switch_ip_keys)
        # switch fabric name gauge
        self._gauge_switch_fabric_name = BrocadeGauge(name='switch_fabric_name', description='Switch fabric name', 
                                           label_keys=BrocadeSwitchToolbar.switch_fabric_name_keys)
        # switch uptime gauge
        self._gauge_switch_uptime = BrocadeGauge(name='switch_uptime', description='Switch uptime', 
                                           label_keys=BrocadeSwitchToolbar.switch_uptime_keys)
        # switch state gauge
        #  0 - Undefined, 2 - Online. 3 = Offline, 7 - Testing
        self._gauge_switch_state = BrocadeGauge(name='switch_state', description='The current state of the switch.', 
                                                label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='operational-status')
        # switch role gauge
        # -1 - Disabled, 0 - Subordinate, 1 - Principal
        self._gauge_switch_role = BrocadeGauge(name='switch_role', description='Switch role: Principal, Subordinate, or Disabled.', 
                                               label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='switch-role-id')
        # switch mode gauge
        # 0, 1 - Native, 2 - 'Access Gateway'
        self._gauge_switch_mode = BrocadeGauge(name='switch_mode', description='Switch operation mode: Access Gateway (if AG is enabled).', 
                                               label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='ag-mode')
        # switch domain id gauge
        self._gauge_switch_did = BrocadeGauge(name='switch_did', description='Switch domain ID', 
                                              label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='domain-id')
        # switch fabric id gauge
        self._gauge_switch_fid = BrocadeGauge(name='switch_fid', description='Switch fabric ID', 
                                              label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='fabric-id')
        # switch port quantity gauge
        self._gauge_switch_port_quantity = BrocadeGauge(name='switch_port_quantity', description='', 
                                                        label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='port-member-quantity')
        # switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='switch_vfid', description='Switch virtual fabric ID', 
                                               label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='vf-id')
        # base switch status gauge
        # 0 - Disabled, 1 - Enabled
        self._gauge_base_switch_status = BrocadeGauge(name='base_switch_status', description='Base switch status', 
                                                      label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='base-switch-enabled')
        # default switch status
        # 0 - Disabled, 1 - Enabled
        self._gauge_default_switch_status = BrocadeGauge(name='default_switch_status', description='Default switch status.', 
                                                         label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='default-switch-status')
        # logical isl status
        # 0 - Disabled, 1 - Enabled
        self._gauge_logical_isl_status = BrocadeGauge(name='logical_isl_status', description='Logical isl status.', 
                                                      label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='logical-isl-enabled')


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_swname(self):
        return self._gauge_swname


    @property
    def gauge_switch_ip(self):
        return self._gauge_switch_ip


    @property
    def gauge_switch_fabric_name(self):
        return self._gauge_switch_fabric_name


    @property
    def gauge_switch_uptime(self):
        return self._gauge_switch_uptime


    @property
    def gauge_switch_state(self):
        return self._gauge_switch_state


    @property
    def gauge_switch_role(self):
        return self._gauge_switch_role


    @property
    def gauge_switch_mode(self):
        return self._gauge_switch_mode


    @property
    def gauge_switch_did(self):
        return self._gauge_switch_did


    @property
    def gauge_switch_fid(self):
        return self._gauge_switch_fid


    @property
    def gauge_switch_port_quantity(self):
        return self._gauge_switch_port_quantity


    @property
    def gauge_switch_vfid(self):
        return self._gauge_switch_vfid


    @property
    def gauge_base_switch_status(self):
        return self._gauge_base_switch_status


    @property
    def gauge_default_switch_status(self):
        return self._gauge_default_switch_status


    @property
    def gauge_logical_isl_status(self):
        return self._gauge_logical_isl_status








