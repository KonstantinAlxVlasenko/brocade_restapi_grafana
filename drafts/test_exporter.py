# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 19:59:34 2024

@author: kavlasenko
"""


from prometheus_client import start_http_server

import os
import pickle
from typing import List, Union, Dict
import time



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

from brocade_chassis_toolbar import BrocadeChassisToolbar


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


if __name__ == '__main__':
    start_http_server(13053)
    while True:
        chassis_tb = BrocadeChassisToolbar()
        chassis_tb.gauge_ch_name.fill_chassis_gauge_metrics(ch_parser_now.chassis)
        time.sleep(60)