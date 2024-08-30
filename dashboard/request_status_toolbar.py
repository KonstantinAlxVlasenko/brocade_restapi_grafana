from base_gauge import BaseGauge
from parser import RequestStatusParser
from switch_telemetry_request import SwitchTelemetryRequest


class RequestStatusToolbar:
    """
    Class to create HTTP request status toolbar for each container.
    Toolbar is a set of prometheus gauges: rs_id, rs_code, rs_error, rs_date, rs_time.
    Each container is identifed by switch ip address, vf-id, module name, container name

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """


    rs_container_keys = ['ip-address', 'vf-id', 'module', 'container']
    
    REQUEST_STATUS_ID = {1: 'OK',  2: 'Warnig', 3: 'Fail'}


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        self._sw_telemetry: SwitchTelemetryRequest = sw_telemetry

        # request status chassis name gauge
        self._gauge_rs_chname = BaseGauge(name='request_status_chassis_name', description='Chassis name corresponding to the IP address loaded from db',
                                          unit_keys=['ip-address'], parameter_key='chassis-name')
        # request status_id gauge
        # 1 - 'Ok',  2 - 'Warnig', 3 - 'Fail'
        rs_id_description = f'HTTP request status ID {RequestStatusToolbar.REQUEST_STATUS_ID}.'
        self._gauge_rs_id =  BaseGauge(name='request_status_id', description=rs_id_description,
                                          unit_keys=RequestStatusToolbar.rs_container_keys, metric_key='status-id')
        # request status_code gauge
        # HTTP Status Code, 200-OK, 400-Bad Request etc
        self._gauge_rs_code =  BaseGauge(name='request_status_code', description='HTTP request status code', 
                                            unit_keys=RequestStatusToolbar.rs_container_keys, metric_key='status-code')
        # request status error message guage
        self._gauge_rs_error =  BaseGauge(name='request_status_error', description='HTTP request status error message', 
                                            unit_keys=RequestStatusToolbar.rs_container_keys, parameter_key='error-message')
        # request status date guage
        self._gauge_rs_date =  BaseGauge(name='request_status_date', description='HTTP request status date', 
                                            unit_keys=RequestStatusToolbar.rs_container_keys, parameter_key='date')
        # request status time guage
        self._gauge_rs_time =  BaseGauge(name='request_status_time', description='HTTP request status time', 
                                            unit_keys=RequestStatusToolbar.rs_container_keys, parameter_key='time')



    def fill_toolbar_gauge_metrics(self, request_status_parser: RequestStatusParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            request_status (BrocadeRequestStatus): object contains required data to fill the gauge metrics.
        """

        gauge_lst = [self.gauge_rs_chname, self.gauge_rs_id, self.gauge_rs_code, 
                     self.gauge_rs_error, self.gauge_rs_date, self.gauge_rs_time]
        
        for gauge in gauge_lst:
            gauge.fill_chassis_gauge_metrics(request_status_parser.request_status)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def gauge_rs_chname(self):
        return self._gauge_rs_chname


    @property
    def gauge_rs_id(self):
        return self._gauge_rs_id
    

    @property
    def gauge_rs_code(self):
        return self._gauge_rs_code
    

    @property
    def gauge_rs_error(self):
        return self._gauge_rs_error


    @property
    def gauge_rs_date(self):
        return self._gauge_rs_date


    @property
    def gauge_rs_time(self):
        return self._gauge_rs_time
