import os
import pickle
from typing import List, Union, Dict


script_dir = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts'
# script_dir = r'/home/kavlasenko@dtln.local/Projects/brocade_restapi_grafana/drafts'
# Change the current working directory
os.chdir(script_dir)


from brocade_chassis_parser import BrocadeChassisParser
from brocade_fcport_params_parser import BrocadeFCPortParametersParser
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser
from brocade_sfp_media_parser import BrocadeSFPMediaParser
from brocade_base_parser import BrocadeTelemetryParser
from prometheus_client import Gauge, start_http_server
from brocade_telemetry_request_status import BrocadeRequestStatus
from brocade_maps_parser import BrocadeMAPSParser
from brocade_fru_parser import BrocadeFRUParser
from brocade_switch_parser import BrocadeSwitchParser

from brocade_chassis_toolbar import BrocadeChassisToolbar
from brocade_request_status_toolbar import BrocadeRequestStatusToolbar
from brocade_fru_toolbar import BrocadeFRUToolbar
from brocade_maps_system_toolbar import BrocadeMAPSSystemToolbar
from brocade_maps_dashboard_toolbar import BrocadeMAPSDashboardToolbar
from brocade_switch_toolbar import BrocadeSwitchToolbar
from brocade_fabricshow_toolbar import BrocadeFabricShowToolbar


def load_object(dirname, filename):
    filpath = os.path.join(dirname, filename)
    # Reading the student object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj



storage_directory = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts\storage'
# storage_directory = r'/home/kavlasenko@dtln.local/Projects/brocade_restapi_grafana/drafts/storage'

chassis_keys = ['chassis-wwn', 'switch-serial-number', 'model', 'product-name']
chassis_name_keys = chassis_keys + ['chassis-user-friendly-name']

o1_g620_009_vc5_f1 = load_object(dirname=storage_directory, filename='o1_g620_009_vc5_f1')
o3_g630_003_vc01_f1_a = load_object(dirname=storage_directory, filename='o3_g630_003_vc01_f1_a')
o3_g630_003_vc01_f1_b = load_object(dirname=storage_directory, filename='o3_g630_003_vc01_f1_b')
n3_g620_005_vc5_f1_a = load_object(dirname=storage_directory, filename='n3_g620_005_vc5_f1_a')
n3_g620_005_vc5_f1_b = load_object(dirname=storage_directory, filename='n3_g620_005_vc5_f1_b')
ost_6510_07_f1_a = load_object(dirname=storage_directory, filename='ost_6510_07_f1_a')
ost_6510_07_f1_b = load_object(dirname=storage_directory, filename='ost_6510_07_f1_b')
o3_g620_107_vc01_f1_a = load_object(dirname=storage_directory, filename='o3_g620_107_vc01_f1_a')
o3_g620_107_vc01_f1_b = load_object(dirname=storage_directory, filename='o3_g620_107_vc01_f1_b')
o1_g620_003_vc5_f1 = load_object(dirname=storage_directory, filename='o1_g620_003_vc5_f1')



# gauge_db_rule = Gauge('dashboard_rule', 'Triggered rules list for the last 7 days', ['category', 'name', 'triggered_count', 'time_stamp', 'repetition_count', 'element', 'value'])



# previous telemetry
sw_telemetry_prev = o3_g630_003_vc01_f1_a
request_status_prev = BrocadeRequestStatus(sw_telemetry_prev)
ch_parser_prev = BrocadeChassisParser(sw_telemetry_prev)
sw_parser_prev = BrocadeSwitchParser(sw_telemetry_prev)
fru_parser_prev = BrocadeFRUParser(sw_telemetry_prev)
maps_parser_prev = BrocadeMAPSParser(sw_telemetry_prev, sw_parser_prev)
fcport_params_parser_prev = BrocadeFCPortParametersParser(sw_telemetry_prev, sw_parser_prev)
sfp_media_parser_prev = BrocadeSFPMediaParser(sw_telemetry_prev, fcport_params_parser_prev)
fcport_stats_parser_prev = BrocadeFCPortStatisticsParser(sw_telemetry_prev, fcport_params_parser_prev)

