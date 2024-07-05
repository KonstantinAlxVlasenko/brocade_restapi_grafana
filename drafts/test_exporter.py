# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 19:59:34 2024

@author: kavlasenko
"""


from prometheus_client import start_http_server, CollectorRegistry

import os
import pickle
from typing import List, Union, Dict
import time



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


def load_object(dirname, filename):
    filpath = os.path.join(dirname, filename)
    # Reading the student object back from the file
    with open(filpath, "rb") as file:
        loaded_obj = pickle.load(file)
    print(f'Object successfully loaded from "{filename}"')
    return loaded_obj



storage_directory = r'E:\Documents\05.PYTHON\Projects\brocade_restapi_grafana\drafts\storage'
# storage_directory = r'/home/kavlasenko@dtln.local/Projects/brocade_restapi_grafana/drafts/storage'

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


# def gauge_init(name: str, description: str, label_names: List[str]):

#     return Gauge(name, description, replace_underscore(label_names), registry=CollectorRegistry())


# def fill_chassis_level_gauge_metrics(gauge_instance: Gauge, gauge_data: Union[List[dict], Dict], label_names: List[str], metric_name: str=None):
        
#     if not gauge_data:
#         return
    
#     if isinstance(gauge_data, list):
#         for gauge_data_current in gauge_data:
#             add_gauge_metric(gauge_instance, gauge_data_current, label_names, metric_name)
#     elif isinstance(gauge_data, dict):
#         add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name)


# def replace_underscore(keys: List[str], char='_'):
#     return [key.replace('-', char) for key in keys]



        
        
# def add_gauge_metric(gauge_instance, gauge_data, label_names, metric_name):
#     label_values = get_ordered_values(gauge_data, label_names)
#     metric_value = gauge_data[metric_name] if metric_name is not None else 1
#     if metric_value is not None:
#         gauge_instance.labels(*label_values).set(metric_value)


# def get_ordered_values(values_dct, keys, fillna='no data'):

#     values_lst = [values_dct.get(key) for key in keys]
#     if fillna is not None:
#         values_lst = [value if value is not None else fillna for value in values_lst]
#     return values_lst


chassis_tb = BrocadeChassisToolbar(sw_telemetry_now)
request_status_tb = BrocadeRequestStatusToolbar(sw_telemetry_now)
fru_tb = BrocadeFRUToolbar(sw_telemetry_now)
maps_system_tb = BrocadeMAPSSystemToolbar(sw_telemetry_now)
maps_dashboard_tb = BrocadeMAPSDashboardToolbar(sw_telemetry_now)


if __name__ == '__main__':
    start_http_server(13053)
    
    while True:
        
        print('request_status')
        request_status_tb.gauge_rs_id.fill_chassis_gauge_metrics(request_status_now.request_status)
        request_status_tb.gauge_rs_code.fill_chassis_gauge_metrics(request_status_now.request_status)
        request_status_tb.gauge_rs_error.fill_chassis_gauge_metrics(request_status_now.request_status)
        request_status_tb.gauge_rs_date.fill_chassis_gauge_metrics(request_status_now.request_status)
        request_status_tb.gauge_rs_time.fill_chassis_gauge_metrics(request_status_now.request_status)
        
        print('chassis')
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

        print('fru')
        fru_tb.gauge_fan_state.fill_chassis_gauge_metrics(fru_parser_now.fru_fan)
        fru_tb.gauge_fan_speed.fill_chassis_gauge_metrics(fru_parser_now.fru_fan)
        fru_tb.gauge_ps_state.fill_chassis_gauge_metrics(fru_parser_now.fru_ps)
        fru_tb.gauge_sensor_state.fill_chassis_gauge_metrics(fru_parser_now.fru_sensor)
        fru_tb.gauge_sensor_temp.fill_chassis_gauge_metrics(fru_parser_now.fru_sensor)

        print('maps system resources')
        maps_system_tb.gauge_sys_resource_chname.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
        maps_system_tb.gauge_cpu_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
        maps_system_tb.gauge_flash_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)
        maps_system_tb.gauge_memory_usage.fill_chassis_gauge_metrics(maps_parser_now.system_resources)

        print('maps system health')
        maps_system_tb.gauge_ssp_report_chname.fill_chassis_gauge_metrics(maps_parser_now.ssp_report)
        maps_system_tb.gauge_ssp_report.fill_chassis_gauge_metrics(maps_parser_now.ssp_report)

        print('maps policy, actions')
        maps_dashboard_tb.gauge_mapsconfig_swname.fill_switch_gauge_metrics(maps_parser_now.maps_config)
        maps_dashboard_tb.gauge_mapsconfig_vfid.fill_switch_gauge_metrics(maps_parser_now.maps_config)
        maps_dashboard_tb.gauge_maps_policy.fill_switch_gauge_metrics(maps_parser_now.maps_config)
        maps_dashboard_tb.gauge_maps_actions.fill_switch_gauge_metrics(maps_parser_now.maps_config)
        
        print('maps dashboard')
        maps_dashboard_tb.gauge_db_swname.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
        maps_dashboard_tb.gauge_db_vfid.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
        maps_dashboard_tb.gauge_db_repetition_count.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
        maps_dashboard_tb.gauge_db_triggered_count.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)
        maps_dashboard_tb.gauge_db_severity.fill_switch_gauge_metrics(maps_parser_now.dashboard_rule)

        time.sleep(5)
    
    
    



