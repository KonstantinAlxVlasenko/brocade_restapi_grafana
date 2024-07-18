from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar


class BrocadeFCPortParamsToolbar(BrocadeToolbar):
    """
    Class to create Fabricshow output toolbar.
    Fabricshow Toolbar is a set of prometheus gauges:
    swictch name, ip address, fabric name, did, fid, principal label, fos and paths number to the remote domain.
    Each unique switch in the fabricshow output identified by switch wwn.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    switch_port_extended_keys  = BrocadeToolbar.switch_port_keys + ['port-index', 'port-id']
    switch_port_name_keys = switch_port_extended_keys + ['port-name']

    PORT_PHYSICAL_STATE_ID = {0: 'Offline', 1: 'Online', 2: 'Testing', 3: 'Faulty', 4: 'E_Port', 5: 'F_Port', 
                              6: 'Segmented', 7: 'Unknown',8: 'No_Port', 9: 'No_Module', 10: 'Laser_Flt', 
                              11: 'No_Light', 12: 'No_Sync', 13: 'In_Sync', 14: 'Port_Flt', 15: 'Hard_Flt', 
                              16: 'Diag_Flt', 17: 'Lock_Ref', 18: 'Mod_Inv', 19: 'Mod_Val', 20: 'No_Sigdet', 
                              100: 'Unknown_ID'}
    
    PORT_TYPE_ID = {0: 'Unknown', 7: 'E-Port', 10: 'G-Port', 11: 'U-Port', 15: 'F-Port', 16: 'L-Port',
                    17: 'FCoE Port', 19: 'EX-Port', 20: 'D-Port', 21: 'SIM Port', 22: 'AF-Port',
                    23: 'AE-Port', 25: 'VE-Port', 26: 'Ethernet Flex Port', 29: 'Flex Port',
                    30: 'N-Port', 32768: 'LB-Port'}
    
    LONG_DISTANCE_LEVEL = {0: 'LD Disabled', 1: 'L0', 2: 'L1', 3: 'L2',
                           4: 'LE', 5: 'L0.5', 6: 'LD', 7: 'LS'}
    
    SPEED_MODE_ID = {0: 'G', 1: 'N'}

    PORT_STATUS_ID = {-1: 'Disabled (Persistent)', 0: 'Disabled', 1: 'Enabled'}

    NO_DEVICE_ENABLED_PORT_ID = {0: '-', 1: 'Empty Active'}

    POD_LICENSE_STATUS_ID = {0: 'POD Released', 1: 'POD Reserved', 2: 'POD Disabled', 3: 'POD Enabled', 4: 'POD Unknown'}


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # fcport params switch name gauge
        self._gauge_swname = BrocadeGauge(name='fcport_params_switchname', description='Switch name in the FC port paramters output.', 
                                          label_keys=BrocadeFCPortParamsToolbar.switch_name_keys)
        # fcport params fabric name gauge
        self._gauge_fabricname = BrocadeGauge(name='fcport_params_fabricname', description='Fabric name in the FC port paramters output.', 
                                              label_keys=BrocadeFCPortParamsToolbar.switch_fabric_name_keys)
        # fcport params port name gauge
        self._gauge_portname = BrocadeGauge(name='fcport_params_portname', description='Port name in the FC port paramters output.',
                                             label_keys=BrocadeFCPortParamsToolbar.switch_port_name_keys)
        # fcport params switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='fcport_params_switch_vfid', description='Switch virtual fabric ID in the FC port paramters output.', 
                                               label_keys=BrocadeFCPortParamsToolbar.switch_wwn_key, metric_key='vf-id')
        # fcport params port speed gbps gauge
        self._gauge_port_speed_value = BrocadeGauge(name='fcport_params_port_speed_value', description='The speed for of the port.', 
                                               label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='port-speed-gbps')
        # fcport params port speed mode gauge
        # 0 - 'G', 1 - 'N'
        speed_mode_description = f'Whether the port speed is auto-negotiated on the specified port {BrocadeFCPortParamsToolbar.SPEED_MODE_ID}.'
        self._gauge_port_speed_mode = BrocadeGauge(name='fcport_params_port_speed_mode', description=speed_mode_description, 
                                               label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='auto-negotiate')
        # fcport params long distance mode gauge
        # 0 - Long-distance is disabled for this port.
        # 1 - L0 configures the port as a regular port.
        # 2 - L1 configures the value as long (<= 50 km)
        # 3 - L2 configures the value as super long (<= 100 km)
        # 4 - LE mode configures an E_Port distance as greater than 5 km and up to 10 km.
        # 5 - L0.5 configures the value as medium long (<= 25 km) .
        # 6 - LD configures the value as automatic long distance.
        # 7 - LS mode configures the value as a static long-distance link with a fixed buffer allocation greater than 10 km.'
        ld_mode_description = f'The long-distance level {BrocadeFCPortParamsToolbar.LONG_DISTANCE_LEVEL}.'
        self._gauge_port_ld_mode = BrocadeGauge(name='fcport_params_long_distace_mode', description=ld_mode_description, 
                                               label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='long-distance')
        # fcport params physical state gauge
        # 0 - 'Offline', 1 - 'Online', 2 - 'Testing', 3 - 'Faulty', 4 - 'E_port', 5 - 'F_port', 
        # 6 - 'Segmented', 7 - 'Unknown', 8 - 'No_port', 9 - 'No_module', 10 - 'Laser_flt',
        # 11 - 'No_light', 12 - 'No_sync', 13 - 'In_sync', 14 - 'Port_flt', 15 - 'Hard_flt',
        # 16 - 'Diag_flt', 17 - 'Lock_ref', 18 - 'Mod_inv', 19 - 'Mod_val', 20 - 'No_sigdet'
        # 100 - 'Unknown_ID'
        port_physical_state_description = f'The physical state of a port {BrocadeFCPortParamsToolbar.PORT_PHYSICAL_STATE_ID}.'
        self._gauge_port_physical_state = BrocadeGauge(name='fcport_params_physical_state', description=port_physical_state_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='physical-state-id')
        # fcport params port type gauge
        # 0 - 'Unknown', 7 - 'E_Port', 10 - 'G_Port', 11 - 'U_Port', 15 - 'F_Port',
        # 16 - 'L_Port', 17 - 'FCoE Port', 19 - 'EX_Port', 20 - 'D_Port', 21 - 'SIM Port',
        # 22 - 'AF_Port', 23 - 'AE_Port', 25 - 'VE_Port', 26 - 'Ethernet Flex Port',
        # 29 - 'Flex Port', 30 - 'N_Port', 32768 - 'LB_Port'
        port_type_description = f'The port type currently enabled for the specified port {BrocadeFCPortParamsToolbar.PORT_PHYSICAL_STATE_ID}.'
        self._gauge_port_type = BrocadeGauge(name='fcport_params_port_type', description=port_type_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='port-type-id')
        # fcport params port type for enabled ports gauge
        self._gauge_port_type = BrocadeGauge(name='fcport_params_port_type_enabled', description=port_type_description,
                                            label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='enabled-port-type-id')
        # fcport params port status gauge
        # -1 - 'Disabled (Persistent)', 0 - 'Disabled', 1 - 'Enabled'
        port_status_description = f'The physical state of a port {BrocadeFCPortParamsToolbar.PORT_STATUS_ID}.'
        self._gauge_port_status = BrocadeGauge(name='fcport_params_port_status', description=port_status_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='port-enable-status-id')
        # fcport params enabled port wo device connected gauge
        # 0 - '_', 1 - 'Enabled'
        nodevice_enabled_port_description = f'Enabled port with no device connected flag {BrocadeFCPortParamsToolbar.NO_DEVICE_ENABLED_PORT_ID}.'
        self._gauge_nodevice_enabled_port = BrocadeGauge(name='fcport_params_nodevice_enabled_port', description=nodevice_enabled_port_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='nodevice_enabled_port_flag')
        
        # fcport params enabled port with U-Port or G-Port type gauge
        # 0 - '_', 1 - 'Enabled'
        uport_gport_enabled_description = f'Enabled port with U-Port or G-Port type {BrocadeFCPortParamsToolbar.NO_DEVICE_ENABLED_PORT_ID}.'
        self._gauge_nodevice_enabled_port = BrocadeGauge(name='fcport_params_nodevice_enabled_port', description=nodevice_enabled_port_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='nodevice_enabled_port_flag')
        
        
        # fcport params pod license status gauge
        # 0 - 'POD Released', 1 - 'POD Reserved', 2 - 'POD Disabled', 3 - 'POD Enabled', 4 - 'POD Unknown'
        pod_license_state_description = f'The POD license status for a port. {BrocadeFCPortParamsToolbar.POD_LICENSE_STATUS_ID}.'
        self._gauge_pod_license_state = BrocadeGauge(name='fcport_params_pod_license_state', description=pod_license_state_description,
                                                       label_keys=BrocadeFCPortParamsToolbar.switch_port_extended_keys, metric_key='pod-license-status-id') 





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


    