# now telemetry
sw_telemetry_now = o3_g630_003_vc01_f1_a
request_status_now = BrocadeRequestStatus(sw_telemetry_now)
ch_parser_now = BrocadeChassisParser(sw_telemetry_now)
sw_parser_now = BrocadeSwitchParser(sw_telemetry_now)
fru_parser_now = BrocadeFRUParser(sw_telemetry_now)
maps_parser_now = BrocadeMAPSParser(sw_telemetry_now, sw_parser_now)
fcport_params_parser_now = BrocadeFCPortParametersParser(sw_telemetry_now, sw_parser_now, fcport_params_parser_prev)
sfp_media_parser_now = BrocadeSFPMediaParser(sw_telemetry_now, fcport_params_parser_now, sfp_media_parser_prev)
fcport_stats_parser_now = BrocadeFCPortStatisticsParser(sw_telemetry_now, fcport_params_parser_now, fcport_stats_parser_prev)


for sw_port_params in fcport_params_parser_now.fcport_params.values():
    for port_params in sw_port_params.values():
        if port_params['is-enabled-state']:
            print(port_params['port-number'])


# sw_parser_now.get_switch_details(vf_id=2)

def gauge_init(name: str, description: str, label_names: List[str]):

    return Gauge(name, description, replace_underscore(label_names))


def replace_underscore(keys: List[str], char='_'):
    return [key.replace('-', char) for key in keys]


def fill_chassis_level_gauge_metrics(gauge_instance: Gauge, gauge_data: Union[List[dict], Dict], label_names: List[str], metric_name: str=None):
    
    # request_status_labels = ['module', 'container', 'vf-id', 'status-code', 'status', 'error-message', 'date', 'time']
    
    if not gauge_data:
        return
    
    if isinstance(gauge_data, list):
        
        for gauge_data_current in gauge_data:
            add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
            # label_values = get_ordered_values(gauge_data_instance, label_names)
            # metric_value = gauge_data_instance[metric_label] if metric_label is not None else 1
            # metric_gauge.labels(*label_values).set(metric_value)
    elif isinstance(gauge_data, dict):
        add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name)
        # label_values = get_ordered_values(gauge_data_instance, label_names)
        # metric_value = gauge_data_instance[metric_label] if metric_label is not None else 1
        # metric_gauge.labels(*label_values).set(metric_value)
        
        
def fill_switch_level_gauge_metrics(gauge_instance: Gauge, gauge_data: Dict[int, Dict], 
                                    label_names: List[str], metric_name: str=None, reverse=False):
    
    if not gauge_data:
        return
    
    for gauge_data_switch in gauge_data.values():
    
        if not gauge_data_switch:
            continue
    
        if isinstance(gauge_data_switch, list):
            gauge_data_switch_ordered = gauge_data_switch[::-1] if reverse else gauge_data_switch
                
            for gauge_data_current in gauge_data_switch_ordered:
                add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
        elif isinstance(gauge_data_switch, dict):
            add_gauge_metric(gauge_instance, gauge_data_switch, label_names, metric_name)
    
    # for gauge_data_current in gauge_data.values():
    #     add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
        
        
    
    # # request_status_labels = ['module', 'container', 'vf-id', 'status-code', 'status', 'error-message', 'date', 'time'] 
    # if isinstance(gauge_data, list) and gauge_data:
        
    #     for gauge_data_current in gauge_data:
    #         add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
    #         # label_values = get_ordered_values(gauge_data_instance, label_names)
    #         # metric_value = gauge_data_instance[metric_label] if metric_label is not None else 1
    #         # metric_gauge.labels(*label_values).set(metric_value)
    # elif isinstance(gauge_data, dict) and gauge_data:
    #     add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name) 


