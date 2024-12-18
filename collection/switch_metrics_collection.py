
import copy
import os
import time
from ipaddress import ip_address
from typing import Tuple, Union

from parser.brocade_parser import BrocadeParser
from parser.request_status_parser import RequestStatusParser

from dotenv import load_dotenv
from prometheus_client import start_http_server

import database as db
from config import HTTP_SERVER_PORT, SWITCH_ACCESS
from dashboard.brocade_dashboard import BrocadeDashboard
from collection.switch_telemetry_request import SwitchTelemetryRequest

TIME_INTERVAL = 60
REQUEST_STATUS_TAG = '-request'
BROCADE_PARSER_TAG = '-parser'
TELEMETRY_TAG = '-telemetry'


def collect_switch_metrics(sw_ipaddress: ip_address, initiator_filename: str) -> None:
    """Function connects to the switch, retrieves the telemetry through rest api,
    and fills the dashboard with the collected metrics.
    Dashboard is a set of proometheus Gauges. Time interval between two collections is 1 minute.

    Args:
        sw_ipaddress (ip_address): switch ip address.
        initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
    """
    
    # get http server port number from the configuration file
    http_port_number = HTTP_SERVER_PORT[sw_ipaddress]

    # if not found create empty nameserver and save it in the database
    db.create_nameserver()
    # create archive folder in the database if not exist
    db.create_directory_if_not_exists(db.ARCHIVE_DIR)
    # create switch log directory in the database if not exist
    db.create_directory_if_not_exists(db.SWITCH_LOG_DIR)


    # start http server on the specified port
    start_http_server(http_port_number)

    # start timer to measure execution time
    start_time = time.time()
    # get telemetry from the switch through rest api
    sw_telemetry = get_sw_telemetry(sw_ipaddress, initiator_filename)
    # get http request status parser
    request_status_parser_now = get_request_status(sw_telemetry, initiator_filename)
    # create switch dashboard (set of toolbars which are set of gauges)
    dashboard = BrocadeDashboard(sw_telemetry, initiator_filename)

    if sw_telemetry.corrupted_request:
        while sw_telemetry.corrupted_request:
            # if any request is corrupted parser is not initialized
            brocade_parser_now = None
            # fill dashboard gauges with labels and metrics from the parser
            dashboard.fill_dashboard_gauge_metrics(brocade_parser_now, request_status_parser_now)   

            # wait timer to expire
            wait_timer(start_time)
            # start timer to measure execution time
            start_time = time.time()

            # save previous parsed request status
            request_status_parser_prev = copy.deepcopy(request_status_parser_now)
            # get telemetry from the switch through rest api
            sw_telemetry = get_sw_telemetry(sw_ipaddress, initiator_filename)
            # get http request status parser
            request_status_parser_now = get_request_status(sw_telemetry, initiator_filename, request_status_parser_prev)
            
    # parse retrieved telemetry to export to the dashboard
    brocade_parser_now = get_brocade_parser(sw_telemetry, initiator_filename)
    # update namserver with data from the parser if needed
    db.update_nameserver(brocade_parser_now.ch_parser)
    # fill dashboard gauges with labels and metrics from the parser
    dashboard.fill_dashboard_gauge_metrics(brocade_parser_now, request_status_parser_now)
    # stop timer
    wait_timer(start_time)
        
    # collect metrics in infinite loop
    while True:
        # reset timer
        start_time = time.time()
        # save previous parsed telemetry
        if not sw_telemetry.corrupted_request:
            brocade_parser_prev = copy.deepcopy(brocade_parser_now)
        # save previous parsed request status
        request_status_parser_prev = copy.deepcopy(request_status_parser_now)
        
        # collect new telemetry
        sw_telemetry = get_sw_telemetry(sw_ipaddress, initiator_filename)
        # get http request status parser
        request_status_parser_now = get_request_status(sw_telemetry, initiator_filename, request_status_parser_prev)
        # parse retrieved telemetry to export to the dashboard
        # if sw_telemetry is corrupted parser is not initialized
        brocade_parser_now = get_brocade_parser(sw_telemetry, initiator_filename, brocade_parser_prev)

        if brocade_parser_now:
            # update namserver with data from the parser if needed
            db.update_nameserver(brocade_parser_now.ch_parser)

        # fill dashboard gauges with labels and metrics from the parser
        dashboard.fill_dashboard_gauge_metrics(brocade_parser_now, request_status_parser_now)
        # wait timer to expire
        wait_timer(start_time)
    

