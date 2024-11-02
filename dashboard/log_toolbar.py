from .base_gauge import BaseGauge
from .base_toolbar import BaseToolbar

from .switch_log import SwitchLog

from collection.switch_telemetry_request import SwitchTelemetryRequest

import database as db
from parser.fcport_params_parser import FCPortParametersParser
from parser.fcport_stats_parser import FCPortStatisticsParser
from parser.fru_parser import FRUParser
from parser.maps_parser import MAPSParser
from parser.sfp_media_parser import SFPMediaParser
from parser.switch_parser import SwitchParser

from typing import Dict, List, Union



class LogToolbar(BaseToolbar):
    """
    Class to create log toolbar to display changes of switch components or port status.
    Log Toolbar is a set of prometheus gauges: current value and previous value.

    Each unique port identified by 'switch-wwn', 'name', 'slot-number', 'port-number' (unit number),
    changed parameter name and log timestamp.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    

    # modified_parameter_key ='modified-parameter'
    # current_value_key = 'current-value'
    # previous_value_key = 'previous-value'

    # log_unit_keys = BaseToolbar.switch_port_keys + [modified_parameter_key, 'time-generated-hrf']

    def __init__(self, sw_telemetry: SwitchTelemetryRequest, initiator_filename: str):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
            initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
        """

        super().__init__(sw_telemetry)
        self._initiator_filename: str = initiator_filename
        # import switch log from the file if exists or create empty log
        self._switch_log = SwitchLog(self.initiator_filename)

        # log switch name gauge
        self._gauge_swname = BaseGauge(name='log_switchname', description='Switch name in the log output.', 
                                          unit_keys=LogToolbar.switch_wwn_key, parameter_key='switch-name')
        # log fabric name gauge
        self._gauge_fabricname = BaseGauge(name='log_fabricname', description='Fabric name in the log output.', 
                                              unit_keys=LogToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # log port name gauge
        # self._gauge_portname = BaseGauge(name='log_portname', description='Port name in the log output.',
        #                                      unit_keys=LogToolbar.switch_port_keys, parameter_key='port-name')
        
        self._gauge_portname = BaseGauge(name='log_portname', description='Port name in the log output.',
                                             unit_keys=LogToolbar.log_unit_keys, parameter_key='port-name')
        # log switch VF ID gauge
        self._gauge_switch_vfid = BaseGauge(name='log_switch_vfid', description='Switch virtual fabric ID in the log output.', 
                                               unit_keys=LogToolbar.switch_wwn_key, metric_key='vf-id')
        # log current value gauge
        self._gauge_current_value_str = BaseGauge(name='log_current_value_str', description='The current value of the parameter.',
                                                     unit_keys=LogToolbar.log_unit_keys, parameter_key='current-value')
        # log previous value gauge
        self._gauge_previous_value_str = BaseGauge(name='log_previous_value_str', description='The previous value of the parameter.',
                                                     unit_keys=LogToolbar.log_unit_keys, parameter_key='previous-value')
        
        self._gauge_log_id = BaseGauge(name='log_id', description='Switch log messages id.',
                                                     unit_keys=LogToolbar.log_unit_keys, metric_key='log-id')
        
        # import saved log sections to the corresponding log toolbar gauges
        self.import_saved_log()


    def import_saved_log(self) -> None:
        """Method adds saved log sections to the log toolbar gauges.
        'port-name' -> gauge_portname, 
        'current-value' -> gauge_current_value_str, 
        'previous-value'-> gauge_previous_value_str.
        
        Args:
            None

        Returns:
            None
        """

        if not self.switch_log.saved_log:
            return
        
        for section_name, section_log in self.switch_log.saved_log.items():
            match section_name:
                case 'port-name':
                    self.gauge_portname.fill_chassis_gauge_metrics(section_log)
                case 'current-value':
                    self.gauge_current_value_str.fill_chassis_gauge_metrics(section_log)
                case 'previous-value':
                    self.gauge_previous_value_str.fill_chassis_gauge_metrics(section_log)

        self._fill_log_id(self.switch_log.saved_log['current-value'])
        

    def _fill_log_id(self, current_value_section: List[Dict[str, Union[str, int, List[str]]]]):
        """Method assigns a number to each message in the current_value log.

        Args:
            current_value_section (List[Dict[str, Union[str, int, List[str]]]]): list of log entries with current value

        Returns:
            None
        """

        current_value_section_logid = current_value_section.copy()
        # add log id to each log entry in the current value log section
        for log_entry in current_value_section_logid:
            # assign next free log id
            log_entry['log-id'] = self.switch_log._last_entry_id + 1
            self.switch_log._last_entry_id += 1
        # fill log_id gauge
        self.gauge_log_id.fill_chassis_gauge_metrics(current_value_section_logid)
        

    def fill_toolbar_gauge_metrics(self, 
                                   sw_parser: SwitchParser,
                                   fcport_params_parser: FCPortParametersParser, 
                                   sfp_media_parser: SFPMediaParser, 
                                   fcport_stats_parser: FCPortStatisticsParser,
                                   fru_parser: FRUParser,
                                   maps_parser: MAPSParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sw_parser (BrocadeSwitchParser): object contains required data to fill the gauge metrics.
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.
            sfp_media_parser (BrocadeSfpMediaParser): object contains required data to fill the gauge metrics.
            fcport_stats_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
            fru_parser (BrocadeFRUParser): object contains required data to fill the gauge metrics.
            maps_parser (BrocadeMAPSParser): object contains required data to fill the gauge metrics.
            # initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
        """

        # port-name current log section
        portname_log = self.switch_log.current_log['port-name']
        # current-value current log section
        current_value_log = self.switch_log.current_log['current-value']
        # previous-value current log section
        previous_value_log = self.switch_log.current_log['previous-value']

        # fill switch related values
        self.gauge_swname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_fabricname.fill_switch_gauge_metrics(sw_parser.fc_switch)
        self.gauge_switch_vfid.fill_switch_gauge_metrics(sw_parser.fc_switch)

        # fill fc port statistics changed values 
        self._fill_fcport_stats_log(fcport_stats_parser, portname_log, current_value_log, previous_value_log)
        # fill sfp media changed values 
        self._fill_sfp_media_log(sfp_media_parser, portname_log, current_value_log, previous_value_log)
        # fill fc port parameters changed values
        self._fill_fc_port_params_log(fcport_params_parser, portname_log, current_value_log, previous_value_log)
        # fill fru parameters changed values
        self._fill_fru_log(fru_parser, sw_parser, current_value_log, previous_value_log)
        # fill system resources changed values
        self._fill_system_resources_log(maps_parser, sw_parser, current_value_log, previous_value_log)
        # fill ssp report changed log
        self._fill_ssp_report_log(maps_parser, sw_parser, current_value_log, previous_value_log)
        # number the entries in the log
        self._fill_log_id(current_value_log)
        # import current log iteration to the switch log
        self.switch_log.import_current_log()


    def _fill_fcport_stats_log(self, fcport_stats_parser: FCPortStatisticsParser, 
                               portname_log: List[Dict], current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed fc port statistics gauge metrics to the log toolbar.

        Args:
            fcport_stats_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
            portname_log (list): list to save current iteration portname dictionaries which added to the portname gauge.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """

        # status keys
        fc_port_status_changed = FCPortStatisticsParser.PORT_ERROR_STATUS_KEYS + FCPortStatisticsParser.IO_RATE_STATUS_KEYS
        # drop ok-status_errors
        counter_category_keys = [key for key in FCPortStatisticsParser.COUNTER_CATEGORY_KEYS if 'ok-status_errors' not in key]

        # portname for port with changed values in fc_port_stats_changed keys
        # self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_any=fc_port_status_changed + counter_category_keys)
        
        # port error status and io rate status change log
        for key in fc_port_status_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: LogToolbar.current_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
            self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                        add_dict={LogToolbar.modified_parameter_key: key},
                                                        storage_lst=portname_log)
        # port error deltas if errors in counter_category_keys has changed
        for key in counter_category_keys:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                 prerequisite_keys_all=[key, key + FCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + FCPortStatisticsParser.DELTA_TAG: LogToolbar.current_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key + FCPortStatisticsParser.DELTA_TAG},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, 
                                                                  prerequisite_keys_all=[key, key + FCPortStatisticsParser.DELTA_TAG],
                                                                 renamed_keys={key + FCPortStatisticsParser.DELTA_TAG + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key + FCPortStatisticsParser.DELTA_TAG},
                                                                 storage_lst=previous_value_log)
            self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                        add_dict={LogToolbar.modified_parameter_key: key + FCPortStatisticsParser.DELTA_TAG},
                                                        storage_lst=portname_log)
        # iorate details if iorate status changed
        for key in ['in-rate', 'out-rate']:
            for extension in ['-bits', '-percentage']:
                self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension: LogToolbar.current_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                                    storage_lst=current_value_log)
                self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension + '-prev': LogToolbar.previous_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                                    storage_lst=previous_value_log)
                self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                        add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                        storage_lst=portname_log)
                
        # io octets throughput change log
        for key in ['in-throughput', 'out-throughput']:
            for extension in ['-megabytes', '-percentage']:
                self.gauge_current_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension: LogToolbar.current_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                                    storage_lst=current_value_log)
                self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key + extension, key + '-status'],
                                                                    renamed_keys={key + extension + '-prev': LogToolbar.previous_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                                    storage_lst=previous_value_log)
                self.gauge_portname.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats_changed, prerequisite_keys_all=[key],
                                                            add_dict={LogToolbar.modified_parameter_key: key + extension},
                                                            storage_lst=portname_log)        


    def _fill_fc_port_params_log(self, fcport_params_parser: FCPortParametersParser, 
                                 portname_log: List[Dict], current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed fc port parameters gauge metrics to the log toolbar.

        Args:
            fcport_params_parser (BrocadeFCPortParametersParser): object contains required data to fill the gauge metrics.
            portname_log (list): list to save current iteration portname dictionaries which added to the portname gauge.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """

        # fcport parameters change log
        # portname for ports with changed port parameters

        # self.gauge_portname.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, 
        #                                             prerequisite_keys_any=FCPortParametersParser.FC_PORT_PARAMS_CHANGED)
        

        for key in FCPortParametersParser.FC_PORT_PARAMS_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key, key + '-prev'],
                                                                 renamed_keys={key: LogToolbar.current_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key, key + '-prev'],
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
            self.gauge_portname.fill_port_gauge_metrics(fcport_params_parser.fcport_params_changed, prerequisite_keys_all=[key, key + '-prev'],
                                                        add_dict={LogToolbar.modified_parameter_key: key},
                                                        storage_lst=portname_log)


    def _fill_sfp_media_log(self, sfp_media_parser: SFPMediaParser, 
                            portname_log: List[Dict], current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed sfp media gauge metrics to the log toolbar.

        Args:
            sfp_media_parser (BrocadeSFPMediaParser): object contains required data to fill the gauge metrics.
            portname_log (list): list to save current iteration portname dictionaries which added to the portname gauge.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """        

        # sfp media module change and power status change log
        sfp_media_changed = SFPMediaParser.MEDIA_RDP_CHANGED + SFPMediaParser.MEDIA_POWER_STATUS_CHANGED + SFPMediaParser.MEDIA_TEMPERATURE_STATUS_CHANGED
        # add portname for port with changed values in sfp_media_changed keys
        # self.gauge_portname.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_any=sfp_media_changed)
        for key in sfp_media_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                renamed_keys={key: LogToolbar.current_value_key}, 
                                                                add_dict={LogToolbar.modified_parameter_key: key},
                                                                storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
            self.gauge_portname.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key],
                                                        add_dict={LogToolbar.modified_parameter_key: key},
                                                        storage_lst=portname_log)
        # sfp media power change if power status has changed
        # sfp media temperature change if temperature status has changed
        sfp_media_sensor_changed = SFPMediaParser.MEDIA_POWER_CHANGED + SFPMediaParser.MEDIA_TEMPERATURE_CHANGED
        for key in sfp_media_sensor_changed:
            self.gauge_current_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                renamed_keys={key: LogToolbar.current_value_key}, 
                                                                add_dict={LogToolbar.modified_parameter_key: key},
                                                                storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
            self.gauge_portname.fill_port_gauge_metrics(sfp_media_parser.sfp_media_changed, prerequisite_keys_all=[key, key + '-status'],
                                                        add_dict={LogToolbar.modified_parameter_key: key},
                                                        storage_lst=portname_log)


    def _fill_fru_log(self, fru_parser: FRUParser, sw_parser: SwitchParser, 
                      current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed fru paramters gauge metrics to the log toolbar.

        Args:
            fru_parser (BrocadeFRUParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """

        # copy fru params to all virtual switches
        fru_fan_changed = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_fan_changed, sw_parser, component_level=True)
        fru_ps_changed = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_ps_changed, sw_parser, component_level=True)
        fru_sensor_changed = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_sensor_changed, sw_parser, component_level=True)

        # fan log
        for key in FRUParser.FAN_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_fan_changed, prerequisite_keys_all=FRUParser.FAN_CHANGED,
                                                                 renamed_keys={key: LogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_fan_changed, prerequisite_keys_all=FRUParser.FAN_CHANGED,
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
        # ps log
        for key in FRUParser.PS_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_ps_changed, prerequisite_keys_all=FRUParser.PS_CHANGED,
                                                                 renamed_keys={key: LogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_ps_changed, prerequisite_keys_all=FRUParser.PS_CHANGED,
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
        # sensor log
        for key in FRUParser.SENSOR_CHANGED:
            self.gauge_current_value_str.fill_port_gauge_metrics(fru_sensor_changed, prerequisite_keys_all=FRUParser.SENSOR_CHANGED,
                                                                 renamed_keys={key: LogToolbar.current_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_port_gauge_metrics(fru_sensor_changed, prerequisite_keys_all=FRUParser.SENSOR_CHANGED,
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key, 'unit-number': 'port-number'}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)


    def _fill_system_resources_log(self, maps_parser: MAPSParser, sw_parser: SwitchParser, 
                                   current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed system resources gauge metrics to the log toolbar.

        Args:
            maps_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """
        
        # copy system resources parameters to all virtual switches
        system_resources_changed = BaseToolbar.clone_chassis_to_vf(maps_parser.system_resources_changed, sw_parser, component_level=False)
        # changed system resource status 
        for key in MAPSParser.SYSTEM_RESOURCE_THRESHOLDS:
            key += '-status'
            self.gauge_current_value_str.fill_switch_gauge_metrics(system_resources_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key: LogToolbar.current_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_switch_gauge_metrics(system_resources_changed, prerequisite_keys_all=[key],
                                                                 renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                 add_dict={LogToolbar.modified_parameter_key: key},
                                                                 storage_lst=previous_value_log)
        # system resource metrics if it's status changed
        for key in MAPSParser.SYSTEM_RESOURCE_THRESHOLDS:
            self.gauge_current_value_str.fill_switch_gauge_metrics(system_resources_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                    renamed_keys={key: LogToolbar.current_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key},
                                                                    storage_lst=current_value_log)
            self.gauge_previous_value_str.fill_switch_gauge_metrics(system_resources_changed, prerequisite_keys_all=[key, key + '-status'],
                                                                    renamed_keys={key + '-prev': LogToolbar.previous_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: key},
                                                                    storage_lst=previous_value_log)


    def _fill_ssp_report_log(self, maps_parser: MAPSParser, sw_parser: SwitchParser, 
                             current_value_log: List[Dict], previous_value_log: List[Dict]) -> None:
        """Method to add changed ssp report gauge metrics to the log toolbar.

        Args:
            maps_parser (BrocadeFCPortStatisticsParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.
            current_value_log (list): list to save current iteration dictionaries which added to the current_value gauge.
            previous_value_log (list): list to save current iteration dictionaries which added to the previous_value gauge.

        Returns: None
        """

        ssp_report_changed = BaseToolbar.clone_chassis_to_vf(maps_parser.ssp_report_changed, sw_parser, component_level=False)
        if ssp_report_changed:
            for key in maps_parser.ssp_report_parameters:
                status_key = key + MAPSParser.STATUS_TAG
                self.gauge_current_value_str.fill_switch_gauge_metrics(ssp_report_changed, prerequisite_keys_all=[status_key],
                                                                    renamed_keys={status_key: LogToolbar.current_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: status_key},
                                                                    storage_lst=current_value_log)
                self.gauge_previous_value_str.fill_switch_gauge_metrics(ssp_report_changed, prerequisite_keys_all=[status_key],
                                                                    renamed_keys={status_key + '-prev': LogToolbar.previous_value_key}, 
                                                                    add_dict={LogToolbar.modified_parameter_key: status_key + '-prev'},
                                                                    storage_lst=previous_value_log)


    @staticmethod
    def align_dct(dct: dict, keys: list) -> dict:
        """Method to extract from dictionary required key, value pairs only.
        If key is not in dictionary None value is used in the new dictionary.
        
        Args:
            dct (dict): dictionary to extract key, values from.
            keys (list): keys to extract from the dictionary.

        Returns: dict
        """
        return {k: dct.get(k) for k in keys}


    @staticmethod
    def remove_list_duplicates(lst: list) -> list:
        """Method to remove duplicates from the list.
        
        Args:
            lst (list): initial list.

        Returns: duplicates free list
        """

        result = []
        [result.append(item) for item in lst if item not in result]
        return result


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"
    
    
    @property
    def initiator_filename(self):
        return self._initiator_filename
    

    @property
    def switch_log(self):
        return self._switch_log


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


    @property
    def gauge_log_id(self):
        return self._gauge_log_id



