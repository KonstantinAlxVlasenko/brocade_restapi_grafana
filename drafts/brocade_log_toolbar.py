from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_fcport_params_parser import BrocadeFCPortParametersParser
from brocade_sfp_media_parser import BrocadeSFPMediaParser
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser
from brocade_fru_parser import BrocadeFRUParser


class BrocadeLogToolbar(BrocadeToolbar):
    """
    Class to create sfp parameters and metrics toolbar.
    SFP Media Toolbar is a set of prometheus gauges:
    sfp vendor, part number, serial number, temperature, poweron time, laser type, speed capabilities,
    wavelength, rx and tx power in uWatts and dBm, rx and tx power status.

    Each unique port identified by 'switch-wwn', 'name', 'slot-number', 'port-number'.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    modified_parameter_key ='modified-parameter'
    current_value_key = 'current-value'
    previous_value_key = 'previous-value'

    log_unit_keys = BrocadeToolbar.switch_port_keys + [modified_parameter_key, 'time-generated-hrf']

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # log switch name gauge
        self._gauge_swname = BrocadeGauge(name='log_switchname', description='Switch name in the log output.', 
                                          unit_keys=BrocadeLogToolbar.switch_wwn_key, parameter_key='switch-name')
        # log fabric name gauge
        self._gauge_fabricname = BrocadeGauge(name='log_fabricname', description='Fabric name in the log output.', 
                                              unit_keys=BrocadeLogToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # log port name gauge
        self._gauge_portname = BrocadeGauge(name='log_portname', description='Port name in the log output.',
                                             unit_keys=BrocadeLogToolbar.switch_port_keys, parameter_key='port-name')  
        # log switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='log_switch_vfid', description='Switch virtual fabric ID in the log output.', 
                                               unit_keys=BrocadeLogToolbar.switch_wwn_key, metric_key='vf-id')
        # log current value gauge
        self._gauge_current_value_str = BrocadeGauge(name='log_current_value_str', description='The current value of the parameter.',
                                                     unit_keys=BrocadeLogToolbar.log_unit_keys, parameter_key='current-value')
        # log previous value gauge
        self._gauge_previous_value_str = BrocadeGauge(name='log_previous_value_str', description='The previous value of the parameter.',
                                                     unit_keys=BrocadeLogToolbar.log_unit_keys, parameter_key='previous-value')
        

    def fill_toolbar_gauge_metrics(self, 
                                   sw_parser: BrocadeSwitchParser,
                                   fcport_params_parser: BrocadeFCPortParametersParser, 
                                   sfp_media_parser:BrocadeSFPMediaParser, 
                                   fcport_stats_parser: BrocadeFCPortStatisticsParser,
                                   fru_parser: BrocadeFRUParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.
            sfp_media_parser (BrocadeSfpMediaParser): object contains required data to fill the gauge metrics.
            fcport_stats_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
        """
        
        # fill switch related values
        self.gauge_swname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_fabricname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_switch_vfid.fill_switch_gauge_metrics(sw_parser.fc_switch)

        # fill fc port statistics changed values 
        self._fill_fcport_stats_log(fcport_stats_parser)
        # fill sfp media changed values 
        self._fill_sfp_media_log(sfp_media_parser)
        # fill fc port parameters changed values
        self._fill_fc_port_params_log(fcport_params_parser)
        # fill fru paramters chaged values
        self._fill_fru_log(fru_parser, sw_parser)



    def _fill_fcport_stats_log(self, fcport_stats_parser: BrocadeFCPortStatisticsParser) -> None:
        """Method to add changed fc port statistics gauge metrics to the log toolbar.

        Args:
            fcport_stats_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.

        Returns: None
        """

        # status keys
        fc_port_status_changed = BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS + BrocadeFCPortStatisticsParser.IO_RATE_STATUS_KEYS
        # drop ok-status_errors
        counter_category_keys = [key for key in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS if 'ok-status_errors' not in key]

        # portname for port with changed values in fc_port_stats_changed keys
        self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_any=fc_port_status_changed + counter_category_keys)
        
        # port error status and io rate status change log
        for key in fc_port_status_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: BrocadeLogToolbar.current_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
        # port error deltas if errors in counter_category_keys has changed
        for key in counter_category_keys:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                 prerequisite_keys_all=[key, key + BrocadeFCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + BrocadeFCPortStatisticsParser.DELTA_TAG: BrocadeLogToolbar.current_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key + BrocadeFCPortStatisticsParser.DELTA_TAG})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                  prerequisite_keys_all=[key, key + BrocadeFCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + BrocadeFCPortStatisticsParser.DELTA_TAG + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key + BrocadeFCPortStatisticsParser.DELTA_TAG})
        # iorate details if iorate status changed
        for key in ['in-rate', 'out-rate']:
            for extension in ['-bits', '-percentage']:
                self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension: BrocadeLogToolbar.current_value_key}, 
                                                                    modified_dict={BrocadeLogToolbar.modified_parameter_key: key + extension})
                self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                    modified_dict={BrocadeLogToolbar.modified_parameter_key: key + extension})


    def _fill_fc_port_params_log(self, fcport_params_parser: BrocadeFCPortParametersParser) -> None:
        """Method to add changed fc port parameters gauge metrics to the log toolbar.

        Args:
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.

        Returns: None
        """

        # fcport parameters change log
        # portname for ports with changed port parameters
        self.gauge_portname.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, 
                                                    prerequisite_keys_any=BrocadeFCPortParametersParser.FC_PORT_PARAMS_CHANGED)
        for key in BrocadeFCPortParametersParser.FC_PORT_PARAMS_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: BrocadeLogToolbar.current_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})


    def _fill_sfp_media_log(self, sfp_media_parser:BrocadeSFPMediaParser) -> None:
        """Method to add changed sfp media gauge metrics to the log toolbar.

        Args:
            sfp_media_parser (BrocadeSFPMediaParser): object contains required data to fill the gauge metrics.

        Returns: None
        """        

        # sfp media module change and power status change log
        sfp_media_changed = BrocadeSFPMediaParser.MEDIA_RDP_CHANGED + BrocadeSFPMediaParser.MEDIA_POWER_STATUS_CHANGED
         # add portname for port with changed values in sfp_media_changed keys
        self.gauge_portname.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_any=sfp_media_changed)
        for key in sfp_media_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                renamed_keys={key: BrocadeLogToolbar.current_value_key}, 
                                                                modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
        # sfp media power change if power status has changed
        for key in BrocadeSFPMediaParser.MEDIA_POWER_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                renamed_keys={key: BrocadeLogToolbar.current_value_key}, 
                                                                modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})


    def _fill_fru_log(self, fru_parser: BrocadeFRUParser, sw_parser: BrocadeSwitchParser) -> None:
        """Method to add changed fru paramters gauge metrics to the log toolbar.

        Args:
            fru_parser (BrocadeFRUParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.

        Returns: None
        """

        # copy fru params to all virtual switches
        fru_fan_changed = BrocadeToolbar.vf_multiplier(fru_parser.fru_fan_changed, sw_parser, component_level=True)
        fru_ps_changed = BrocadeToolbar.vf_multiplier(fru_parser.fru_ps_changed, sw_parser, component_level=True)
        fru_sensor_changed = BrocadeToolbar.vf_multiplier(fru_parser.fru_sensor_changed, sw_parser, component_level=True)

        # fan log
        for key in BrocadeFRUParser.FAN_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_fan_changed, prerequisite_keys_all=BrocadeFRUParser.FAN_CHANGED,
                                                                 renamed_keys={key: BrocadeLogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_fan_changed, prerequisite_keys_all=BrocadeFRUParser.FAN_CHANGED,
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
        # ps log
        for key in BrocadeFRUParser.PS_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_ps_changed, prerequisite_keys_all=BrocadeFRUParser.PS_CHANGED,
                                                                 renamed_keys={key: BrocadeLogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_ps_changed, prerequisite_keys_all=BrocadeFRUParser.PS_CHANGED,
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
        # sensor log
        for key in BrocadeFRUParser.SENSOR_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_sensor_changed, prerequisite_keys_all=BrocadeFRUParser.SENSOR_CHANGED,
                                                                 renamed_keys={key: BrocadeLogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_sensor_changed, prerequisite_keys_all=BrocadeFRUParser.SENSOR_CHANGED,
                                                                 renamed_keys={key + '-prev': BrocadeLogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})



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
    def gauge_current_value_str(self):
        return self._gauge_current_value_str


    @property
    def gauge_previous_value_str(self):
        return self._gauge_previous_value_str

