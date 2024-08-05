from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_fcport_params_parser import BrocadeFCPortParametersParser
from brocade_sfp_media_parser import BrocadeSFPMediaParser
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser


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
    log_unit_keys = BrocadeToolbar.switch_port_keys + [modified_parameter_key, 'time-generated-hrf']

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # sfp media switch name gauge
        self._gauge_swname = BrocadeGauge(name='log_switchname', description='Switch name in the SFP media output.', 
                                          unit_keys=BrocadeLogToolbar.switch_wwn_key, parameter_key='switch-name')
        # sfp media fabric name gauge
        self._gauge_fabricname = BrocadeGauge(name='log_fabricname', description='Fabric name in the SFP media output.', 
                                              unit_keys=BrocadeLogToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # sfp media port name gauge
        self._gauge_portname = BrocadeGauge(name='log_portname', description='Port name in the SFP media output.',
                                             unit_keys=BrocadeLogToolbar.switch_port_keys, parameter_key='port-name')  
        # sfp media switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='log_switch_vfid', description='Switch virtual fabric ID in the SFP media output.', 
                                               unit_keys=BrocadeLogToolbar.switch_wwn_key, metric_key='vf-id')
        
        self._gauge_current_value_str = BrocadeGauge(name='log_current_value_str', description='The current value of the parameter.',
                                                     unit_keys=BrocadeLogToolbar.log_unit_keys, parameter_key='current-value')
        self._gauge_previous_value_str = BrocadeGauge(name='log_previous_value_str', description='The previous value of the parameter.',
                                                     unit_keys=BrocadeLogToolbar.log_unit_keys, parameter_key='previous-value')
        


    def fill_toolbar_gauge_metrics(self, 
                                   sw_parser: BrocadeSwitchParser,
                                   fcport_params_parser: BrocadeFCPortParametersParser, 
                                   sfp_media_parser:BrocadeSFPMediaParser, 
                                   fcport_stats_parser: BrocadeFCPortStatisticsParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.
            sfp_media_parser (BrocadeSfpMediaParser): object contains required data to fill the gauge metrics.
            fcport_stats_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
        """
        

        self.gauge_swname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_fabricname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_switch_vfid.fill_switch_gauge_metrics(sw_parser.fc_switch)

        # fcport stats change log
        # fc_port_stats_changed = [key for key in BrocadeFCPortStatisticsParser.FC_PORT_STATS_CHANGED if 'ok-status_errors' not in key]
        fc_port_stats_changed = BrocadeFCPortStatisticsParser.PORT_ERROR_STATUS_KEYS + BrocadeFCPortStatisticsParser.IO_RATE_STATUS_KEYS
        # drop ok-status_errors
        counter_category_keys = [key for key in BrocadeFCPortStatisticsParser.COUNTER_CATEGORY_KEYS if 'ok-status_errors' not in key]

        # portname for port with changed values in fc_port_stats_changed keys
        self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_any=fc_port_stats_changed + counter_category_keys)
        
        # port error status, errors list and io rate status change log
        for key in fc_port_stats_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: 'current-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': 'previous-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            
        # port error deltas if errors in counter_category_keys has changed
        for key in counter_category_keys:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                 prerequisite_keys_all=[key, key + BrocadeFCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + BrocadeFCPortStatisticsParser.DELTA_TAG: 'current-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key + BrocadeFCPortStatisticsParser.DELTA_TAG})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                  prerequisite_keys_all=[key, key + BrocadeFCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + BrocadeFCPortStatisticsParser.DELTA_TAG + '-prev': 'previous-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key + BrocadeFCPortStatisticsParser.DELTA_TAG})

        # iorate details if iorate status changed
        for key in ['in-rate', 'out-rate']:
            for extension in ['-bits', '-percentage']:
                self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension: 'current-value'}, 
                                                                    modified_dict={BrocadeLogToolbar.modified_parameter_key: key + extension})
                self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension + '-prev': 'previous-value'}, 
                                                                    modified_dict={BrocadeLogToolbar.modified_parameter_key: key + extension})

        # sfp media module change and power status change log
        sfp_media_changed = BrocadeSFPMediaParser.MEDIA_RDP_CHANGED + BrocadeSFPMediaParser.MEDIA_POWER_STATUS_CHANGED
         # add portname for port with changed values in sfp_media_changed keys
        self.gauge_portname.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_any=sfp_media_changed)
        for key in sfp_media_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                renamed_keys={key: 'current-value'}, 
                                                                modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': 'previous-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
        
        # sfp media power change if power status has changed
        for key in BrocadeSFPMediaParser.MEDIA_POWER_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                renamed_keys={key: 'current-value'}, 
                                                                modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                 renamed_keys={key + '-prev': 'previous-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            
        
        # fcport parameters change log
        # add portname for ports with changed port parameters
        self.gauge_portname.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, 
                                                    prerequisite_keys_any=BrocadeFCPortParametersParser.FC_PORT_PARAMS_CHANGED)
        for key in BrocadeFCPortParametersParser.FC_PORT_PARAMS_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: 'current-value'}, 
                                                                 modified_dict={BrocadeLogToolbar.modified_parameter_key: key})
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': 'previous-value'}, 
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