def add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name):
    label_values = get_ordered_values(gauge_data, label_names)
    metric_value = gauge_data[metric_name] if metric_name is not None else 1
    if metric_value is not None:
        gauge_instance.labels(*label_values).set(metric_value)


def get_ordered_values(values_dct, keys, fillna='no data'):

    values_lst = [values_dct.get(key) for key in keys]
    if fillna is not None:
        values_lst = [value if value is not None else fillna for value in values_lst]
    return values_lst


# # request status gauge
# request_status_container_labels = ['module', 'container', 'vf-id']
# # TELEMETRY_STATUS_ID = {'OK': 1, 'WARNING': 2, 'FAIL': 3}
# gauge_request_status_id = gauge_init(name='request_status_id', description='Request status id', label_names=request_status_container_labels)


# fill_chassis_level_gauge_metrics(gauge_request_status_id, gauge_data=request_status_now.request_status, label_names=request_status_container_labels, metric_name='status-id')
# # HTTP Status Code, 200-OK, 400-Bad Request etc
# gauge_request_status_code = gauge_init(name='request_status_code', description='HTTP Request status code', label_names=request_status_container_labels)
# fill_chassis_level_gauge_metrics(gauge_request_status_code, gauge_data=request_status_now.request_status, label_names=request_status_container_labels, metric_name='status-code')

# # request status error message
# request_status_error_labels = request_status_container_labels + ['error-message']
# gauge_request_status_error = gauge_init(name='request_status_error', description='HTTP Request status error', label_names=request_status_error_labels)
# fill_chassis_level_gauge_metrics(gauge_request_status_error, gauge_data=request_status_now.request_status, label_names=request_status_error_labels)

# # request status date
# request_status_date_labels = request_status_container_labels + ['date']
# gauge_request_status_date = gauge_init(name='request_status_date', description='HTTP Request status date', label_names=request_status_date_labels)
# fill_chassis_level_gauge_metrics(gauge_request_status_date, gauge_data=request_status_now.request_status, label_names=request_status_date_labels)

# # request status time
# request_status_time_labels = request_status_container_labels + ['time']
# gauge_request_status_time = gauge_init(name='request_status_time', description='HTTP Request status time', label_names=request_status_time_labels)
# fill_chassis_level_gauge_metrics(gauge_request_status_time, gauge_data=request_status_now.request_status, label_names=request_status_time_labels)


request_status_tb = BrocadeRequestStatusToolbar(sw_telemetry_now)
request_status_tb.gauge_rs_id.fill_chassis_gauge_metrics(request_status_now.request_status)
request_status_tb.gauge_rs_code.fill_chassis_gauge_metrics(request_status_now.request_status)
request_status_tb.gauge_rs_error.fill_chassis_gauge_metrics(request_status_now.request_status)
request_status_tb.gauge_rs_date.fill_chassis_gauge_metrics(request_status_now.request_status)
request_status_tb.gauge_rs_time.fill_chassis_gauge_metrics(request_status_now.request_status)



# # chassis parameters gauge
# chassis_labels = ['chassis-wwn', 'switch-serial-number', 'model', 'product-name']
# # chassis name gauge
# chassis_name_labels = chassis_labels + ['chassis-user-friendly-name']
# gauge_chassis_name =  gauge_init(name='chassis_name', description='Chassis name', label_names=chassis_name_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_name, gauge_data=ch_parser_now.chassis, label_names=chassis_name_labels)

# # chassis fos version
# chassis_fos_labels = chassis_labels + ['firmware-version']
# gauge_chassis_fos =  gauge_init(name='chassis_fos', description='Chassis firmware version', label_names=chassis_fos_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_fos, gauge_data=ch_parser_now.chassis, label_names=chassis_fos_labels)

