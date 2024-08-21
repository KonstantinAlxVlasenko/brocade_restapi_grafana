from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_switch_parser import BrocadeSwitchParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


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
    # switch_uptime_keys = ['switch-wwn', 'up-time-hrf']


    SWITCH_STATE_ID = {0:  'Undefined', 2: 'Online', 3: 'Offline', 7: 'Testing'}
    SWITCH_ROLE_ID = {-1: 'Disabled', 0: 'Subordinate', 1: 'Principal'}
    SWITCH_MODE_ID = {0: 'Native', 1: 'Native', 2: 'Access Gateway'}
    MODE_STATUS_ID = {0: 'Disabled', 1: 'Enabled'}


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # # switch name gauge
        # self._gauge_swname = BrocadeGauge(name='switch_name', description='Switch name', 
        #                                    label_keys=BrocadeSwitchToolbar.switch_name_keys)
        # # switch ip address gauge
        # self._gauge_switch_ip = BrocadeGauge(name='switch_ip_address', description='Switch IP address', 
        #                                    label_keys=BrocadeSwitchToolbar.switch_ip_keys)
        # # switch fabric name gauge
        # self._gauge_switch_fabric_name = BrocadeGauge(name='switch_fabric_name', description='Switch fabric name', 
        #                                    label_keys=BrocadeSwitchToolbar.switch_fabric_name_keys)
        # # switch uptime gauge
        # self._gauge_switch_uptime = BrocadeGauge(name='switch_uptime', description='Switch uptime', 
        #                                    label_keys=BrocadeSwitchToolbar.switch_uptime_keys)
        # # switch state gauge
        # #  0 - Undefined, 2 - Online. 3 = Offline, 7 - Testing
        # self._gauge_switch_state = BrocadeGauge(name='switch_state', description='The current state of the switch.', 
        #                                         label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='operational-status')
        # # switch role gauge
        # # -1 - Disabled, 0 - Subordinate, 1 - Principal
        # self._gauge_switch_role = BrocadeGauge(name='switch_role', description='Switch role: Principal, Subordinate, or Disabled.', 
        #                                        label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='switch-role-id')
        # # switch mode gauge
        # # 0, 1 - Native, 2 - 'Access Gateway'
        # self._gauge_switch_mode = BrocadeGauge(name='switch_mode', description='Switch operation mode: Access Gateway (if AG is enabled).', 
        #                                        label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='ag-mode')
        # # switch domain id gauge
        # self._gauge_switch_did = BrocadeGauge(name='switch_did', description='Switch domain ID', 
        #                                       label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='domain-id')
        # # switch fabric id gauge
        # self._gauge_switch_fid = BrocadeGauge(name='switch_fid', description='Switch fabric ID', 
        #                                       label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='fabric-id')
        # # switch port quantity gauge
        # self._gauge_switch_port_quantity = BrocadeGauge(name='switch_port_quantity', description='', 
        #                                                 label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='port-member-quantity')
        # # switch VF ID gauge
        # self._gauge_switch_vfid = BrocadeGauge(name='switch_vfid', description='Switch virtual fabric ID', 
        #                                        label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='vf-id')
        # # base switch status gauge
        # # 0 - Disabled, 1 - Enabled
        # self._gauge_base_switch_status = BrocadeGauge(name='base_switch_status', description='Base switch status', 
        #                                               label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='base-switch-enabled')
        # # default switch status
        # # 0 - Disabled, 1 - Enabled
        # self._gauge_default_switch_status = BrocadeGauge(name='default_switch_status', description='Default switch status.', 
        #                                                  label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='default-switch-status')
        # # logical isl status
        # # 0 - Disabled, 1 - Enabled
        # self._gauge_logical_isl_status = BrocadeGauge(name='logical_isl_status', description='Logical isl status.', 
        #                                               label_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='logical-isl-enabled')


        # switch name gauge
        self._gauge_swname = BrocadeGauge(name='switch_name', description='Switch name', 
                                           unit_keys=BrocadeSwitchToolbar.switch_wwn_key, parameter_key='switch-name')
        # switch ip address gauge
        self._gauge_switch_ip = BrocadeGauge(name='switch_ip_address', description='Switch IP address', 
                                           unit_keys=BrocadeSwitchToolbar.switch_wwn_key, parameter_key='ip-address')
        # switch fabric name gauge
        self._gauge_switch_fabricname = BrocadeGauge(name='switch_fabric_name', description='Switch fabric name', 
                                           unit_keys=BrocadeSwitchToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # switch uptime gauge
        self._gauge_switch_uptime = BrocadeGauge(name='switch_uptime', description='Switch uptime', 
                                           unit_keys=BrocadeSwitchToolbar.switch_wwn_key, parameter_key='up-time-hrf')
        # switch state gauge
        #  0 - Undefined, 2 - Online. 3 = Offline, 7 - Testing
        switch_state_description = f'The current state of the switch {BrocadeSwitchToolbar.SWITCH_STATE_ID}.'
        self._gauge_switch_state = BrocadeGauge(name='switch_state', description=switch_state_description, 
                                                unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='operational-status')
        # switch role gauge
        # -1 - Disabled, 0 - Subordinate, 1 - Principal
        switch_role_description = f'Switch role: Principal, Subordinate, or Disabled {BrocadeSwitchToolbar.SWITCH_ROLE_ID}.'
        self._gauge_switch_role = BrocadeGauge(name='switch_role', description=switch_role_description, 
                                               unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='switch-role-id')
        # switch mode gauge
        # 0, 1 - Native, 2 - 'Access Gateway'
        switch_mode_description = f'Switch operation mode: Access Gateway (if AG is enabled) {BrocadeSwitchToolbar.SWITCH_MODE_ID}.'
        self._gauge_switch_mode = BrocadeGauge(name='switch_mode', description=switch_mode_description, 
                                               unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='ag-mode')
        # switch domain id gauge
        self._gauge_switch_did = BrocadeGauge(name='switch_did', description='Switch domain ID', 
                                              unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='domain-id')
        # switch fabric id gauge
        self._gauge_switch_fid = BrocadeGauge(name='switch_fid', description='Switch fabric ID', 
                                              unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='fabric-id')
        # switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='switch_vfid', description='Switch virtual fabric ID', 
                                               unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='vf-id')
        # switch port quantity gauge
        self._gauge_switch_port_quantity = BrocadeGauge(name='switch_port_quantity', description='', 
                                                        unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='port-member-quantity')
        # online port quantity gauge
        self._gauge_online_port_quantity = BrocadeGauge(name='online_port_quantity', description='Number of online ports', 
                                                        unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='online-port-quantity')
        # uport-gport-enabled-quantity gauge
        self._gauge_uport_gport_enabled_quantity = BrocadeGauge(name='uport_gport_enabled_quantity', 
                                                                description='Number of enabled ports with no device connected to', 
                                                                unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='uport-gport-enabled-quantity')
        # base switch status gauge
        # 0 - Disabled, 1 - Enabled
        base_switch_status_description = f'Base switch status {BrocadeSwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_base_switch_status = BrocadeGauge(name='base_switch_status', description=base_switch_status_description, 
                                                      unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='base-switch-enabled')
        # default switch status
        # 0 - Disabled, 1 - Enabled
        default_switch_status_description = f'Default switch status {BrocadeSwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_default_switch_status = BrocadeGauge(name='default_switch_status', description=default_switch_status_description, 
                                                         unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='default-switch-status')
        # logical isl status
        # 0 - Disabled, 1 - Enabled
        logiacal_isl_status_description = f'Logical isl status {BrocadeSwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_logical_isl_status = BrocadeGauge(name='logical_isl_status', description=logiacal_isl_status_description, 
                                                      unit_keys=BrocadeSwitchToolbar.switch_wwn_key, metric_key='logical-isl-enabled')
        
    
    def fill_toolbar_gauge_metrics(self, sw_parser: BrocadeSwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
        """

        gauge_lst = [self.gauge_swname, self.gauge_switch_ip, self.gauge_switch_fabricname, self.gauge_switch_uptime, 
                     self.gauge_switch_state, self.gauge_switch_mode, self.gauge_switch_role, self.gauge_switch_did, 
                     self.gauge_switch_fid, self.gauge_switch_vfid, self.gauge_switch_port_quantity, 
                     self.gauge_online_port_quantity, self.gauge_uport_gport_enabled_quantity, 
                     self.gauge_base_switch_status, self.gauge_default_switch_status, self.gauge_logical_isl_status,
]
        for gauge in gauge_lst:
            gauge.fill_switch_gauge_metrics(sw_parser.fc_switch)
        
        # self.gauge_swname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_ip.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_fabricname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_uptime.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_state.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_mode.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_role.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_did.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_fid.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_vfid.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_switch_port_quantity.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_online_port_quantity.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_uport_gport_enabled_quantity.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_base_switch_status.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_default_switch_status.fill_switch_gauge_metrics(sw_parser.fc_switch)
        # self.gauge_logical_isl_status.fill_switch_gauge_metrics(sw_parser.fc_switch)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_swname(self):
        return self._gauge_swname


    @property
    def gauge_switch_ip(self):
        return self._gauge_switch_ip


    @property
    def gauge_switch_fabricname(self):
        return self._gauge_switch_fabricname


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
    def gauge_online_port_quantity(self):
        return self._gauge_online_port_quantity
    

    @property
    def gauge_uport_gport_enabled_quantity(self):
        return self._gauge_uport_gport_enabled_quantity


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








