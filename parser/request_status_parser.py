from datetime import datetime
from typing import Dict, List, Union, Self

from collection.switch_telemetry_request import SwitchTelemetryRequest


class RequestStatusParser:
    """
    Class to create request status dictionaries for all http telemetry requests.


    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
        date: date sw_telemetry verification performed
        time: time sw_telemetry verification performed
        request_status: dictionary with request details for all http reqests in sw_telemetry
    """
    
    # dictionary with status ID for the corresponding status
    TELEMETRY_STATUS_ID = {'OK': 1,  
                           'WARNING': 2, 
                           'FAIL': 3}
    
    # errors which are considered to be OK status
    IGNORED_ERRORS = ['VF feature is not enabled', 
                      'No Rule violations found']
    
    
    def __init__(self, 
                 sw_telemetry: SwitchTelemetryRequest, 
                 nameserver_dct: dict,
                 request_status_parser_prev: Self = None) -> None:
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
            nameserver_dct (Dict[str, str]): dictionary key as ip address and chassis name as value.
        """
        
        self._sw_telemetry: SwitchTelemetryRequest = sw_telemetry
        self._nameserver: dict = nameserver_dct.copy()
        self._request_status_parser_prev = request_status_parser_prev
        self._date: datetime = datetime.now().strftime("%d/%m/%Y")
        self._time: datetime = datetime.now().strftime("%H:%M:%S")
        self._request_status: dict = self._get_request_status()

        if self.request_status_parser_prev:
            self._request_status_parser_prev._request_status_parser_prev = None

        

    def _get_request_status(self) -> List[Dict[str, Union[str, int]]]:
        """
        Method verifies telemetry request status for all http requests.
        
        Returns:
            List of dictionaries.
            Dictionary contains details which telemetry is retrieved, vf_id if applicable, 
            datetime request was performed and its status.
        """
        
        # list to store request status dictionaries
        request_status_lst = []
        
        # check request status for the telemetry with url wo vf_id
        for current_sw_telemetry, (module, container) in self.sw_telemetry._ch_unique_containers:
            request_status_lst.append(
                self._create_status_dct(current_sw_telemetry, module, container)
                )
                
        # check request status for the telemetry with url w vf_id        
        for current_sw_telemetry, (module, container) in self.sw_telemetry._vf_unique_containers:
            for vf_id, current_vf_telemetry in current_sw_telemetry.items():
                request_status_lst.append(
                    self._create_status_dct(current_vf_telemetry, module, container, vf_id)
                    )
        return request_status_lst
    
    
    def _create_status_dct(self,
                           telemetry_dct: Dict[str, Union[str, int]], 
                           module: str, container: str, 
                           vf_id=None) -> Dict[str, Union[str, int]]:
        """
        Method creates request status details dictionary of the request result telemetry_dct
        for the module and container name.
        
        Args:
            telemetry_dct: dictionary with request result
            module: requested module name
            container: requested container name
            vf_id: virtual ID used to perform telemetry reqest
            
        Returns:
            Request status dictionary for the request result telemetry_dct.
            Dictionary keys are module name, container name, retrieve datetime, status and vf_id.
        """
        
        ip_address = self.sw_telemetry.sw_ipaddress

        # retrive values from the telemetry_dct
        request_keys = ['date', 'time', 'status-code', 'error-message', 'vf-id']
        telemetry_status_dct = {key: telemetry_dct.get(key) for key in request_keys}
        # add module name, container name and vf_id
        telemetry_status_dct['vf-id'] = vf_id
        telemetry_status_dct['module'] = module
        telemetry_status_dct['container'] = container
        # verify request status
        status = RequestStatusParser._get_container_status(telemetry_dct)
        # add status and its id
        telemetry_status_dct['status'] = status
        telemetry_status_dct['status-id'] =  RequestStatusParser.TELEMETRY_STATUS_ID[status]
        telemetry_status_dct['ip-address'] = ip_address
        telemetry_status_dct['chassis-name'] = self.nameserver.get(ip_address)
        return telemetry_status_dct

    
    @staticmethod
    def _get_container_status(container: Dict[str, Union[str, int]]) -> str:
        """
        Method verifies request response, error-message and resonse status-code.
        
        Args:
            container: container with switch telemetry
            
        Returns:
            Response result status ('OK', 'WARNING', 'FAIL')
        """
    
        # if response contains non-empty data 
        if container.get('Response'):
            return 'OK'
        # if error-message is in the ignore list
        elif container.get('error-message') in RequestStatusParser.IGNORED_ERRORS:
            return 'OK'
        elif container.get('status-code'):
            if container['status-code'] in [401]: # Unauthorized access
                return 'FAIL'
            else:
                return 'WARNING'
        else:
            return 'FAIL'

        
    def __repr__(self):
        return (f"{self.__class__.__name__} " 
                f"ip_address: {self.sw_telemetry.sw_ipaddress}, "
                f"date: {self.telemetry_date if self.telemetry_date else 'None'}, "
                f"time: {self.telemetry_time if self.telemetry_time else 'None'}")
    

    @property
    def sw_telemetry(self):
        return self._sw_telemetry


    @property
    def nameserver(self):
        return self._nameserver


    @property
    def request_status_parser_prev(self):
        return self._request_status_parser_prev

    # @property
    # def ch_wwn(self):
    #     return self._ch_wwn
    
                
    @property
    def date(self):
        return self._date
    
    
    @property
    def time(self):
        return self._time  
    
    
    @property
    def request_status(self):
        return self._request_status  


    