# # chassis ls number
# gauge_chassis_ls_number =  gauge_init(name='chassis_ls_number', description='Chassis logical switch number', label_names=chassis_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_ls_number, gauge_data=ch_parser_now.chassis, label_names=chassis_labels, metric_name='ls-number')

# # chassis vf mode
# # -1 - 'Not Applicable',  1 - 'Enabled', 0 - 'Disabled'
# gauge_chassis_vf_mode =  gauge_init(name='chassis_vf_mode', description='Chassis virtual fabrics mode', label_names=chassis_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_vf_mode, gauge_data=ch_parser_now.chassis, label_names=chassis_labels, metric_name='virtual-fabrics-id')


# # chassis date gauge
# chassis_date_labels = chassis_labels + ['date']
# gauge_chassis_date =  gauge_init(name='chassis_date', description='Chassis date', label_names=chassis_date_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_ls_number, gauge_data=ch_parser_now.chassis, label_names=chassis_date_labels)

# # chassis time gauge
# chassis_time_labels = chassis_labels + ['time']
# gauge_chassis_time =  gauge_init(name='chassis_time', description='Chassis time', label_names=chassis_time_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_time, gauge_data=ch_parser_now.chassis, label_names=chassis_time_labels)

# # chassis timezone gauge
# chassis_tz_labels = chassis_labels + ['time-zone']
# gauge_chassis_tz =  gauge_init(name='chassis_tz', description='Chassis timezone', label_names=chassis_tz_labels)
# fill_chassis_level_gauge_metrics(gauge_chassis_tz, gauge_data=ch_parser_now.chassis, label_names=chassis_tz_labels)


# # chassis ntpserver gauge
# chassis_wwn_label = ['chassis-wwn']
# # chassis active ntp
# chassis_ntp_active_labels = chassis_wwn_label + ['active-server']
# gauge_ntp_active = gauge_init(name='ntp_server', description='Active NTP Address', label_names=chassis_ntp_active_labels)
# fill_chassis_level_gauge_metrics(gauge_ntp_active, gauge_data=ch_parser_now.ntp_server, label_names=chassis_ntp_active_labels)

# # chassis configured ntp
# chassis_ntp_configured_labels = chassis_wwn_label + ['ntp-server-address']
# gauge_ntp_configured = gauge_init(name='ntp_list', description='Configured NTP Address(es)', label_names=chassis_ntp_configured_labels)
# fill_chassis_level_gauge_metrics(gauge_ntp_configured, gauge_data=ch_parser_now.ntp_server, label_names=chassis_ntp_configured_labels)




# # chassis license gauge
# # License status:
# # 0 - No expiration date
# # 1 - Expiration date has not arrived
# # 2 - Expiration date has arrived
# license_labels = ['chassis-wwn', 'feature', 'expiration-date']
# gauge_licenses = gauge_init(name='licenses', description='Switch licenses', label_names=license_labels)
# fill_chassis_level_gauge_metrics(gauge_licenses, gauge_data=ch_parser_now.sw_license, label_names=license_labels, metric_name='license-status-id')


chassis_tb = BrocadeChassisToolbar(sw_telemetry_now)

chassis_tb.gauge_ch_name.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_fos.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_date.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_time.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_tz.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_ntp_active.fill_chassis_gauge_metrics(ch_parser_now.ntp_server)
chassis_tb.gauge_ntp_configured.fill_chassis_gauge_metrics(ch_parser_now.ntp_server)
chassis_tb.gauge_vf_mode.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_ls_number.fill_chassis_gauge_metrics(ch_parser_now.chassis)
chassis_tb.gauge_licenses.fill_chassis_gauge_metrics(ch_parser_now.sw_license)




