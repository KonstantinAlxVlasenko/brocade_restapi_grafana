from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeRequestStatusToolbar:
    """
    Class to create HTTP request status toolbar for each container.
    Toolbar is a set of prometheus gauges: rs_id, rs_code, rs_error, rs_date, rs_time.
    Each container is identifed by switch ip address, vf-id, module name, container name

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """


    rs_container_keys = ['ip-address', 'vf-id', 'module', 'container']
    rs_error_keys =  rs_container_keys + ['error-message']
    rs_date_keys  =  rs_container_keys + ['date']
    rs_time_keys   =   rs_container_keys + ['time']
    

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

        # request status_id gauge
        # 1 - 'Ok',  2 - 'Warnig', 3 - 'Fail'
        self._gauge_rs_id =  BrocadeGauge(name='request_status_id', description='HTTP request status ID', 
                                            label_keys=BrocadeRequestStatusToolbar.rs_container_keys, metric_key='status-id')
        # request status_code gauge
        # HTTP Status Code, 200-OK, 400-Bad Request etc
        self._gauge_rs_code =  BrocadeGauge(name='request_status_code', description='HTTP request status code', 
                                            label_keys=BrocadeRequestStatusToolbar.rs_container_keys, metric_key='status-code')
        # request status error message guage
        self._gauge_rs_error =  BrocadeGauge(name='request_status_error', description='HTTP request status error message', 
                                            label_keys=BrocadeRequestStatusToolbar.rs_error_keys)
        # request status date guage
        self._gauge_rs_date =  BrocadeGauge(name='request_status_date', description='HTTP request status date', 
                                            label_keys=BrocadeRequestStatusToolbar.rs_date_keys)
        # request status time guage
        self._gauge_rs_time =  BrocadeGauge(name='request_status_time', description='HTTP request status time', 
                                            label_keys=BrocadeRequestStatusToolbar.rs_time_keys)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def sw_telemetry(self):
        return self._sw_telemetry


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
