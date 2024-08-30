
import copy
import os
import time
from ipaddress import ip_address
from parser import BrocadeParser
from typing import Tuple

from dotenv import load_dotenv
from prometheus_client import start_http_server

import database as db
from config import HTTP_SERVER_PORT, SWITCH_ACCESS
from dashboard import BrocadeDashboard
from switch_telemetry_request import SwitchTelemetryRequest


def collect_switch_metrics(sw_ipaddress: ip_address) -> None:
    """Function connects to the switch, retrieves the telemetry through rest api,
    and fills the dashboard with the collected metrics.
    Dashboard is a set of proometheus Gauges. Time interval between two collections is 1 minute.

    Args:
        sw_ipaddress (ip_address): switch ip address.
    """

    # get switch credentials from .env file
    sw_username, sw_password = get_credentials(sw_ipaddress)
    # get switch access protocol (http or https) from the configuration file
    secure_access = SWITCH_ACCESS[sw_ipaddress]["secure_access"]
    # get http server port number from the configuration file
    http_port_number = HTTP_SERVER_PORT[sw_ipaddress]

    # create empty nameserver and save it in the database
    db.create_nameserver()
    # start http server on the specified port
    start_http_server(http_port_number)

    # start timer to measure execution time
    start = time.time()
    # get telemetry from the switch through rest api
    sw_telemetry = SwitchTelemetryRequest(sw_ipaddress, sw_username, sw_password, secure_access)
    # load current nameserver from the database
    nameserver_dct = db.load_object(db.NS_DIR, db.NS_FILENAME)
    # parse retrieved telemetry to export to the dashboard
    brocade_parser_now = BrocadeParser(sw_telemetry, nameserver_dct)
    # update namserver with data from the parser if needed
    db.update_nameserver(nameserver_dct, brocade_parser_now.ch_parser)

    # create switch dashboard (set of toolbars which are set of gauges)
    dashboard = BrocadeDashboard(sw_telemetry)
    # fill dashboard gauges with labels and metrics from the parser
    dashboard.fill_dashboard_gauge_metrics(brocade_parser_now)

    # stop timer
    end = time.time()
    duration = end - start
    # wait till 1 minute is expired
    if duration < 60:
        time.sleep(60 - duration)
        
        # collect metrics in infinite loop
        while True:
            # reset timer
            start = time.time()
            # save previous parsed telemmetry
            brocade_parser_prev = copy.deepcopy(brocade_parser_now)
            # collect new telemetry
            sw_telemetry = SwitchTelemetryRequest(sw_ipaddress, sw_username, sw_password, secure_access)
            # load current nameserver from the database
            nameserver_dct = db.load_object(db.NS_DIR, db.NS_FILENAME)
            # parse retrieved telemetry to export to the dashboard
            brocade_parser_now = BrocadeParser(sw_telemetry, nameserver_dct, brocade_parser_prev)
            # update namserver with data from the parser if needed
            db.update_nameserver(nameserver_dct, brocade_parser_now.ch_parser)
            # fill dashboard gauges with labels and metrics from the parser
            dashboard.fill_dashboard_gauge_metrics(brocade_parser_now)
            
            # stop timer
            end = time.time()
            # wait till 1 minute is expired
            duration = end - start
            if duration < 60:
                time.sleep(60 - duration)
    

def get_credentials(sw_ipaddress: ip_address) -> Tuple[str]:
    """Function retrieves switch credentials from .env file.

    Args:
        sw_ipaddress (ip_address): switch ip address.

    Returns:
        Tuple[str]: switch username and password.
    """

    load_dotenv()

    if SWITCH_ACCESS[sw_ipaddress]['authentication'] == 'ldap':
        sw_username = os.getenv("SW_USERNAME_LDAP")
        sw_password = os.getenv("SW_PASSWORD_LDAP")
    elif SWITCH_ACCESS[sw_ipaddress]['authentication'] == 'local':
        sw_username = os.getenv("SW_USERNAME_LOCAL")
        sw_password = os.getenv("SW_PASSWORD_LOCAL")

    return sw_username, sw_password