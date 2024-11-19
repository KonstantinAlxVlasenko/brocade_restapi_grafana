from parser.switch_parser import SwitchParser

from .base_gauge import BaseGauge
from .base_toolbar import BaseToolbar

from collection.switch_telemetry_request import SwitchTelemetryRequest
from parser.fcport_stats_parser import FCPortStatisticsParser


class SwitchToolbar(BaseToolbar):
    """
    Class to create Switch toolbar.
    Switch Toolbar is a set of prometheus gauges:
    swictch name, ip address, fabric name, uptime, switch state, switch mode, switch role, 
    did, fid, port quantity, vf id, base and default switches status, logical isl status.
    Each unique switch identified by switch wwn.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    SWITCH_STATE_ID = {0:  'Undefined', 2: 'Online', 3: 'Offline', 7: 'Testing'}
    SWITCH_ROLE_ID = {-1: 'Disabled', 0: 'Subordinate', 1: 'Principal'}
    SWITCH_MODE_ID = {0: 'Native', 1: 'Native', 2: 'Access Gateway'}
    MODE_STATUS_ID = {0: 'Disabled', 1: 'Enabled'}


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # switch name gauge
        self._gauge_swname = BaseGauge(name='switch_name', description='Switch name', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, parameter_key='switch-name')
        # switch ip address gauge
        self._gauge_switch_ip = BaseGauge(name='switch_ip_address', description='Switch IP address', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, parameter_key='ip-address')
        # switch fabric name gauge
        self._gauge_switch_fabricname = BaseGauge(name='switch_fabric_name', description='Switch fabric name', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # switch uptime gauge
        self._gauge_switch_uptime = BaseGauge(name='switch_uptime', description='Switch uptime', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, parameter_key='up-time-hrf')
        # switch uptime days gauge
        self._gauge_switch_uptime_days = BaseGauge(name='switch_uptime_days', description='Switch uptime_days', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, metric_key='up-time-d')
        # switch uptime hours gauge
        self._gauge_switch_uptime_hours = BaseGauge(name='switch_uptime_hours', description='Switch uptime_hours', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, metric_key='up-time-hr')
        # switch uptime mins gauge
        self._gauge_switch_uptime_mins = BaseGauge(name='switch_uptime_minutes', description='Switch uptime_minutes', 
                                           unit_keys=SwitchToolbar.switch_wwn_key, metric_key='up-time-min')
        # switch uptime status gauge
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        switch_uptime_status_description  = f'Switch uptime status id {SwitchToolbar.STATUS_ID}.'
        self._gauge_switch_uptime_status = BaseGauge(name='switch_uptime_status', 
                                                     description=switch_uptime_status_description, 
                                                     unit_keys=SwitchToolbar.switch_wwn_key, metric_key='up-time-status-id')        
        # switch state gauge
        #  0 - Undefined, 2 - Online. 3 = Offline, 7 - Testing
        switch_state_description = f'The current state of the switch {SwitchToolbar.SWITCH_STATE_ID}.'
        self._gauge_switch_state = BaseGauge(name='switch_state', description=switch_state_description, 
                                                unit_keys=SwitchToolbar.switch_wwn_key, metric_key='operational-status')
        # switch role gauge
        # -1 - Disabled, 0 - Subordinate, 1 - Principal
        switch_role_description = f'Switch role: Principal, Subordinate, or Disabled {SwitchToolbar.SWITCH_ROLE_ID}.'
        self._gauge_switch_role = BaseGauge(name='switch_role', description=switch_role_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='switch-role-id')
        # switch mode gauge
        # 0, 1 - Native, 2 - 'Access Gateway'
        switch_mode_description = f'Switch operation mode: Access Gateway (if AG is enabled) {SwitchToolbar.SWITCH_MODE_ID}.'
        self._gauge_switch_mode = BaseGauge(name='switch_mode', description=switch_mode_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='ag-mode')
        # switch domain id gauge
        self._gauge_switch_did = BaseGauge(name='switch_did', description='Switch domain ID', 
                                              unit_keys=SwitchToolbar.switch_wwn_key, metric_key='domain-id')
        # switch fabric id gauge
        self._gauge_switch_fid = BaseGauge(name='switch_fid', description='Switch fabric ID', 
                                              unit_keys=SwitchToolbar.switch_wwn_key, metric_key='fabric-id')
        # switch VF ID gauge
        self._gauge_switch_vfid = BaseGauge(name='switch_vfid', description='Switch virtual fabric ID', 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='vf-id')
        # switch port quantity gauge
        self._gauge_switch_port_quantity = BaseGauge(name='switch_port_quantity', description='', 
                                                        unit_keys=SwitchToolbar.switch_wwn_key, metric_key='port-member-quantity')
        # online port quantity gauge
        self._gauge_online_port_quantity = BaseGauge(name='online_port_quantity', description='Number of online ports', 
                                                        unit_keys=SwitchToolbar.switch_wwn_key, metric_key='online-port-quantity')
        # uport-gport-enabled-quantity gauge
        self._gauge_uport_gport_enabled_quantity = BaseGauge(name='uport_gport_enabled_quantity', 
                                                                description='Number of enabled ports with no device connected to', 
                                                                unit_keys=SwitchToolbar.switch_wwn_key, metric_key='uport-gport-enabled-quantity')
        # port-physical-state-status-id
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        port_physical_state_status_description = f'Switch port physical state status depending on port enable state {SwitchToolbar.STATUS_ID}.'
        self._gauge_switch_port_physical_state_status = BaseGauge(name='switch_port_physical_state_status', 
                                                                description=port_physical_state_status_description, 
                                                                unit_keys=SwitchToolbar.switch_wwn_key, metric_key='port-physical-state-status-id')
        # base switch status gauge
        # 0 - Disabled, 1 - Enabled
        base_switch_status_description = f'Base switch status {SwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_base_switch_status = BaseGauge(name='base_switch_status', description=base_switch_status_description, 
                                                      unit_keys=SwitchToolbar.switch_wwn_key, metric_key='base-switch-enabled')
        # default switch status
        # 0 - Disabled, 1 - Enabled
        default_switch_status_description = f'Default switch status {SwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_default_switch_status = BaseGauge(name='default_switch_status', description=default_switch_status_description, 
                                                         unit_keys=SwitchToolbar.switch_wwn_key, metric_key='default-switch-status')
        # logical isl status
        # 0 - Disabled, 1 - Enabled
        logiacal_isl_status_description = f'Logical isl status {SwitchToolbar.MODE_STATUS_ID}.'
        self._gauge_logical_isl_status = BaseGauge(name='logical_isl_status', description=logiacal_isl_status_description, 
                                                      unit_keys=SwitchToolbar.switch_wwn_key, metric_key='logical-isl-enabled')
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        # port in-throughput-status-id
        description_in_throughput_status_id = f"Switch port receive throughput status id {SwitchToolbar.STATUS_ID}."
        self._gauge_switch_in_throughput_status_id = BaseGauge(name='switch_port_in_throughput_status', 
                                                                description=description_in_throughput_status_id, 
                                                                unit_keys=SwitchToolbar.switch_wwn_key, metric_key='in-throughput-status-id')
        # port out-throughput-status-id
        description_out_throughput_status_id = f"Switch port transmit throughput status id {SwitchToolbar.STATUS_ID}."
        self._gauge_switch_out_throughput_status_id = BaseGauge(name='switch_port_out_throughput_status', 
                                                                description=description_out_throughput_status_id, 
                                                                unit_keys=SwitchToolbar.switch_wwn_key, metric_key='out-throughput-status-id')
        # low severiry errors port status id
        description_low_severity_errors_status_id = f"Switch port error status ID {SwitchToolbar.STATUS_ID} for the LOW severity errors {FCPortStatisticsParser.LOW_SEVERITY_ERROR_LEAFS}."
        self._gauge_low_severity_errors_status_id = BaseGauge(name="switch_low_severity_errors_port_status_id", description=description_low_severity_errors_status_id, 
                                                                      unit_keys=SwitchToolbar.switch_wwn_key, metric_key="low-severity-errors_port-status-id")
        # medium severiry errors port status id
        description_medium_severity_errors_status_id = f"Switch port error status ID {SwitchToolbar.STATUS_ID} for the MEDIUM severity errors {FCPortStatisticsParser.MEDIUM_SEVERITY_ERROR_LEAFS}."
        self._gauge_medium_severity_errors_status_id = BaseGauge(name="switch_medium_severity_errors_port_status_id", description=description_medium_severity_errors_status_id, 
                                                                         unit_keys=SwitchToolbar.switch_wwn_key, metric_key="medium-severity-errors_port-status-id")
        # high severiry errors port status id
        description_high_severity_errors_status_id = f"Switch port error status ID {SwitchToolbar.STATUS_ID} for the HIGH severity errors {FCPortStatisticsParser.HIGH_SEVERITY_ERROR_LEAFS}."
        self._gauge_high_severity_errors_status_id = BaseGauge(name="switch_high_severity_errors_port_status_id", description=description_high_severity_errors_status_id, 
                                    unit_keys=SwitchToolbar.switch_wwn_key, metric_key="high-severity-errors_port-status-id")
        # sfp media temperature status id gauge
        temperature_status_description = f'Switch SFP temperature status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_temperature_status = BaseGauge(name='switch_sfp_temperature_status', description=temperature_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='temperature-status-id')
        # remote sfp media temperature status id gauge
        temperature_remote_status_description = f'Switch remote SFP temperature status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_remote_temperature_status = BaseGauge(name='switch_remote_sfp_temperature_status', description=temperature_remote_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='remote-media-temperature-status-id')
        # sfp media rx-power status id gauge
        rx_power_status_description = f'Switch SFP rx power status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_rx_power_status = BaseGauge(name='switch_sfp_rx_power_status', description=rx_power_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='rx-power-status-id')
        # sfp media tx-power status id gauge
        tx_power_status_description = f'Switch SFP tx power status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_tx_power_status = BaseGauge(name='switch_sfp_tx_power_status', description=tx_power_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='tx-power-status-id')
        # remote sfp media rx-power status id gauge
        rx_power_remote_status_description = f'Switch remote SFP rx power status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_remote_rx_power_status = BaseGauge(name='switch_remote_sfp_rx_power_status', description=rx_power_remote_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='remote-media-rx-power-status-id')
        # remote sfp media tx-power status id gauge
        tx_power_remote_status_description = f'Switch remote SFP tx power status {SwitchToolbar.STATUS_ID}.'
        self._gauge_sfp_remote_tx_power_status = BaseGauge(name='switch_remote_sfp_tx_power_status', description=tx_power_remote_status_description, 
                                               unit_keys=SwitchToolbar.switch_wwn_key, metric_key='remote-media-tx-power-status-id')
        
    
    def fill_toolbar_gauge_metrics(self, sw_parser: SwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
        """

        gauge_lst = [self.gauge_swname, self.gauge_switch_ip, self.gauge_switch_fabricname, 
                     self.gauge_switch_uptime, self.gauge_switch_uptime_status,
                     self.gauge_switch_uptime_days, self.gauge_switch_uptime_hours, self.gauge_switch_uptime_mins,
                     self.gauge_switch_state, self.gauge_switch_mode, self.gauge_switch_role, self.gauge_switch_did, 
                     self.gauge_switch_fid, self.gauge_switch_vfid, self.gauge_switch_port_quantity, 
                     self.gauge_online_port_quantity, self.gauge_uport_gport_enabled_quantity, self.gauge_switch_port_physical_state_status,
                     self.gauge_base_switch_status, self.gauge_default_switch_status, self.gauge_logical_isl_status, 
                     self.gauge_switch_in_throughput_status_id, self.gauge_switch_out_throughput_status_id,
                     self.gauge_low_severity_errors_status_id, self.gauge_medium_severity_errors_status_id,
                     self.gauge_high_severity_errors_status_id, self.gauge_sfp_temperature_status,
                     self.gauge_sfp_remote_temperature_status, self.gauge_sfp_rx_power_status,
                     self.gauge_sfp_tx_power_status, self.gauge_sfp_remote_rx_power_status, self.gauge_sfp_remote_tx_power_status]
        for gauge in gauge_lst:
            gauge.fill_switch_gauge_metrics(sw_parser.fc_switch)
        

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
    def gauge_switch_uptime_days(self):
        return self._gauge_switch_uptime_days
    

    @property
    def gauge_switch_uptime_hours(self):
        return self._gauge_switch_uptime_hours
    

    @property
    def gauge_switch_uptime_mins(self):
        return self._gauge_switch_uptime_mins


    @property
    def gauge_switch_uptime_status(self):
        return self._gauge_switch_uptime_status


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
    def gauge_switch_port_physical_state_status(self):
        return self._gauge_switch_port_physical_state_status


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
    

    @property
    def gauge_switch_in_throughput_status_id(self):
        return self._gauge_switch_in_throughput_status_id
    

    @property
    def gauge_switch_out_throughput_status_id(self):
        return self._gauge_switch_out_throughput_status_id
    

    @property
    def gauge_low_severity_errors_status_id(self):
        return self._gauge_low_severity_errors_status_id
    

    @property
    def gauge_medium_severity_errors_status_id(self):
        return self._gauge_medium_severity_errors_status_id
    

    @property
    def gauge_high_severity_errors_status_id(self):
        return self._gauge_high_severity_errors_status_id
    

    @property
    def gauge_sfp_temperature_status(self):
        return self._gauge_sfp_temperature_status
    

    @property
    def gauge_sfp_remote_temperature_status(self):
        return self._gauge_sfp_remote_temperature_status
    

    @property
    def gauge_sfp_rx_power_status(self):
        return self._gauge_sfp_rx_power_status
    

    @property
    def gauge_sfp_tx_power_status(self):
        return self._gauge_sfp_tx_power_status
    

    @property
    def gauge_sfp_remote_rx_power_status(self):
        return self._gauge_sfp_remote_rx_power_status
    

    @property
    def gauge_sfp_remote_tx_power_status(self):
        return self._gauge_sfp_remote_tx_power_status