# # fru fan gauge
# fan_labels = ['unit-number', 'airflow-direction']
# # FAN_STATE = {'absent': 0, 'ok': 1, 'below minimum': 2, 'above maximum': 3, 'unknown': 4, 'not ok': 5, 'faulty': 6}
# gauge_fan_state = gauge_init(name='fan_state', description='Status of each fan in the system', label_names=fan_labels)
# fill_chassis_level_gauge_metrics(gauge_fan_state, gauge_data=fru_parser_now.fru_fan, label_names=fan_labels, metric_name='operational-state-id')
# # fan speed
# gauge_fan_speed = gauge_init(name='fan_speed', description='Speed of each fan in the system', label_names=fan_labels)
# fill_chassis_level_gauge_metrics(gauge_fan_speed, gauge_data=fru_parser_now.fru_fan, label_names=fan_labels, metric_name='speed')


# # fru ps gauge
# # PS_STATE = {'absent': 0, 'ok': 1, 'predicting failure': 2, 'unknown': 3, 'try reseating unit': 4, 'faulty': 5}
# ps_labels = ['unit-number']
# gauge_ps_state = gauge_init(name='ps', description='Status of the switch power supplies', label_names=ps_labels)
# fill_chassis_level_gauge_metrics(gauge_ps_state, gauge_data=fru_parser_now.fru_ps, label_names=ps_labels, metric_name='operational-state-id')


# # fru sensor gauge
# # SENSOR_STATE = {'absent': 0, 'ok': 1}
# sensor_labels = ['unit-number']
# gauge_sensor_state = gauge_init(name='sensor_state', description='Sensor temperature state', label_names=sensor_labels)
# fill_chassis_level_gauge_metrics(gauge_sensor_state, gauge_data=fru_parser_now.fru_sensor, label_names=sensor_labels, metric_name='operational-state-id')
# # sensor temperature
# gauge_sensor_temp = gauge_init(name='sensor_temp', description='Sensor temperature', label_names=sensor_labels)
# fill_chassis_level_gauge_metrics(gauge_sensor_temp, gauge_data=fru_parser_now.fru_sensor, label_names=sensor_labels, metric_name='temperature')


fru_tb = BrocadeFRUToolbar(sw_telemetry_now)

fru_tb.gauge_fan_state.fill_chassis_gauge_metrics(fru_parser_now.fru_fan)
fru_tb.gauge_fan_speed.fill_chassis_gauge_metrics(fru_parser_now.fru_fan)
fru_tb.gauge_ps_state.fill_chassis_gauge_metrics(fru_parser_now.fru_ps)
fru_tb.gauge_sensor_state.fill_chassis_gauge_metrics(fru_parser_now.fru_sensor)
fru_tb.gauge_sensor_temp.fill_chassis_gauge_metrics(fru_parser_now.fru_sensor)


# # maps system resources gauge
# gauge_system_resource_data = maps_config_now.system_resources.copy()
# gauge_system_resource_data['chassis-wwn'] = maps_config_now.ch_wwn
# system_resource_labels = ['chassis-wwn']

# # cpu
# gauge_cpu = gauge_init(name='cpu', description='CPU usage', label_names=system_resource_labels)
# fill_chassis_level_gauge_metrics(gauge_cpu, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='cpu-usage')
# # flash
# gauge_flash = gauge_init(name='flash', description='Flash usage', label_names=system_resource_labels)
# fill_chassis_level_gauge_metrics(gauge_flash, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='flash-usage')
# # memory
# gauge_memory = gauge_init(name='memory', description='Memory usage', label_names=system_resource_labels)
# fill_chassis_level_gauge_metrics(gauge_memory, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='memory-usage')


# # maps ssp report gauge
# # SSP_STATE = {'healthy': 1, 'unknown': 2, 'marginal': 3, 'down': 4}
# ssp_report_labels = ['name']
# gauge_ssp_report = gauge_init(name='ssp_report', description='The switch status policy report state.', label_names=ssp_report_labels)
# fill_chassis_level_gauge_metrics(gauge_ssp_report, gauge_data=maps_config_now.ssp_report, label_names=ssp_report_labels, metric_name='operational-state-id')


