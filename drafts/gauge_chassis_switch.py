import os
import pickle
from typing import List, Union, Dict


script_dir = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts'
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


def load_object(dirname, filename):
    filpath = os.path.join(dirname, filename)
    # Reading the student object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj



storage_directory = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts\storage'

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
maps_config_prev = BrocadeMAPSParser(sw_telemetry_prev, sw_parser_prev)
fcport_params_parser_prev = BrocadeFCPortParametersParser(sw_telemetry_prev, sw_parser_prev)
sfp_media_parser_prev = BrocadeSFPMediaParser(sw_telemetry_prev, fcport_params_parser_prev)
fcport_stats_parser_prev = BrocadeFCPortStatisticsParser(sw_telemetry_prev, fcport_params_parser_prev)

# now telemetry
sw_telemetry_now = o3_g630_003_vc01_f1_a
request_status_now = BrocadeRequestStatus(sw_telemetry_now)
ch_parser_now = BrocadeChassisParser(sw_telemetry_now)
sw_parser_now = BrocadeSwitchParser(sw_telemetry_now)
fru_parser_now = BrocadeFRUParser(sw_telemetry_now)
maps_config_now = BrocadeMAPSParser(sw_telemetry_now, sw_parser_now)
fcport_params_parser_now = BrocadeFCPortParametersParser(sw_telemetry_now, sw_parser_now, fcport_params_parser_prev)
sfp_media_parser_now = BrocadeSFPMediaParser(sw_telemetry_now, fcport_params_parser_now, sfp_media_parser_prev)
fcport_stats_parser_now = BrocadeFCPortStatisticsParser(sw_telemetry_now, fcport_params_parser_now, fcport_stats_parser_prev)


def gauge_init(name: str, description: str, label_names: List[str]):

    return Gauge(name, description, replace_underscore(label_names))


def replace_underscore(keys: List[str], char='_'):
    return [key.replace('-', char) for key in keys]


def fill_chassis_level_gauge_metrics(gauge_instance: Gauge, gauge_data: Union[List[dict], Dict], label_names: List[str], metric_name: str = None):
    
    # request_status_labels = ['module', 'container', 'vf-id', 'status-code', 'status', 'error-message', 'date', 'time'] 
    if isinstance(gauge_data, list) and gauge_data:
        
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


def add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name):
    label_values = get_ordered_values(gauge_data, label_names)
    metric_value = gauge_data[metric_name] if metric_name is not None else 1
    gauge_instance.labels(*label_values).set(metric_value)


def get_ordered_values(values_dct, keys, fillna='no data'):

    values_lst = [values_dct.get(key) for key in keys]
    if fillna is not None:
        values_lst = [value if value is not None else fillna for value in values_lst]
    return values_lst


# request status gauge
request_status_label_names = ['module', 'container', 'vf-id', 'status-code', 'status', 'error-message', 'date', 'time']
gauge_request_status = gauge_init(name='request_status', description='Request status', label_names=request_status_label_names)
fill_chassis_level_gauge_metrics(gauge_request_status, gauge_data=request_status_now.request_status, label_names=request_status_label_names, metric_name='status-id')


# chassis parameters gauge
chassis_labels = ['chassis-user-friendly-name', 'chassis-wwn', 'switch-serial-number', 'model', 'product-name', 'firmware-version', 'virtual-fabrics', 'ls-number']
gauge_chassis_parameters = gauge_init(name='chassis_parameters', description='Chassis parameters', label_names=chassis_labels)
fill_chassis_level_gauge_metrics(gauge_chassis_parameters, gauge_data=ch_parser_now.chassis, label_names=chassis_labels)


# chassis datetetime gauge
datetime_labels = ['date', 'time', 'time-zone']
gauge_datetime = gauge_init(name='datetime_parameters', description='Datetime and timezone', label_names=datetime_labels)
fill_chassis_level_gauge_metrics(gauge_datetime, gauge_data=ch_parser_now.chassis, label_names=datetime_labels)


# chassis ntpserver gauge
ntp_labels = ['active-server', 'ntp-server-address']
gauge_ntp_server = gauge_init(name='ntp_server', description='NTP Address', label_names=ntp_labels)
fill_chassis_level_gauge_metrics(gauge_ntp_server, gauge_data=ch_parser_now.ntp_server, label_names=ntp_labels)


# chassis license gauge
license_labels = ['feature', 'expiration-date']
gauge_licenses = gauge_init(name='licenses', description='Switch licenses', label_names=license_labels)
fill_chassis_level_gauge_metrics(gauge_licenses, gauge_data=ch_parser_now.sw_license, label_names=license_labels, metric_name='license-status-id')


# fru fan gauge
fan_labels = ['unit-number', 'airflow-direction', 'operational-state']

gauge_fan_state = gauge_init(name='fan_state', description='Status of each fan in the system', label_names=fan_labels)
gauge_fan_speed = gauge_init(name='fan_speed', description='Speed of each fan in the system', label_names=fan_labels)

fill_chassis_level_gauge_metrics(gauge_fan_state, gauge_data=fru_parser_now.fru_fan, label_names=fan_labels, metric_name='operational-state-id')
fill_chassis_level_gauge_metrics(gauge_fan_speed, gauge_data=fru_parser_now.fru_fan, label_names=fan_labels, metric_name='speed')


