
from parser import FCPortParametersParser

from base_gauge import BaseGauge
from base_toolbar import BaseToolbar

from switch_telemetry_request import SwitchTelemetryRequest


class FCPortParamsToolbar(BaseToolbar):
    """
    Class to create port parameters, state and status toolbar.
    Port parameters Toolbar is a set of prometheus gauges:
    port name, port speed value and mode, LD mode, physical state, port type, enabled port type, port status, port pod license.
    Each unique port identified by 'switch-wwn', 'slot-number', 'port-number', 'port-index', 'port-id'.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    switch_port_extended_keys  = BaseToolbar.switch_port_keys + ['port-index', 'port-id']
    # switch_port_name_keys = switch_port_extended_keys + ['port-name']

    PORT_PHYSICAL_STATE_ID = {0: 'Offline', 1: 'Online', 2: 'Testing', 3: 'Faulty', 4: 'E_Port', 5: 'F_Port', 
                              6: 'Segmented', 7: 'Unknown',8: 'No_Port', 9: 'No_Module', 10: 'Laser_Flt', 
                              11: 'No_Light', 12: 'No_Sync', 13: 'In_Sync', 14: 'Port_Flt', 15: 'Hard_Flt', 
                              16: 'Diag_Flt', 17: 'Lock_Ref', 18: 'Mod_Inv', 19: 'Mod_Val', 20: 'No_Sigdet', 
                              100: 'Unknown_ID'}
    
    PORT_TYPE_ID = {0: 'Unknown', 7: 'E-Port', 10: 'G-Port', 11: 'U-Port', 15: 'F-Port', 16: 'L-Port',
                    17: 'FCoE Port', 19: 'EX-Port', 20: 'D-Port', 21: 'SIM Port', 22: 'AF-Port',
                    23: 'AE-Port', 25: 'VE-Port', 26: 'Ethernet Flex Port', 29: 'Flex Port',
                    30: 'N-Port', 32768: 'LB-Port'}
    
    LONG_DISTANCE_LEVEL_ID = {0: 'LD Disabled', 1: 'L0', 2: 'L1', 3: 'L2',
                           4: 'LE', 5: 'L0.5', 6: 'LD', 7: 'LS'}
    
    SPEED_MODE_ID = {0: 'G', 1: 'N'}

    PORT_STATUS_ID = {-1: 'Disabled (Persistent)', 0: 'Disabled', 1: 'Enabled'}

    NO_DEVICE_ENABLED_PORT_ID = {0: '-', 1: 'Empty Active'}

    UPORT_GPORT_ENABLED_ID = {0: '_', 1: 'Enabled U-Port ', 2: 'Enabled G-Port'}

    POD_LICENSE_STATUS_ID = {0: 'POD Released', 1: 'POD Reserved', 2: 'POD Disabled', 3: 'POD Enabled', 4: 'POD Unknown'}


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # fcport params switch name gauge
        self._gauge_swname = BaseGauge(name='fcport_params_switchname', description='Switch name in the FC port parameters output.', 
                                          unit_keys=FCPortParamsToolbar.switch_wwn_key, parameter_key='switch-name')
        # fcport params fabric name gauge
        self._gauge_fabricname = BaseGauge(name='fcport_params_fabricname', description='Fabric name in the FC port parameters output.', 
                                              unit_keys=FCPortParamsToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # fcport params port name gauge
        self._gauge_portname = BaseGauge(name='fcport_params_portname', description='Port name in the FC port parameters output.',
                                             unit_keys=FCPortParamsToolbar.switch_port_extended_keys, parameter_key='port-name')
        # fcport params neighbor wwpn gauge
        self._gauge_neighbor_wwpn = BaseGauge(name='fcport_params_neighbor_wwpn', description='The Fibre Channel WWN of the neighbor port.',
                                                unit_keys=FCPortParamsToolbar.switch_port_extended_keys, parameter_key='neighbor-port-wwn-str')        
        # fcport params switch VF ID gauge
        self._gauge_switch_vfid = BaseGauge(name='fcport_params_switch_vfid', description='Switch virtual fabric ID in the FC port parameters output.', 
                                               unit_keys=FCPortParamsToolbar.switch_wwn_key, metric_key='vf-id')
        # fcport params port speed gbps gauge
        self._gauge_port_speed_value = BaseGauge(name='fcport_params_port_speed_value', description='The speed for of the port.', 
                                               unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='port-speed-gbps')
        # fcport params port speed mode gauge
        # 0 - 'G', 1 - 'N'
        speed_mode_description = f'Whether the port speed is auto-negotiated on the specified port {FCPortParamsToolbar.SPEED_MODE_ID}.'
        self._gauge_port_speed_mode = BaseGauge(name='fcport_params_port_speed_mode', description=speed_mode_description, 
                                               unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='auto-negotiate')
        # fcport params long distance mode gauge
        # 0 - Long-distance is disabled for this port.
        # 1 - L0 configures the port as a regular port.
        # 2 - L1 configures the value as long (<= 50 km)
        # 3 - L2 configures the value as super long (<= 100 km)
        # 4 - LE mode configures an E_Port distance as greater than 5 km and up to 10 km.
        # 5 - L0.5 configures the value as medium long (<= 25 km) .
        # 6 - LD configures the value as automatic long distance.
        # 7 - LS mode configures the value as a static long-distance link with a fixed buffer allocation greater than 10 km.'
        ld_mode_description = f'The long-distance level {FCPortParamsToolbar.LONG_DISTANCE_LEVEL_ID}.'
        self._gauge_port_ld_mode = BaseGauge(name='fcport_params_long_distace_mode', description=ld_mode_description, 
                                               unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='long-distance')
        # fcport params physical state gauge
        # 0 - 'Offline', 1 - 'Online', 2 - 'Testing', 3 - 'Faulty', 4 - 'E_port', 5 - 'F_port', 
        # 6 - 'Segmented', 7 - 'Unknown', 8 - 'No_port', 9 - 'No_module', 10 - 'Laser_flt',
        # 11 - 'No_light', 12 - 'No_sync', 13 - 'In_sync', 14 - 'Port_flt', 15 - 'Hard_flt',
        # 16 - 'Diag_flt', 17 - 'Lock_ref', 18 - 'Mod_inv', 19 - 'Mod_val', 20 - 'No_sigdet'
        # 100 - 'Unknown_ID'
        port_physical_state_description = f'The physical state of a port {FCPortParamsToolbar.PORT_PHYSICAL_STATE_ID}.'
        self._gauge_port_physical_state = BaseGauge(name='fcport_params_physical_state', description=port_physical_state_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='physical-state-id')
        # port physical state status gauge
        port_physical_state_status_description = f'Port physical state status depending on port enable state {FCPortParamsToolbar.STATUS_ID}.'
        self._gauge_port_physical_state_status = BaseGauge(name='fcport_params_port_physical_state_status', description=port_physical_state_status_description,
                                                              unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='physical-state-status-id')
        # fcport params port type gauge
        # 0 - 'Unknown', 7 - 'E_Port', 10 - 'G_Port', 11 - 'U_Port', 15 - 'F_Port',
        # 16 - 'L_Port', 17 - 'FCoE Port', 19 - 'EX_Port', 20 - 'D_Port', 21 - 'SIM Port',
        # 22 - 'AF_Port', 23 - 'AE_Port', 25 - 'VE_Port', 26 - 'Ethernet Flex Port',
        # 29 - 'Flex Port', 30 - 'N_Port', 32768 - 'LB_Port'
        port_type_description = f'The port type currently enabled for the specified port {FCPortParamsToolbar.PORT_TYPE_ID}.'
        self._gauge_port_type = BaseGauge(name='fcport_params_port_type', description=port_type_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='port-type-id')
        # fcport params port type for enabled ports gauge
        enabled_port_type_description = f'The port type for the specified port if its port status is "Enabled" {FCPortParamsToolbar.PORT_TYPE_ID}.'
        self._gauge_enabled_port_type = BaseGauge(name='fcport_params_enabled_port_type', description=enabled_port_type_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='enabled-port-type-id')
        # fcport params port status gauge
        # -1 - 'Disabled (Persistent)', 0 - 'Disabled', 1 - 'Enabled'
        port_status_description = f'The physical state of a port {FCPortParamsToolbar.PORT_STATUS_ID}.'
        self._gauge_port_status = BaseGauge(name='fcport_params_port_status', description=port_status_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='port-enable-status-id')
        # fcport params enabled port wo device connected gauge
        # 0 - '_', 1 - 'Enabled'
        nodevice_enabled_port_description = f'Enabled port with no device connected flag {FCPortParamsToolbar.NO_DEVICE_ENABLED_PORT_ID}.'
        self._gauge_nodevice_enabled_port = BaseGauge(name='fcport_params_nodevice_enabled_port', description=nodevice_enabled_port_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='nodevice-enabled-port')
        # fcport params enabled port with U-Port or G-Port type gauge
        # 0 - '_', 1 - 'Enabled U-Port ', 'Enabled G-Port'
        uport_gport_enabled_description = f'Enabled port with U-Port or G-Port type {FCPortParamsToolbar.UPORT_GPORT_ENABLED_ID}.'
        self._gauge_uport_gport_enabled_port = BaseGauge(name='fcport_params_uport_gport_enabled_port', description=uport_gport_enabled_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='uport-gport-enabled')
        # fcport params pod license status gauge
        # 0 - 'POD Released', 1 - 'POD Reserved', 2 - 'POD Disabled', 3 - 'POD Enabled', 4 - 'POD Unknown'
        pod_license_state_description = f'The POD license status for a port. {FCPortParamsToolbar.POD_LICENSE_STATUS_ID}.'
        self._gauge_pod_license_state = BaseGauge(name='fcport_params_pod_license_state', description=pod_license_state_description,
                                                       unit_keys=FCPortParamsToolbar.switch_port_extended_keys, metric_key='pod-license-status-id') 


    def fill_toolbar_gauge_metrics(self, fcport_params_parser: FCPortParametersParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.
        """

        gauge_lst = [self.gauge_swname, self.gauge_fabricname, self.gauge_portname, self.gauge_neighbor_wwpn, 
                     self.gauge_switch_vfid, self.gauge_port_speed_value, self.gauge_port_speed_mode, 
                     self.gauge_port_ld_mode, self.gauge_port_physical_state, self.gauge_port_physical_state_status, 
                     self.gauge_port_type, self.gauge_enabled_port_type, self.gauge_port_status, 
                     self.gauge_nodevice_enabled_port, self.gauge_uport_gport_enabled_port, self.gauge_pod_license_state,]


        for gauge in gauge_lst:
            gauge.fill_port_gauge_metrics(fcport_params_parser.fcport_params)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_swname(self):
        return self._gauge_swname


    @property
    def gauge_fabricname(self):
         return self._gauge_fabricname


    @property
    def gauge_portname(self):
        return self._gauge_portname
    

    @property
    def gauge_neighbor_wwpn(self):
        return self._gauge_neighbor_wwpn


    @property
    def gauge_switch_vfid(self):
        return self._gauge_switch_vfid


    @property
    def gauge_port_speed_value(self):
        return self._gauge_port_speed_value


    @property
    def gauge_port_speed_mode(self):
        return self._gauge_port_speed_mode


    @property
    def gauge_port_ld_mode(self):
        return self._gauge_port_ld_mode


    @property
    def gauge_port_physical_state(self):
        return self._gauge_port_physical_state


    @property
    def gauge_port_physical_state_status(self):
        return self._gauge_port_physical_state_status


    @property
    def gauge_port_type(self):
        return self._gauge_port_type


    @property
    def gauge_enabled_port_type(self):
        return self._gauge_enabled_port_type


    @property
    def gauge_port_status(self):
        return self._gauge_port_status


    @property
    def gauge_nodevice_enabled_port(self):
        return self._gauge_nodevice_enabled_port


    @property
    def gauge_uport_gport_enabled_port(self):
        return self._gauge_uport_gport_enabled_port

    @property
    def gauge_pod_license_state(self):
        return self._gauge_pod_license_state


    