# # maps config
# maps_config_labels = ['switch-name', 'switch-wwn', 'vf-id', 'maps-policy', 'maps-actions']
# gauge_maps_config = gauge_init(name='maps_config', description='Active MAPS policy and actions', label_names=maps_config_labels)
# fill_switch_level_gauge_metrics(gauge_maps_config, gauge_data=maps_config_now.maps_config, label_names=maps_config_labels)




# # maps dashboard
# maps_dashboard_labels = ['switch-name', 'switch-wwn', 'vf-id', 'category', 'name', 'time-stamp', 'object-element', 'object-value']
# # category triggered-count
# gauge_mapsdb_triggered_count = gauge_init(name='mapsdb_triggered_count', description='The number of times the rule was triggered for the category', 
#                                           label_names=maps_dashboard_labels)
# fill_switch_level_gauge_metrics(gauge_mapsdb_triggered_count, gauge_data=maps_config_now.dashboard_rule, 
#                                 label_names=maps_dashboard_labels, metric_name='triggered-count', reverse=True)
# # rule repetition-count
# gauge_mapsdb_repetition_count = gauge_init(name='mapsdb_repetition_count', description='The number of times a rule was triggered', 
#                                            label_names=maps_dashboard_labels)
# fill_switch_level_gauge_metrics(gauge_mapsdb_repetition_count, gauge_data=maps_config_now.dashboard_rule, 
#                                 label_names=maps_dashboard_labels, metric_name='repetition-count', reverse=True)
# # mapsdb rule severity
# # Severity level:
# # 0 - no event triggired or retrieved
# # 1 - information that event condition is cleared 
# # 2 - warning that event condition detected
# gauge_mapsdb_rule_severity = gauge_init(name='mapsdb_rule_severity', description='MAPS rule severity', label_names=maps_dashboard_labels)
# fill_switch_level_gauge_metrics(gauge_mapsdb_rule_severity, gauge_data=maps_config_now.dashboard_rule, 
#                                 label_names=maps_dashboard_labels, metric_name='severity', reverse=True)




maps_system_tb = BrocadeMAPSSystemToolbar(sw_telemetry_now)
maps_system_tb.gauge_sys_resource_chname.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
maps_system_tb.gauge_cpu_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
maps_system_tb.gauge_flash_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
maps_system_tb.gauge_memory_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)

maps_system_tb.gauge_ssp_report_chname.fill_chassis_gauge_metrics(maps_parser_now.ssp_report)
maps_system_tb.gauge_ssp_report.fill_chassis_gauge_metrics(maps_parser_now.ssp_report)

maps_dashboard_tb = BrocadeMAPSDashboardToolbar(sw_telemetry_now)
maps_dashboard_tb.gauge_mapsconfig_swname.fill_switch_gauge_metrics(maps_parser_now.maps_config)
maps_dashboard_tb.gauge_mapsconfig_vfid.fill_switch_gauge_metrics(maps_parser_now.maps_config)
maps_dashboard_tb.gauge_maps_policy.fill_switch_gauge_metrics(maps_parser_now.maps_config)
maps_dashboard_tb.gauge_maps_actions.fill_switch_gauge_metrics(maps_parser_now.maps_config)

maps_dashboard_tb.gauge_db_swname.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
maps_dashboard_tb.gauge_db_vfid.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
maps_dashboard_tb.gauge_db_repetition_count.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
maps_dashboard_tb.gauge_db_triggered_count.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
maps_dashboard_tb.gauge_db_severity.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)


# # switch name
# switch_name_labels = ['switch-wwn', 'switch-name']
# gauge_switch_name = gauge_init(name='switch_name', description='Switch name', label_names=switch_name_labels)
# fill_switch_level_gauge_metrics(gauge_switch_name, gauge_data=sw_parser_now.fc_switch, label_names=switch_name_labels)

