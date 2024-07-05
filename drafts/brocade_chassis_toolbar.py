from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry

class BrocadeChassisToolbar:
    """
    Class to create Chassis toolbar.
    Chassis Toolbar is a set of prometheus gauges:
    chassis_name, fos version, date, time, timezone, ntp_active, ntp_configured, vf_mode, ls_number, licenses installed.
    Each unique chassis identified by chassis wwn, serial number, model and product name.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    chassis_keys = ['chassis-wwn', 'switch-serial-number', 'model', 'product-name']
    chassis_name_keys = chassis_keys + ['chassis-user-friendly-name']
    fos_keys = chassis_keys + ['firmware-version']
    chassis_date_keys = chassis_keys + ['date']
    chassis_time_keys = chassis_keys + ['time']
    tz_keys = chassis_keys + ['time-zone']
    ntp_active_keys = ['chassis-wwn', 'active-server']
    ntp_configured_keys = ['chassis-wwn', 'ntp-server-address']
    license_keys = ['chassis-wwn', 'feature', 'expiration-date']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

        # chassis name gauge
        self._gauge_ch_name = BrocadeGauge(name='chassis_name', description='Chassis name', 
                                           label_keys=BrocadeChassisToolbar.chassis_name_keys)
        # fos version gauge
        self._gauge_fos =  BrocadeGauge(name='chassis_fos', description='Chassis firmware version', 
                                        label_keys=BrocadeChassisToolbar.fos_keys)
        # date gauge
        self._gauge_date =  BrocadeGauge(name='chassis_date', description='Chassis date', 
                                         label_keys=BrocadeChassisToolbar.chassis_date_keys)
        # time gauge
        self._gauge_time =  BrocadeGauge(name='chassis_time', description='Chassis time', 
                                         label_keys=BrocadeChassisToolbar.chassis_time_keys)
        # timezone gauge
        self._gauge_tz =  BrocadeGauge(name='chassis_tz', description='Chassis timezone', 
                                       label_keys=BrocadeChassisToolbar.tz_keys)
        # active ntp
        self._gauge_ntp_active = BrocadeGauge(name='ntp_server', description='Active NTP Address', 
                                              label_keys=BrocadeChassisToolbar.ntp_active_keys)
        # configured ntp
        self._gauge_ntp_configured = BrocadeGauge(name='ntp_list', description='Configured NTP Address(es)', 
                                                  label_keys=BrocadeChassisToolbar.ntp_configured_keys)

        # vf mode gauge
        # -1 - 'Not Applicable',  1 - 'Enabled', 0 - 'Disabled'
        self._gauge_vf_mode =  BrocadeGauge(name='chassis_vf_mode', description='Chassis virtual fabrics mode', 
                                            label_keys=BrocadeChassisToolbar.chassis_keys, metric_key='virtual-fabrics-id')
        # ls quantity gauge
        self._gauge_ls_number =  BrocadeGauge(name='chassis_ls_number', description='Chassis logical switch qunatity', 
                                              label_keys=BrocadeChassisToolbar.chassis_keys, metric_key='ls-number')
        # license starus gauge
        # 0 - No expiration date
        # 1 - Expiration date has not arrived
        # 2 - Expiration date has arrived
        self._gauge_licenses = BrocadeGauge(name='licenses', description='Switch licenses', 
                                            label_keys=BrocadeChassisToolbar.license_keys, metric_key='license-status-id')

    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def gauge_ch_name(self):
        return self._gauge_ch_name
    

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
    def gauge_licenses(self):
        return self._gauge_licenses



        # # chassis name gauge
        # fill_chassis_level_gauge_metrics(gauge_chassis_name, gauge_data=ch_parser_now.chassis, label_names=chassis_name_labels)

        # # chassis fos version
        # fill_chassis_level_gauge_metrics(gauge_chassis_fos, gauge_data=ch_parser_now.chassis, label_names=fos_labels)

        # # chassis ls number
        # fill_chassis_level_gauge_metrics(gauge_chassis_ls_number, gauge_data=ch_parser_now.chassis, label_names=chassis_labels, metric_name='ls-number')

        # # chassis vf mode
        # # -1 - 'Not Applicable',  1 - 'Enabled', 0 - 'Disabled'
        # fill_chassis_level_gauge_metrics(gauge_chassis_vf_mode, gauge_data=ch_parser_now.chassis, label_names=chassis_labels, metric_name='virtual-fabrics-id')


        # # chassis date gauge
        # fill_chassis_level_gauge_metrics(gauge_chassis_ls_number, gauge_data=ch_parser_now.chassis, label_names=chassis_date_labels)

        # # chassis time gauge
        # fill_chassis_level_gauge_metrics(gauge_chassis_time, gauge_data=ch_parser_now.chassis, label_names=chassis_time_labels)

        # # chassis timezone gauge
        # fill_chassis_level_gauge_metrics(gauge_chassis_tz, gauge_data=ch_parser_now.chassis, label_names=tz_labels)


        # # chassis active ntp
        # fill_chassis_level_gauge_metrics(gauge_ntp_active, gauge_data=ch_parser_now.ntp_server, label_names=ntp_active_labels)

        # # chassis configured ntp
        # fill_chassis_level_gauge_metrics(gauge_ntp_configured, gauge_data=ch_parser_now.ntp_server, label_names=ntp_configured_labels)




        # # chassis license gauge
        # # License status:
        # # 0 - No expiration date
        # # 1 - Expiration date has not arrived
        # # 2 - Expiration date has arrived
        # fill_chassis_level_gauge_metrics(gauge_licenses, gauge_data=ch_parser_now.sw_license, label_names=license_labels, metric_name='license-status-id')




       
        # self._gauge_ch_name
        # self._gauge_fos
        # self._gauge_date
        # self._gauge_time 
        # self._gauge_tz
        # self._gauge_ntp_active
        # self._gauge_ntp_configured
        # self._gauge_vf_mode
        # self._gauge_ls_number
        # self._gauge_licenses