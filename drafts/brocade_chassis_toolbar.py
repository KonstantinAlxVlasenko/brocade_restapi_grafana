from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_chassis_parser import BrocadeChassisParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeChassisToolbar(BrocadeToolbar):
    """
    Class to create Chassis toolbar.
    Chassis Toolbar is a set of prometheus gauges:
    chassis_name, fos version, date, time, timezone, ntp_active, ntp_configured, vf_mode, ls_number, licenses installed.
    Each unique chassis identified by chassis wwn, serial number, model and product name.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    chassis_keys = ['chassis-wwn', 'switch-serial-number', 'model', 'product-name']
    # chassis_uf_name_keys = chassis_keys + ['chassis-user-friendly-name']
    # fos_keys = chassis_keys + ['firmware-version']
    # chassis_date_keys = chassis_keys + ['date']
    # chassis_time_keys = chassis_keys + ['time']
    # tz_keys = chassis_keys + ['time-zone']
    
    # ntp_active_keys = ['chassis-wwn', 'active-server']
    # ntp_configured_keys = ['chassis-wwn', 'ntp-server-address']
    license_keys = ['chassis-wwn', 'name', 'feature']

    VF_MODE_STATUS_ID = {-1: 'Not Applicable',  1: 'Enabled', 0: 'Disabled'}

    LICENSE_STATUS_ID = {0: 'OK', 
                         1: 'Temporary', 
                         2: 'Expired'}


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # # chassis name gauge
        # self._gauge_chname = BrocadeGauge(name='chassis_name', description='Chassis name', 
        #                                   label_keys=BrocadeChassisToolbar.chassis_uf_name_keys)
        # # fos version gauge
        # self._gauge_fos =  BrocadeGauge(name='chassis_fos', description='Chassis firmware version', 
        #                                 label_keys=BrocadeChassisToolbar.fos_keys)
        # # date gauge
        # self._gauge_date =  BrocadeGauge(name='chassis_date', description='Chassis date', 
        #                                  label_keys=BrocadeChassisToolbar.chassis_date_keys)
        # # time gauge
        # self._gauge_time =  BrocadeGauge(name='chassis_time', description='Chassis time', 
        #                                  label_keys=BrocadeChassisToolbar.chassis_time_keys)
        # # timezone gauge
        # self._gauge_tz =  BrocadeGauge(name='chassis_tz', description='Chassis timezone', 
        #                                label_keys=BrocadeChassisToolbar.tz_keys)
        # # active ntp
        # self._gauge_ntp_active = BrocadeGauge(name='ntp_server', description='Active NTP Address', 
        #                                       label_keys=BrocadeChassisToolbar.ntp_active_keys)
        # # configured ntp
        # self._gauge_ntp_configured = BrocadeGauge(name='ntp_list', description='Configured NTP Address(es)', 
        #                                           label_keys=BrocadeChassisToolbar.ntp_configured_keys)
        

        # chassis name gauge
        self._gauge_chname = BrocadeGauge(name='chassis_name', description='Chassis name', 
                                          unit_keys=BrocadeChassisToolbar.chassis_keys, parameter_key='chassis-user-friendly-name')
        # fos version gauge
        self._gauge_fos =  BrocadeGauge(name='chassis_fos', description='Chassis firmware version', 
                                        unit_keys=BrocadeChassisToolbar.chassis_keys, parameter_key='firmware-version')
        # date gauge
        self._gauge_date =  BrocadeGauge(name='chassis_date', description='Chassis date', 
                                         unit_keys=BrocadeChassisToolbar.chassis_keys, parameter_key='date')
        # time gauge
        self._gauge_time =  BrocadeGauge(name='chassis_time', description='Chassis time', 
                                         unit_keys=BrocadeChassisToolbar.chassis_keys, parameter_key='time')
        # timezone gauge
        self._gauge_tz =  BrocadeGauge(name='chassis_tz', description='Chassis timezone', 
                                       unit_keys=BrocadeChassisToolbar.chassis_keys, parameter_key='time-zone')
        # active ntp
        self._gauge_ntp_active = BrocadeGauge(name='ntp_server', description='Active NTP Address', 
                                              unit_keys=BrocadeChassisToolbar.chassis_wwn_key, parameter_key='active-server')
        # configured ntp
        self._gauge_ntp_configured = BrocadeGauge(name='ntp_list', description='Configured NTP Address(es)', 
                                                  unit_keys=BrocadeChassisToolbar.chassis_wwn_key, parameter_key='ntp-server-address')
        # vf mode gauge
        # -1 - 'Not Applicable',  1 - 'Enabled', 0 - 'Disabled'
        vf_mode_description = f'Chassis virtual fabrics mode {BrocadeChassisToolbar.VF_MODE_STATUS_ID}.'
        self._gauge_vf_mode =  BrocadeGauge(name='chassis_vf_mode', description=vf_mode_description, 
                                            unit_keys=BrocadeChassisToolbar.chassis_keys, metric_key='virtual-fabrics-mode-id')
        # ls quantity gauge
        self._gauge_ls_number =  BrocadeGauge(name='chassis_ls_number', description='Chassis logical switch qunatity', 
                                              unit_keys=BrocadeChassisToolbar.chassis_keys, metric_key='ls-number')
        # license status gauge
        # 0 - No expiration date
        # 1 - Expiration date has not arrived
        # 2 - Expiration date has arrived
        license_status_description = f'Switch licenses status {BrocadeChassisToolbar.LICENSE_STATUS_ID}.'
        self._gauge_license_status = BrocadeGauge(name='license_status', description=license_status_description, 
                                            unit_keys=BrocadeChassisToolbar.license_keys, metric_key='license-status-id')
        # license capacity gauge
        self._gauge_license_capacity = BrocadeGauge(name='license_capacity', description='POD license capacity', 
                                            unit_keys=BrocadeChassisToolbar.license_keys, metric_key='capacity')        
        # license exp date gauge
        self._gauge_license_exp_date = BrocadeGauge(name='license_exp_date', description='License expiration date', 
                                            unit_keys=BrocadeChassisToolbar.license_keys, parameter_key='expiration-date')


    def fill_toolbar_gauge_metrics(self, ch_parser: BrocadeChassisParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            ch_parser (BrocadeChassisParser): object contains required data to fill the gauge metrics.
        """

        self.gauge_ch_name.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_fos.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_date.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_time.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_tz.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_ntp_active.fill_chassis_gauge_metrics(ch_parser.ntp_server)
        self.gauge_ntp_configured.fill_chassis_gauge_metrics(ch_parser.ntp_server)
        self.gauge_vf_mode.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_ls_number.fill_chassis_gauge_metrics(ch_parser.chassis)
        self.gauge_license_status.fill_chassis_gauge_metrics(ch_parser.sw_license)
        self.gauge_license_capacity.fill_chassis_gauge_metrics(ch_parser.sw_license)
        self.gauge_license_exp_date.fill_chassis_gauge_metrics(ch_parser.sw_license)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_ch_name(self):
        return self._gauge_chname
    

    @property
    def gauge_fos(self):
        return self._gauge_fos
    

    @property
    def gauge_date(self):
        return self._gauge_date


    @property
    def gauge_time(self):
        return self._gauge_time


    @property
    def gauge_tz(self):
        return self._gauge_tz
    

    @property
    def gauge_ntp_active(self):
        return self._gauge_ntp_active


    @property
    def gauge_ntp_configured(self):
        return self._gauge_ntp_configured


    @property
    def gauge_vf_mode(self):
        return self._gauge_vf_mode


    @property
    def gauge_ls_number(self):
        return self._gauge_ls_number


    @property
    def gauge_license_status(self):
        return self._gauge_license_status
    

    @property
    def gauge_license_capacity(self):
        return self._gauge_license_capacity


    @property
    def gauge_license_exp_date(self):
        return self._gauge_license_exp_date