# # switch ip address
# switch_ip_labels = ['switch-wwn', 'ip-address']
# gauge_switch_ip = gauge_init(name='switch_ip', description='Switch IP address', label_names=switch_ip_labels)
# fill_switch_level_gauge_metrics(gauge_switch_ip, gauge_data=sw_parser_now.fc_switch, label_names=switch_ip_labels)

# # switch fabric name
# switch_fabric_name_labels = ['switch-wwn', 'fabric-user-friendly-name']
# gauge_switch_fabric_name = gauge_init(name='switch_fabric_name', description='Switch fabric name', label_names=switch_fabric_name_labels)
# fill_switch_level_gauge_metrics(gauge_switch_fabric_name, gauge_data=sw_parser_now.fc_switch, label_names=switch_fabric_name_labels)

# # switch uptime
# switch_uptime_labels = ['switch-wwn', 'up-time-hrf']
# gauge_switch_uptime = gauge_init(name='switch_uptime', description='Switch uptime', label_names=switch_uptime_labels)
# fill_switch_level_gauge_metrics(gauge_switch_uptime, gauge_data=sw_parser_now.fc_switch, label_names=switch_uptime_labels)


# # switch
# switch_labels = ['switch-wwn']

# # switch state
# # 0 - Undefined, 2 - Online. 3 = Offline. 7 - Testing
# gauge_switch_state = gauge_init(name='switch_state', description='The current state of the switch.', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_state, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='operational-status')

# # switch role
# # -1 - Disabled, 0 - Subordinate, 1 - Principal
# gauge_switch_role = gauge_init(name='switch_role', description='Switch role: Principal, Subordinate, or Disabled.', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_role, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='switch-role-id')

# # switch mode
# # 0, 1 - Native, 2 - 'Access Gateway'
# gauge_switch_mode = gauge_init(name='switch_mode', description='Switch operation mode: Access Gateway (if AG is enabled).', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_mode, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='ag-mode')

# # switch did
# gauge_switch_did = gauge_init(name='switch_domain_id', description='Switch domain ID', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_did, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='domain-id')

# # switch fid
# gauge_switch_fid = gauge_init(name='switch_fabric_id', description='Switch fabric ID', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_fid, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='fabric-id')

# # switch port quantity
# gauge_switch_port_quantity = gauge_init(name='switch_port_quantity', description='Switch port member quantity', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_port_quantity, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='port-member-quantity')

# # switch vf id
# gauge_switch_vfid = gauge_init(name='switch_vfid', description='Switch virtual fabric ID', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_switch_vfid, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='vf-id')



# # base switch status
# # 0 = Disabled. 1 = Enabled
# gauge_base_switch_status = gauge_init(name='base_switch_status', description='Base switch status', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_base_switch_status, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='base-switch-enabled')

# # default switch status
# # 0 = Disabled. 1 = Enabled
# gauge_default_switch_status = gauge_init(name='default_switch_status', description='Deafault switch status', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_default_switch_status, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='default-switch-status')

# # logical isl status
# # 0 = Disabled. 1 = Enabled
# gauge_logical_isl_status = gauge_init(name='logical_isl_status', description='Logical isl status', label_names=switch_labels)
# fill_switch_level_gauge_metrics(gauge_logical_isl_status, gauge_data=sw_parser_now.fc_switch, label_names=switch_labels, metric_name='logical-isl-enabled')


switch_tb = BrocadeSwitchToolbar(sw_telemetry_now)
switch_tb.gauge_swname.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_ip.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_fabric_name.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_uptime.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_state.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_mode.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_role.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_did.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_fid.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_vfid.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_switch_port_quantity.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_base_switch_status.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_default_switch_status.fill_switch_gauge_metrics(sw_parser_now.fc_switch)
switch_tb.gauge_logical_isl_status.fill_switch_gauge_metrics(sw_parser_now.fc_switch)



# # fabricshow
# switch_wwn_label = ['switch-wwn']