# fru ps gauge
ps_labels = ['unit-number', 'operational-state']
gauge_ps_state = gauge_init(name='ps', description='Status of the switch power supplies', label_names=ps_labels)
fill_chassis_level_gauge_metrics(gauge_ps_state, gauge_data=fru_parser_now.fru_ps, label_names=ps_labels, metric_name='operational-state-id')


# fru sensor gauge
sensor_labels = ['unit-number', 'operational-state']
gauge_sensor_state = gauge_init(name='sensor_state', description='Sensor temperature state', label_names=sensor_labels)
gauge_sensor_temp = gauge_init(name='sensor_temp', description='Sensor temperature', label_names=sensor_labels)

fill_chassis_level_gauge_metrics(gauge_sensor_state, gauge_data=fru_parser_now.fru_sensor, label_names=sensor_labels, metric_name='operational-state-id')
fill_chassis_level_gauge_metrics(gauge_sensor_temp, gauge_data=fru_parser_now.fru_sensor, label_names=sensor_labels, metric_name='temperature')


# maps system resources gauge
gauge_system_resource_data = maps_config_now.system_resources.copy()
gauge_system_resource_data['chassis-wwn'] = maps_config_now.ch_wwn

system_resource_labels = ['chassis-wwn']
gauge_cpu = gauge_init(name='cpu', description='CPU usage', label_names=system_resource_labels)
gauge_flash = gauge_init(name='flash', description='Flash usage', label_names=system_resource_labels)
gauge_memory = gauge_init(name='memory', description='Memory usage', label_names=system_resource_labels)

fill_chassis_level_gauge_metrics(gauge_cpu, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='cpu-usage')
fill_chassis_level_gauge_metrics(gauge_flash, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='flash-usage')
fill_chassis_level_gauge_metrics(gauge_memory, gauge_data=gauge_system_resource_data, label_names=system_resource_labels, metric_name='memory-usage')


# maps ssp report gauge
ssp_report_labels = ['name']
gauge_ssp_report = gauge_init(name='ssp_report', description='The switch status policy report state.', label_names=ssp_report_labels)
fill_chassis_level_gauge_metrics(gauge_ssp_report, gauge_data=ch_parser_now.sw_license, label_names=license_labels, metric_name='operational-state-id')




# maps ssp report gauge

# request status gauge
# request_status_labels = ['module', 'container', 'vf-id', 'status-code', 'status', 'error-message', 'date', 'time']
# gauge_request_status = Gauge('request_status', 'Request status', replace_underscore(request_status_labels))
# for request in request_status_now.request_status:
#     request_parameters = get_ordered_values(request, request_status_labels)
#     gauge_request_status.labels(*request_parameters).set(request['status-id'])
    

# # chassis parameters gauge
# chassis_labels = ['chassis-user-friendly-name', 'chassis-wwn', 'switch-serial-number', 'model', 'product-name', 'firmware-version', 'virtual-fabrics', 'ls-number']
# gauge_chassis_parameters = Gauge('chassis_parameters', 'Chassis parameters', replace_underscore(chassis_labels))

# chassis_parameters = get_ordered_values(ch_parser_now.chassis, chassis_labels)
# gauge_chassis_parameters.labels(*chassis_parameters).set(1)


# # chassis datetetime gauge
# datetime_labels = ['date', 'time', 'time-zone']
# gauge_datetime_parameters = Gauge('datetime_parameters', 'Datetime', replace_underscore(datetime_labels))
# datetime_parameters = get_ordered_values(ch_parser_now.chassis, datetime_labels)
# gauge_datetime_parameters.labels(*datetime_parameters).set(1)


# # chassis ntpserver gauge
# ntp_labels = ['active-server', 'ntp-server-address']
# gauge_ntp_server = Gauge('ntp_server', 'NTP Address', replace_underscore(ntp_labels))
# ntp_parameters = get_ordered_values(ch_parser_now.ntp_server, ntp_labels)
# gauge_ntp_server.labels(*ntp_parameters).set(1)


# # chassis license gauge
# license_labels = ['feature', 'expiration-date']
# gauge_licenses = Gauge('licenses', 'Switch licenses', replace_underscore(license_labels))
# for lic in ch_parser_now.sw_license:
#     lic_parameters = get_ordered_values(lic, license_labels)
#     gauge_licenses.labels(*lic_parameters).set(lic['license-status-id'])


# # fru fan gauge
# fan_labels = ['unit-number', 'airflow-direction', 'speed', 'operational-state']
# gauge_fans = Gauge('fans', 'Status and speed of each fan in the system', replace_underscore(fan_labels))
# for fan in fru_parser_now.fru_fan:
#     fan_parameters = get_ordered_values(fan, fan_labels)
#     gauge_fans.labels(*fan_parameters).set(fan['operational-state-id'])










def replace_underscore_(*args, char='_'):
    
    cleared_args = [arg.replace('-', char) for arg in args]
    
    if len(cleared_args) == 1:
        return cleared_args[0]
    else:
        return cleared_args






