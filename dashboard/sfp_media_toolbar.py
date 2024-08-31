from parser.sfp_media_parser import SFPMediaParser

from .base_gauge import BaseGauge
from .base_toolbar import BaseToolbar

from collection.switch_telemetry_request import SwitchTelemetryRequest


class SFPMediaToolbar(BaseToolbar):
    """
    Class to create sfp parameters and metrics toolbar.
    SFP Media Toolbar is a set of prometheus gauges:
    sfp vendor, part number, serial number, temperature, poweron time, laser type, speed capabilities,
    wavelength, rx and tx power in uWatts and dBm, rx and tx power status.

    Each unique port identified by 'switch-wwn', 'name', 'slot-number', 'port-number'.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # sfp media switch name gauge
        self._gauge_swname = BaseGauge(name='sfp_switchname', description='Switch name in the SFP media output.', 
                                          unit_keys=SFPMediaToolbar.switch_wwn_key, parameter_key='switch-name')
        # sfp media fabric name gauge
        self._gauge_fabricname = BaseGauge(name='sfp_fabricname', description='Fabric name in the SFP media output.', 
                                              unit_keys=SFPMediaToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # sfp media port name gauge
        self._gauge_portname = BaseGauge(name='sfp_portname', description='Port name in the SFP media output.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='port-name')  
        # sfp media switch VF ID gauge
        self._gauge_switch_vfid = BaseGauge(name='sfp_switch_vfid', description='Switch virtual fabric ID in the SFP media output.', 
                                               unit_keys=SFPMediaToolbar.switch_wwn_key, metric_key='vf-id')
        # sfp media port speed gbps gauge
        self._gauge_port_speed_value = BaseGauge(name='sfp_port_speed_value', description='The speed of the port.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='port-speed-gbps')
        # sfp media port speed mode gauge
        # 0 - 'G', 1 - 'N'
        speed_mode_description = f'Whether the port speed is auto-negotiated on the specified port {SFPMediaToolbar.SPEED_MODE_ID}.'
        self._gauge_port_speed_mode = BaseGauge(name='sfp_port_speed_mode', description=speed_mode_description, 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='auto-negotiate')
        # sfp media physical state gauge
        # 0 - 'Offline', 1 - 'Online', 2 - 'Testing', 3 - 'Faulty', 4 - 'E_port', 5 - 'F_port', 
        # 6 - 'Segmented', 7 - 'Unknown', 8 - 'No_port', 9 - 'No_module', 10 - 'Laser_flt',
        # 11 - 'No_light', 12 - 'No_sync', 13 - 'In_sync', 14 - 'Port_flt', 15 - 'Hard_flt',
        # 16 - 'Diag_flt', 17 - 'Lock_ref', 18 - 'Mod_inv', 19 - 'Mod_val', 20 - 'No_sigdet'
        # 100 - 'Unknown_ID'
        port_physical_state_description = f'The physical state of a port {SFPMediaToolbar.PORT_PHYSICAL_STATE_ID}.'
        self._gauge_port_physical_state = BaseGauge(name='sfp_physical_state', description=port_physical_state_description,
                                                       unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='physical-state-id')
        # sfp media port type gauge
        # 0 - 'Unknown', 7 - 'E_Port', 10 - 'G_Port', 11 - 'U_Port', 15 - 'F_Port',
        # 16 - 'L_Port', 17 - 'FCoE Port', 19 - 'EX_Port', 20 - 'D_Port', 21 - 'SIM Port',
        # 22 - 'AF_Port', 23 - 'AE_Port', 25 - 'VE_Port', 26 - 'Ethernet Flex Port',
        # 29 - 'Flex Port', 30 - 'N_Port', 32768 - 'LB_Port'
        port_type_description = f'The port type currently enabled for the specified port {SFPMediaToolbar.PORT_TYPE_ID}.'
        self._gauge_port_type = BaseGauge(name='sfp_port_type', description=port_type_description,
                                                       unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='port-type-id')
        # sfp media vendor name gauge
        self._gauge_vendor = BaseGauge(name='sfp_vendor_name', description='The vendor name for the sfp media.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='vendor-name')
        # sfp media part number gauge
        self._gauge_pn = BaseGauge(name='sfp_pn', description='The part number for the sfp module assigned by the manufacturer.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='part-number')
        # sfp media serial number gauge
        self._gauge_sn = BaseGauge(name='sfp_sn', description='The serial number for the sfp module assigned by the manufacturer.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='serial-number')
        # sfp media laser type gauge
        self._gauge_laser_type = BaseGauge(name='sfp_laser_type', description='The short wave or long wave sfp module.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='media-distance')
        # sfp media speed capability gauge
        self._gauge_speed_capability = BaseGauge(name='sfp_speed_capability', description='The SFP module speed capabilities',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='media-speed-capability')
        # sfp media wavelength gauge
        self._gauge_wavelength = BaseGauge(name='sfp_wavelength', description='The SFP module wavelength in nm.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='wavelength')
        # sfp media power on time in human readable format gauge
        self._gauge_power_on_time = BaseGauge(name='sfp_power_on_time', description='The SFP module power on time in human readable format',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='power-on-time-hrf')
        # sfp media temperature gauge
        self._gauge_temperature = BaseGauge(name='sfp_temperature', description='The SFP module temperature in Celcius.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='temperature')
        # sfp media rx-power in uWatts gauge
        self._gauge_rx_power_uwatt = BaseGauge(name='sfp_rx_power_uwatt', description='The SFP rx power in uWatts.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='rx-power')
        # sfp media rx-power in dBm gauge
        self._gauge_rx_power_dbm = BaseGauge(name='sfp_rx_power_dbm', description='The SFP rx power in dBm.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='rx-power-dbm')
        # sfp media rx-power status id gauge
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        rx_power_status_description = f'SFP rx power status {SFPMediaToolbar.STATUS_ID}.'
        self._gauge_rx_power_status = BaseGauge(name='sfp_rx_power_status', description=rx_power_status_description, 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='rx-power-status-id')
        # sfp media tx-power in uWatts gauge
        self._gauge_tx_power_uwatt = BaseGauge(name='sfp_tx_power_uwatt', description='The SFP tx power in uWatts.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='tx-power')
        # sfp media tx-power in dBm gauge
        self._gauge_tx_power_dbm = BaseGauge(name='sfp_tx_power_dbm', description='The SFP tx power in dBm.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='tx-power-dbm')
        # sfp media tx-power status id gauge
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        tx_power_status_description = f'SFP tx power status {SFPMediaToolbar.STATUS_ID}.'
        self._gauge_tx_power_status = BaseGauge(name='sfp_tx_power_status', description=tx_power_status_description, 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='tx-power-status-id')

        # remote sfp media vendor name gauge
        self._gauge_remote_vendor = BaseGauge(name='remote_sfp_vendor_name', description='The vendor name for the remote sfp media.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='remote-vendor-name')
        # remote sfp media part number gauge
        self._gauge_remote_pn = BaseGauge(name='remote_sfp_pn', description='The part number for the remote sfp module assigned by the manufacturer.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='remote-part-number')
        # remote sfp media serial number gauge
        self._gauge_remote_sn = BaseGauge(name='remote_sfp_sn', description='The serial number for the remote sfp module assigned by the manufacturer.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='remote-serial-number')
        # remote sfp media laser type gauge
        self._gauge_remote_laser_type = BaseGauge(name='remote_sfp_laser_type', description='The short wave or long wave remote sfp module.',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='remote-laser-type')
        # remote sfp media speed capability gauge
        self._gauge_remote_speed_capability = BaseGauge(name='remote_sfp_speed_capability', description='The remote SFP module speed capabilities',
                                             unit_keys=SFPMediaToolbar.switch_port_keys, parameter_key='remote-media-speed-capability')
        # remote sfp media temperature gauge
        self._gauge_remote_temperature = BaseGauge(name='remote_sfp_temperature', description='The remote SFP module temperature in Celcius.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-temperature')

        # remote sfp media rx-power in uWatts gauge
        self._gauge_remote_rx_power_uwatt = BaseGauge(name='remote_sfp_rx_power_uwatt', description='The remote SFP rx power in uWatts.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-rx-power')
        # remote sfp media rx-power in dBm gauge
        self._gauge_remote_rx_power_dbm = BaseGauge(name='remote_sfp_rx_power_dbm', description='The remote SFP rx power in dBm.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-rx-power-dbm')
        # remote sfp media rx-power status id gauge
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        rx_power_remote_status_description = f'Remote SFP rx power status {SFPMediaToolbar.STATUS_ID}.'
        self._gauge_remote_rx_power_status = BaseGauge(name='remote_sfp_rx_power_status', description=rx_power_remote_status_description, 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-rx-power-status-id')
        # remote sfp media tx-power in uWatts gauge
        self._gauge_remote_tx_power_uwatt = BaseGauge(name='remote_sfp_tx_power_uwatt', description='The remote SFP tx power in uWatts.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-tx-power')
        # remote sfp media tx-power in dBm gauge
        self._gauge_remote_tx_power_dbm = BaseGauge(name='remote_sfp_tx_power_dbm', description='The remote SFP tx power in dBm.', 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-tx-power-dbm')
        # remote sfp media tx-power status id gauge
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        tx_power_remote_status_description = f'Remote SFP tx power status {SFPMediaToolbar.STATUS_ID}.'
        self._gauge_remote_tx_power_status = BaseGauge(name='remote_sfp_tx_power_status', description=tx_power_remote_status_description, 
                                               unit_keys=SFPMediaToolbar.switch_port_keys, metric_key='remote-media-tx-power-status-id')
    

    def fill_toolbar_gauge_metrics(self, sfp_media_parser: SFPMediaParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sfp_media_parser (BrocadeSfpMediaParser): object contains required data to fill the gauge metrics.
        """
        
        gauge_lst = [self.gauge_swname, self.gauge_fabricname, self.gauge_portname, self.gauge_switch_vfid, 
                     self.gauge_port_speed_value, self.gauge_port_speed_mode, self.gauge_port_physical_state, 
                     self.gauge_port_type, self.gauge_vendor, self.gauge_pn, self.gauge_sn, self.gauge_laser_type, 
                     self.gauge_speed_capability, self.gauge_wavelength, self.gauge_power_on_time, self.gauge_temperature, 
                     self.gauge_rx_power_uwatt, self.gauge_rx_power_dbm, self.gauge_rx_power_status, self.gauge_tx_power_uwatt, 
                     self.gauge_tx_power_dbm, self.gauge_tx_power_status, self.gauge_remote_vendor, self.gauge_remote_pn, 
                     self.gauge_remote_sn, self.gauge_remote_laser_type, self.gauge_remote_speed_capability, 
                     self.gauge_remote_temperature, self.gauge_remote_rx_power_uwatt, self.gauge_remote_rx_power_dbm, 
                     self.gauge_remote_rx_power_status, self.gauge_remote_tx_power_uwatt, self.gauge_remote_tx_power_dbm, 
                     self.gauge_remote_tx_power_status]

        for gauge in gauge_lst:
            gauge.fill_port_gauge_metrics(sfp_media_parser.sfp_media)


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
    def gauge_switch_vfid(self):
        return self._gauge_switch_vfid


    @property
    def gauge_port_speed_value(self):
        return self._gauge_port_speed_value


    @property
    def gauge_port_speed_mode(self):
        return self._gauge_port_speed_mode


    @property
    def gauge_port_physical_state(self):
        return self._gauge_port_physical_state


    @property
    def gauge_port_type(self):
        return self._gauge_port_type


    # @property
    # def gauge_enabled_port_type(self):
    #     return self._gauge_enabled_port_type


    @property
    def gauge_vendor(self):
        return self._gauge_vendor


    @property
    def gauge_pn(self):
        return self._gauge_pn


    @property
    def gauge_sn(self):
        return self._gauge_sn


    @property
    def gauge_laser_type(self):
        return self._gauge_laser_type


    @property
    def gauge_speed_capability(self):
        return self._gauge_speed_capability


    @property
    def gauge_wavelength(self):
        return self._gauge_wavelength


    @property
    def gauge_power_on_time(self):
        return self._gauge_power_on_time


    @property
    def gauge_temperature(self):
        return self._gauge_temperature


    @property
    def gauge_rx_power_uwatt(self):
        return self._gauge_rx_power_uwatt


    @property
    def gauge_rx_power_dbm(self):
        return self._gauge_rx_power_dbm


    @property
    def gauge_rx_power_status(self):
        return self._gauge_rx_power_status


    @property
    def gauge_tx_power_uwatt(self):
        return self._gauge_tx_power_uwatt


    @property
    def gauge_tx_power_dbm(self):
        return self._gauge_tx_power_dbm


    @property
    def gauge_tx_power_status(self):
        return self._gauge_tx_power_status


    @property
    def gauge_remote_vendor(self):
        return self._gauge_remote_vendor


    @property
    def gauge_remote_pn(self):
        return self._gauge_remote_pn


    @property
    def gauge_remote_sn(self):
        return self._gauge_remote_sn


    @property
    def gauge_remote_laser_type(self):
        return self._gauge_remote_laser_type


    @property
    def gauge_remote_speed_capability(self):
        return self._gauge_remote_speed_capability


    @property
    def gauge_remote_temperature(self):
        return self._gauge_remote_temperature


    @property
    def gauge_remote_rx_power_uwatt(self):
        return self._gauge_remote_rx_power_uwatt


    @property
    def gauge_remote_rx_power_dbm(self):
        return self._gauge_remote_rx_power_dbm


    @property
    def gauge_remote_rx_power_status(self):
        return self._gauge_remote_rx_power_status


    @property
    def gauge_remote_tx_power_uwatt(self):
        return self._gauge_remote_tx_power_uwatt


    @property
    def gauge_remote_tx_power_dbm(self):
        return self._gauge_remote_tx_power_dbm


    @property
    def gauge_remote_tx_power_status(self):
        return self._gauge_remote_tx_power_status