# # principal label
# # 1 - ">", 0 - "-"
# gauge_fabricshow_principal_label = gauge_init(name='fabricshow_principal_label', description='Fabricshow principal switch label >', label_names=switch_wwn_label)
# fill_switch_level_gauge_metrics(gauge_fabricshow_principal_label, gauge_data=sw_parser_now.fabric, label_names=switch_wwn_label, metric_name='principal')

# # fabricshow switch did
# gauge_fabricshow_switch_did = gauge_init(name='fabricshow_switch_did', description='Fabricshow switch domain ID', label_names=switch_wwn_label)
# fill_switch_level_gauge_metrics(gauge_fabricshow_switch_did, gauge_data=sw_parser_now.fabric, label_names=switch_wwn_label, metric_name='domain-id')

# # fabricshow switch fid
# gauge_fabricshow_switch_fid = gauge_init(name='fabricshow_switch_fid', description='Fabricshow switch fabric ID', label_names=switch_wwn_label)
# fill_switch_level_gauge_metrics(gauge_fabricshow_switch_fid, gauge_data=sw_parser_now.fabric, label_names=switch_wwn_label, metric_name='fabric-id')

# # fabricshow path-count
# gauge_fabricshow_path_count = gauge_init(name='fabricshow_path_count', description='Fabricshow path count', label_names=switch_wwn_label)
# fill_switch_level_gauge_metrics(gauge_fabricshow_path_count, gauge_data=sw_parser_now.fabric, label_names=switch_wwn_label, metric_name='path-count')

# # fabricshow fabric name
# fabricshow_fabricname_labels = ['switch-wwn', 'fabric-user-friendly-name']
# gauge_fabricshow_fabricname = gauge_init(name='fabricshow_fabricname', description='Fabric name in the fabricshow output', label_names=fabricshow_fabricname_labels)
# fill_switch_level_gauge_metrics(gauge_fabricshow_fabricname, gauge_data=sw_parser_now.fabric, label_names=fabricshow_fabricname_labels)

# # fabricshow fos
# fabricshow_fos_labels = ['switch-wwn', 'firmware-version']
# gauge_fabricshow_fos = gauge_init(name='fabricshow_fos', description='Firmware version in the fabricshow output', label_names=fabricshow_fos_labels)
# fill_switch_level_gauge_metrics(gauge_fabricshow_fos, gauge_data=sw_parser_now.fabric, label_names=fabricshow_fos_labels)

# # fabricshow ip-address
# fabricshow_ip_labels = ['switch-wwn', 'ip-address']
# gauge_fabricshow_ip = gauge_init(name='fabricshow_ip', description='Switch ip-address in the fabricshow output', label_names=fabricshow_ip_labels)
# fill_switch_level_gauge_metrics(gauge_fabricshow_ip, gauge_data=sw_parser_now.fabric, label_names=fabricshow_ip_labels)

# # fabricshow switch name
# fabricshow_switchname_labels = ['switch-wwn', 'switch-user-friendly-name']
# gauge_fabricshow_switchname = gauge_init(name='fabricshow_switchname', description='Switch name in the fabricshow output', label_names=fabricshow_switchname_labels)
# fill_switch_level_gauge_metrics(gauge_fabricshow_switchname, gauge_data=sw_parser_now.fabric, label_names=fabricshow_switchname_labels)



fabricshow_tb = BrocadeFabricShowToolbar(sw_telemetry_now)
fabricshow_tb.gauge_swname.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_fabricname.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_switch_ip.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_switch_fos.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_principal_label.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_switch_did.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_switch_fid.fill_switch_gauge_metrics(sw_parser_now.fabric)
fabricshow_tb.gauge_path_count.fill_switch_gauge_metrics(sw_parser_now.fabric)












def replace_underscore_(*args, char='_'):
    
    cleared_args = [arg.replace('-', char) for arg in args]
    
    if len(cleared_args) == 1:
        return cleared_args[0]
    else:
        return cleared_args






