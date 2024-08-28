
import time
from dotenv import load_dotenv
import os
from prometheus_client import start_http_server
import copy
import database as db

from switch_telemetry_request import SwitchTelemetryRequest


from config import SWITCH_ACCESS, HTTP_SERVER_PORT



def collect_switch_metrics(sw_ipaddress):

    load_dotenv()


    if SWITCH_ACCESS[sw_ipaddress]['authentication'] == 'ldap':
        sw_username = os.getenv("SW_USERNAME_LDAP")
        sw_password = os.getenv("SW_PASSWORD_LDAP")
    elif SWITCH_ACCESS[sw_ipaddress]['authentication'] == 'local':
        sw_username = os.getenv("SW_USERNAME_LOCAL")
        sw_password = os.getenv("SW_PASSWORD_LOCAL")

    if SWITCH_ACCESS[sw_ipaddress]["secure_access"]:
        secure_access = True
    else:
        secure_access = False

    http_port_number = HTTP_SERVER_PORT[sw_ipaddress]


    # db.create_chname_ip_db_file(db.CHNAME_IP_DB_DIR, db.CHNAME_IP_DB_FILENAME)
    db.create_chname_ip_db_file()

    start = time.time()

    sw_telemetry = SwitchTelemetryRequest(sw_ipaddress, sw_username, sw_password, secure_access)

    






    chname_ip_dct = db.load_object(db.CHNAME_IP_DB_DIR, db.CHNAME_IP_DB_FILENAME)

    brocade_parser_now = BrocadeParser(sw_telemetry, chname_ip_dct)

    # db.update_chname_ip_db(chname_ip_dct, brocade_parser_now.ch_parser, db.CHNAME_IP_DB_DIR, db.CHNAME_IP_DB_FILENAME)
    db.update_chname_ip_db(chname_ip_dct, brocade_parser_now.ch_parser)

    start_http_server(http_port_number)
    dashboard = BrocadeDashboard(sw_telemetry)
    dashboard.fill_dashboard_gauge_metrics(brocade_parser_now)



    end = time.time()
    duration = end - start
    if duration < 60:
        time.sleep(60 - duration)





        
        while True:
            
            start = time.time()
            
            brocade_parser_prev = copy.deepcopy(brocade_parser_now)
            
            sw_telemetry = SwitchTelemetryRequest(sw_ipaddress, sw_username, sw_password, secure_access)

            chname_ip_dct = db.load_object(db.CHNAME_IP_DB_DIR, db.CHNAME_IP_DB_FILENAME)

            brocade_parser_now = BrocadeParser(sw_telemetry, chname_ip_dct, brocade_parser_prev)
            
            # db.update_chname_ip_db(chname_ip_dct, brocade_parser_now.ch_parser, db.CHNAME_IP_DB_DIR, db.CHNAME_IP_DB_FILENAME)
            db.update_chname_ip_db(chname_ip_dct, brocade_parser_now.ch_parser)
            dashboard.fill_dashboard_gauge_metrics(brocade_parser_now)

            end = time.time()

            duration = end - start
            if duration < 60:
                time.sleep(60 - duration)
    