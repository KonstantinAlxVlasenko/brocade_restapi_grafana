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
from brocade_switch_toolbar import BrocadeSwitchToolbar
from brocade_fabricshow_toolbar import BrocadeFabricShowToolbar
from brocade_fcport_params_toolbar import BrocadeFCPortParamsToolbar
from brocade_sfp_media_toolbar import BrocadeSFPMediaToolbar
from brocade_fcport_stats_toolbar import BrocadeFCPortStatsToolbar
from brocade_log_toolbar import BrocadeLogToolbar


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



lr_out_2 = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-link-resets']
ofl_in_2 = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-offline-sequences']

ofl_out_2 = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-offline-sequences']
lr_in_2 = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-link-resets']

# print(f'{lr_out_2=}, {ofl_in_2=}\n{lr_in_2=}, {ofl_out_2=}')



o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-link-resets'] = lr_out_2
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-offline-sequences'] = ofl_in_2

o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-offline-sequences'] = ofl_out_2 +10
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-link-resets'] = lr_in_2 + 40

# high severity
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['pcs-block-errors'] = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['pcs-block-errors'] + 60
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['class3-in-discards'] = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['class3-in-discards'] + 20
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['class3-out-discards'] = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['class3-out-discards'] + 20

# medium severity
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['f-rjt-frames'] = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['f-rjt-frames'] + 35
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['invalid-transmission-words'] = o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][1]['invalid-transmission-words'] + 35


# print(o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-link-resets'])
# print(o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-offline-sequences'])

# print(o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['out-offline-sequences'])
# print(o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-link-resets'])


# io rate
o3_g630_003_vc01_f1_b.fc_statistics[-1]['Response']['fibrechannel-statistics'][0]['in-rate'] = 3_875_000_000

o3_g630_003_vc01_f1_b.fc_interface[-1]['Response']['fibrechannel'][0]['user-friendly-name'] = 'FAKE REFS'
# o3_g630_003_vc01_f1_b.fc_interface[-1]['Response']['fibrechannel'][0]['physical-state'] = 'offline'
o3_g630_003_vc01_f1_b.fc_interface[-1]['Response']['fibrechannel'][0]['speed'] = 32000000000
o3_g630_003_vc01_f1_b.fc_interface[-1]['Response']['fibrechannel'][0]['neighbor'] = None
o3_g630_003_vc01_f1_b.fc_interface[-1]['Response']['fibrechannel'][0]['neighbor-node-wwn'] = None


o3_g630_003_vc01_f1_b.media_rdp[-1]['Response']['media-rdp'][0]['serial-number'] = 'HOO252209160183'
o3_g630_003_vc01_f1_b.media_rdp[-1]['Response']['media-rdp'][0]['tx-power'] = 130
o3_g630_003_vc01_f1_b.media_rdp[-1]['Response']['media-rdp'][1]['part-number'] = None


# fan spped
o3_g630_003_vc01_f1_b.fru_fan['Response']['fan'][0]['speed'] = 12000
o3_g630_003_vc01_f1_b.fru_fan['Response']['fan'][0]['operational-state'] = 'above maximum'

# cpu_usage
o3_g630_003_vc01_f1_b.system_resources['Response']['system-resources']['cpu-usage'] = 80
o3_g630_003_vc01_f1_b.system_resources['Response']['system-resources']['memory-usage'] = 95

# ssp report
o3_g630_003_vc01_f1_b.ssp_report['Response']['switch-status-policy-report']['power-supply-health'] = 'down'
o3_g630_003_vc01_f1_b.ssp_report['Response']['switch-status-policy-report']['fan-health'] = 'marginal'


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

# print('now----------------------')

# now telemetry
sw_telemetry_now = o3_g630_003_vc01_f1_b
request_status_now = BrocadeRequestStatus(sw_telemetry_now)
ch_parser_now = BrocadeChassisParser(sw_telemetry_now)
sw_parser_now = BrocadeSwitchParser(sw_telemetry_now)
fru_parser_now = BrocadeFRUParser(sw_telemetry_now, fru_parser_prev)
maps_parser_now = BrocadeMAPSParser(sw_telemetry_now, sw_parser_now, maps_parser_prev)
fcport_params_parser_now = BrocadeFCPortParametersParser(sw_telemetry_now, sw_parser_now, fcport_params_parser_prev)
sfp_media_parser_now = BrocadeSFPMediaParser(sw_telemetry_now, fcport_params_parser_now, sfp_media_parser_prev)
fcport_stats_parser_now = BrocadeFCPortStatisticsParser(sw_telemetry_now, fcport_params_parser_now, fcport_stats_parser_prev)


# request_status_tb = BrocadeRequestStatusToolbar(sw_telemetry_now)
# chassis_tb = BrocadeChassisToolbar(sw_telemetry_now)
# fru_tb = BrocadeFRUToolbar(sw_telemetry_now)
# maps_system_tb = BrocadeMAPSSystemToolbar(sw_telemetry_now)
# maps_dashboard_tb = BrocadeMAPSDashboardToolbar(sw_telemetry_now)
# switch_tb = BrocadeSwitchToolbar(sw_telemetry_now)
fabricshow_tb = BrocadeFabricShowToolbar(sw_telemetry_now)
# fcport_params_tb = BrocadeFCPortParamsToolbar(sw_telemetry_now)
# sfp_media_tb = BrocadeSFPMediaToolbar(sw_telemetry_now)
# fcport_stats_tb = BrocadeFCPortStatsToolbar(sw_telemetry_now)
# log_tb = BrocadeLogToolbar(sw_telemetry_now)


if __name__ == '__main__':
    start_http_server(13053)
    
    while True:
        
        # print('request_status')
        # request_status_tb.fill_toolbar_gauge_metrics(request_status_now)
        
        # print('chassis')
        # chassis_tb.fill_toolbar_gauge_metrics(ch_parser_now, sw_parser_now)

        # print('fru')
        # fru_tb.fill_toolbar_gauge_metrics(fru_parser_now, sw_parser_now)

        # print('maps system resources', 'maps system health')
        # maps_system_tb.fill_toolbar_gauge_metrics(maps_parser_now, sw_parser_now)

        # print('maps policy, actions','maps dashboard')
        # maps_dashboard_tb.fill_toolbar_gauge_metrics(maps_parser_now)

        # print('switch')
        # switch_tb.fill_toolbar_gauge_metrics(sw_parser_now)
        
        print('fabrichsow')
        fabricshow_tb.fill_toolbar_gauge_metrics(sw_parser_now)

        # print('fcport parameters')
        # fcport_params_tb.fill_toolbar_gauge_metrics(fcport_params_parser_now)

        # print('sfp media')
        # sfp_media_tb.fill_toolbar_gauge_metrics(sfp_media_parser_now)

        # print('fcport_stats')
        # fcport_stats_tb.fill_toolbar_gauge_metrics(fcport_stats_parser_now)

        # print('log')
        # log_tb.fill_toolbar_gauge_metrics(sw_parser_now, fcport_params_parser_now, sfp_media_parser_now, 
        #                                   fcport_stats_parser_now, fru_parser_now, maps_parser_now)

        time.sleep(5)
    
    
    