def get_sw_telemetry(sw_ipaddress: ip_address, 
                    initiator_filename: str) -> Tuple[SwitchTelemetryRequest, RequestStatusParser]:
    """Method performs http request to retrieve switch telemetry. 
    Then request status for each module is extracted from switch telemetry .

    Args:
        sw_ipaddress (ip_address): switch ip address.
        initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).

    Returns:
        Union[SwitchTelemetryRequest, RequestStatusParser]: switch telemetry.
    """
    
    # get switch credentials from .env file
    sw_username, sw_password = get_credentials(sw_ipaddress)
    # get switch access protocol (http or https) from the configuration file
    secure_access = SWITCH_ACCESS[sw_ipaddress]["secure_access"]
    
    st = time.time()
    # collect new telemetry
    sw_telemetry = SwitchTelemetryRequest(sw_ipaddress, sw_username, sw_password, secure_access)
    elapsed_time = time.time() - st
    print('\nCollection time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    # save current switch telemetry to the database
    db.save_object(sw_telemetry, db.ARCHIVE_DIR, filename=initiator_filename + TELEMETRY_TAG)
    return sw_telemetry


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


def get_request_status(sw_telemetry: SwitchTelemetryRequest, 
                        initiator_filename: str, 
                        request_status_parser_prev: RequestStatusParser = None) -> RequestStatusParser:
    """Function creates request status summary for each module from the sw_telemetry.
    Saves request status summary to the database.

    Args:
        sw_telemetry (SwitchTelemetryRequest): set of switch telemetry retrieved from the switch.
        initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
        request_status_parser_prev (RequestStatusParser, optional): previous request_status_parser. Defaults to None.

    Returns:
        RequestStatusParser: request status module summary.
    """

    # load current nameserver from the database
    nameserver_dct = db.load_object(db.DATABASE_DIR, db.NS_FILENAME)
    # http request status parser
    request_status_parser_now = RequestStatusParser(sw_telemetry, nameserver_dct, request_status_parser_prev)
    # save current request status to the database
    db.save_object(request_status_parser_now, db.ARCHIVE_DIR, filename=initiator_filename + REQUEST_STATUS_TAG)
    return request_status_parser_now


def get_brocade_parser(sw_telemetry: SwitchTelemetryRequest, 
                        initiator_filename: str, 
                        brocade_parser_prev: BrocadeParser = None) -> BrocadeParser:
    """Function parse data for each sw_telemetry module and saves parser to the database.

    Args:
        sw_telemetry (SwitchTelemetryRequest): set of switch telemetry retrieved from the switch.
        initiator_filename (str): filename where collect_switch_metrics function is executed (switchname by default).
        brocade_parser_prev (BrocadeParser, optional): brocade parser from the previous not corrupted iteration. Defaults to None.

    Returns:
        BrocadeParser: brocade parser contains parsers for each module from the sw_telemetry.
    """

    # if any module of sw_telemetry is corrupted brocade_parser is not initialized
    if sw_telemetry.corrupted_request:
        return
    # parse retrieved telemetry to export to the dashboard
    brocade_parser_now = BrocadeParser(sw_telemetry, brocade_parser_prev)            
    # save current switch parser to the database
    db.save_object(brocade_parser_now, db.ARCHIVE_DIR, filename=initiator_filename + BROCADE_PARSER_TAG)
    return brocade_parser_now        


def wait_timer(start_time: time) -> None:
    """Function pause code execution and waits timer is expired.

    Args:
        start_time (time): start timer
    """

    # stop timer
    finish_time = time.time()
    duration = finish_time - start_time
    # wait till TIME_INTERVAL is expired
    if duration < TIME_INTERVAL:
        time.sleep(TIME_INTERVAL - duration)



