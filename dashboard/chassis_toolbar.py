from parser import ChassisParser, SwitchParser

from base_gauge import BaseGauge
from base_toolbar import BaseToolbar

from switch_telemetry_request import SwitchTelemetryRequest


class ChassisToolbar(BaseToolbar):
    """
    Class to create Chassis toolbar.
    Chassis Toolbar is a set of prometheus gauges:
    chassis_name, fos version, date, time, timezone, ntp_active, ntp_configured, vf_mode, ls_number, licenses installed.
    Each unique chassis identified by chassis wwn, serial number, model and product name.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    license_keys = ['chassis-wwn', 'switch-wwn', 'name', 'feature']

    VF_MODE_STATUS_ID = {-1: 'Not Applicable',  1: 'Enabled', 0: 'Disabled'}

    LICENSE_STATUS_ID = {1: 'OK', 
                         2: 'Temporary', 
                         3: 'Expired'}


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # chassis name gauge
        self._gauge_chname = BaseGauge(name='chassis_name', description='Chassis name', 
                                          unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='chassis-user-friendly-name')
        # switch serial numbaer gauge
        self._gauge_sn = BaseGauge(name='chassis_sn', description='Chassis serial number', 
                                          unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='switch-serial-number')
        # switct type gauge
        self._gauge_model = BaseGauge(name='switch_type', description='Switch type', 
                                          unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='model')
        # switch product name gauge
        self._gauge_product_name = BaseGauge(name='switch_product_name', description='Switch product name', 
                                          unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='product-name')
        # switch name
        self._gauge_swname = BaseGauge(name='chassis_swname', description='Chassis switch name', 
                                                    unit_keys=ChassisToolbar.switch_wwn_key, parameter_key='switch-name')
        # fabric name
        self._gauge_fabricname = BaseGauge(name='chassis_fabric_name', description='Chassis fabric name', 
                                                    unit_keys=ChassisToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_vfid = BaseGauge(name='chassis_vfid', description='Chassis VF ids', 
                                                    unit_keys=ChassisToolbar.switch_wwn_key, parameter_key='vf-id')
        # fos version gauge
        self._gauge_fos =  BaseGauge(name='chassis_fos', description='Chassis firmware version', 
                                        unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='firmware-version')
        # date gauge
        self._gauge_date =  BaseGauge(name='chassis_date', description='Chassis date', 
                                         unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='date')
        # time gauge
        self._gauge_time =  BaseGauge(name='chassis_time', description='Chassis time', 
                                         unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='time')
        # timezone gauge
        self._gauge_tz =  BaseGauge(name='chassis_tz', description='Chassis timezone', 
                                       unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='time-zone')

        # vf mode gauge
        # -1 - 'Not Applicable',  1 - 'Enabled', 0 - 'Disabled'
        vf_mode_description = f'Chassis virtual fabrics mode {ChassisToolbar.VF_MODE_STATUS_ID}.'
        self._gauge_vf_mode =  BaseGauge(name='chassis_vf_mode', description=vf_mode_description, 
                                            unit_keys=ChassisToolbar.chassis_switch_wwn_keys, metric_key='virtual-fabrics-mode-id')
        # ls quantity gauge
        self._gauge_ls_number =  BaseGauge(name='chassis_ls_number', description='Chassis logical switch qunatity', 
                                              unit_keys=ChassisToolbar.chassis_switch_wwn_keys, metric_key='ls-number')
        
        # active ntp
        self._gauge_ntp_active = BaseGauge(name='ntp_server', description='Active NTP Address', 
                                              unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='active-server')
        # configured ntp
        self._gauge_ntp_configured = BaseGauge(name='ntp_list', description='Configured NTP Address(es)', 
                                                  unit_keys=ChassisToolbar.chassis_switch_wwn_keys, parameter_key='ntp-server-address')
        # license status gauge
        # 1 - No expiration date
        # 2 - Expiration date has not arrived
        # 3 - Expiration date has arrived
        license_status_description = f'Switch licenses status {ChassisToolbar.LICENSE_STATUS_ID}.'
        self._gauge_license_status = BaseGauge(name='license_status', description=license_status_description, 
                                            unit_keys=ChassisToolbar.license_keys, metric_key='license-status-id')
        # license capacity gauge
        self._gauge_license_capacity = BaseGauge(name='license_capacity', description='POD license capacity', 
                                            unit_keys=ChassisToolbar.license_keys, metric_key='capacity')        
        # license exp date gauge
        self._gauge_license_exp_date = BaseGauge(name='license_exp_date', description='License expiration date', 
                                            unit_keys=ChassisToolbar.license_keys, parameter_key='expiration-date')


    def fill_toolbar_gauge_metrics(self, ch_parser: ChassisParser , sw_parser: SwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            ch_parser (ChassisParser): object contains required data to fill the gauge metrics.
            sw_parser (SwitchParser): object contains vf details.
        """

        chassis_gauges_lst = [self.gauge_chname, self.gauge_sn, self.gauge_model, self.gauge_product_name, 
                              self.gauge_swname, self.gauge_fabricname, self.gauge_vfid, self.gauge_fos, 
                              self.gauge_date, self.gauge_time, self.gauge_tz, self.gauge_vf_mode, self.gauge_ls_number]
        chassis = BaseToolbar.clone_chassis_to_vf(ch_parser.chassis, sw_parser, component_level=False)
        for gauge in chassis_gauges_lst:
            gauge.fill_switch_gauge_metrics(chassis)
        

        ntp_server = BaseToolbar.clone_chassis_to_vf(ch_parser.ntp_server, sw_parser, component_level=False)
        self.gauge_ntp_active.fill_switch_gauge_metrics(ntp_server)
        self.gauge_ntp_configured.fill_switch_gauge_metrics(ntp_server)

        sw_license = BaseToolbar.clone_chassis_to_vf(ch_parser.sw_license, sw_parser)
        self.gauge_license_status.fill_switch_gauge_metrics(sw_license)
        self.gauge_license_capacity.fill_switch_gauge_metrics(sw_license)
        self.gauge_license_exp_date.fill_switch_gauge_metrics(sw_license)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_chname(self):
        return self._gauge_chname
    

    @property
    def gauge_sn(self):
        return self._gauge_sn
    

    @property
    def gauge_model(self):
        return self._gauge_model
    

    @property
    def gauge_product_name(self):
        return self._gauge_product_name


    @property
    def gauge_swname(self):
        return self._gauge_swname
    

    @property
    def gauge_fabricname(self):
        return self._gauge_fabricname
    

    @property
    def gauge_vfid(self):
        return self._gauge_vfid


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